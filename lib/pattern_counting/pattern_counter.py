#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


from collections import deque
from lib.util.misc import clear_output_line
from dp import KPattern, DPTable
from double_count import InclusionExclusion
from lib.decomposition import CombinationsSweep
from lib.graph.treedepth import treedepth


class PatternCounter(object):
    """
    Run the decompose, count, and combine parts of the pipeline

    The PatternCounter is responsible for creating a CountCombiner and a
    DecompGenerator, then running the DecompGenerator, getting DPTable
    objects from the CountCombiner for the decompositions, and returning
    the final count from the whole graph.
    """

    def __init__(self, G, H, td_lower, coloring, pattern_class=KPattern,
                 table_hints={}, decomp_class=CombinationsSweep,
                 combiner_class=InclusionExclusion, verbose=False,
                 big_component_file=None, dp_table_file=None,
                 colset_count_file=None):
        """
        Create the CountCombiner and DecompGenerator objects

        Arguments:
            G: Host graph
            H: Pattern graph
            coloring: A (|H|+1)-centered coloring of G
            pattern_class: The k-pattern class to use in dynamic programming
            table_hints: probably-respected options for the DP table
            decomp_class: DecompGenerator subclass
            combiner_class: CountCombiner subclass
            verbose: whether or not to print debugging information
        """
        self.G = G
        self.H = H
        self.coloring = coloring
        self.pattern_class = pattern_class
        self.verbose = verbose

        self.big_component_file = big_component_file
        self.big_component = None
        self.dp_table_file = dp_table_file
        self.dp_table = None
        self.colset_count_file = colset_count_file

        self.combiner = combiner_class(len(H), coloring, table_hints,
                                       td=td_lower,
                                       execdata_file=colset_count_file)
        # TODO: calculate a lower bound on treedepth
        self.decomp_generator = decomp_class(G, coloring, len(H),
                                             self.combiner.tree_depth,
                                             [self.combiner.before_color_set],
                                             [self.combiner.after_color_set],
                                             self.verbose)

    def count_patterns_from_TDD(self, decomp):
        """
        Count the number of occurrences of our pattern in the given treedepth
        decomposition.

        Arguments:
            decomp:  Treedepth decomposition of a graph
        """
        # Keep this table if the big component is the current component
        keep_table = (self.big_component is decomp)

        # Get a table object for this decomposition from the CountCombiner
        table = self.combiner.table(decomp)

        # create a post order traversal ordering with a DFS to use in the DP
        ordering = []
        q = deque([decomp.root])
        #print decomp.root, len(decomp), [(i+1,self.coloring[i]) for i in decomp]
        while q:
            curr = q.pop()
            ordering.append(curr)
            if not decomp.hasLeaf(curr):
                q.extend(reversed(decomp.children(curr)))
        ordering.reverse()

        # Perform dynamic programming on the treedepth decomposition in the
        # post order traversal
        computeLeaf = table.computeLeaf
        computeInnerVertexSet = table.computeInnerVertexSet
        computeInnerVertexSetCleanup = table.computeInnerVertexSetCleanup
        computeInnerVertex = table.computeInnerVertex
        pattern_class = self.pattern_class
        # For each vertex in the TDD:
        for v in ordering:
            # If the vertex is a leaf
            if decomp.hasLeaf(v):
                for pattern in pattern_class.allPatterns(self.H,
                                                         decomp.depth()):
                    # print "  Pattern:  ", pattern
                    computeLeaf(v, pattern)
            # If the vertex is internal:
            else:
                # Get counts for tuples of its children (join case)
                for c_idx in range(2, len(decomp.children(v))+1):
                    leftChildren = tuple(decomp.children(v)[:c_idx])
                    for pattern in pattern_class.allPatterns(self.H,
                                                             decomp.depth()):
                        # print "  Pattern:  ", pattern
                        computeInnerVertexSet(leftChildren, pattern)
                    # Possibly clean up some unneeded data structures
                    computeInnerVertexSetCleanup(leftChildren)
                # Combine child counts (forget case)
                for pattern in pattern_class.allPatterns(self.H,
                                                         decomp.depth()):
                    computeInnerVertex(v, pattern)

        # leaf = G.leaves().pop()
        # for pattern in patternClass.allPatterns(H, G.depth()):
        #     print G.isIsomorphism(leaf, pattern), pattern

        # Get the total count for the whole TDD
        trivialPattern = pattern_class(self.H.nodes, None, self.H)

        retVal = table.lookup((decomp.root,), trivialPattern)
        # if retVal > 0:
        #     print "Return value", retVal
        #     print table

        # Keep the table if this tdd is the big component
        if keep_table:
            self.dp_table = table

        return retVal

    def count_patterns(self):
        """Count the number of occurrences of our pattern in our host graph."""
        # For every TDD given to us by the decomposition generator
        for tdd in self.decomp_generator:
            # Remember the largest component we've seen if we're making
            # visualization output
            if self.big_component_file is not None:
                if self.big_component is None:
                    self.big_component = tdd
                elif len(self.big_component) < len(tdd):
                    self.big_component = tdd
            # Count patterns in that TDD
            count = self.count_patterns_from_TDD(tdd)
            # Combine the count from the TDD
            self.combiner.combine_count(count)

        # Write the largest component to a file
        if self.big_component_file is not None:
            from lib.graph.graphformats import write_edgelist
            write_edgelist(self.big_component, self.big_component_file)

        # Write the DP table for the largest component to a file
        if self.dp_table_file is not None:
            # Write the table in a machine-readable format
            dp_table = self.dp_table.table
            for v_tup in sorted(dp_table.keys()):
                self.dp_table_file.write(str([v for v in v_tup]) + " {\n")
                for pattern, count in sorted(dp_table[v_tup].iteritems()):
                    if count > 0:
                        self.dp_table_file.write("\t" + str(count) + "; ")
                        vString = [v for v in pattern.vertices]
                        bString = [str(v) + ":" + str(i) for v, i in
                                   pattern.boundary.iteritems()]
                        bString = '[' + ', '.join(bString) + ']'
                        self.dp_table_file.write(str(vString) + "; " + str(bString) + "\n")
                self.dp_table_file.write("}\n")

        # Return the total for the whole graph
        return self.combiner.get_count()
