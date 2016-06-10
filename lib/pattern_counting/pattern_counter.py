#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import deque

from dp import KPattern, DPTable
from double_count import InclusionExclusion
from lib.util.misc import clear_output_line
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

    def __init__(self, G, multi, td_list, coloring, pattern_class=KPattern,
                 table_hints={}, decomp_class=CombinationsSweep,
                 combiner_class=InclusionExclusion, verbose=False,
                 big_component_file=None, tdd_file=None, dp_table_file=None,
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
        self.multi = multi
        self.coloring = coloring
        self.pattern_class = pattern_class
        self.verbose = verbose

        self.big_component_file = big_component_file
        self.big_component = None
        self.tdd_file = tdd_file
        self.dp_table_file = dp_table_file
        self.dp_table = None
        self.colset_count_file = colset_count_file

        self.combiners = [combiner_class(len(multi[idx]), coloring, table_hints, td=td_list[idx],
                                        execdata_file=colset_count_file) for idx in range(len(multi))]

        before_color_set_callbacks = [combiner.before_color_set for combiner in self.combiners]
        after_color_set_callbacks = [combiner.after_color_set for combiner in self.combiners]

        # TODO: calculate a lower bound on treedepth

        self.decomp_generator = decomp_class(G, coloring, len(max(multi, key=len)),
                                             min(td_list), len(min(multi, key=len)),
                                             before_color_set_callbacks,
                                             after_color_set_callbacks,
                                             self.verbose)

    def count_patterns_from_TDD(self, decomp, pat, idx):
        """
        Count the number of occurrences of our pattern in the given treedepth
        decomposition.

        Arguments:
            decomp:  Treedepth decomposition of a graph
            pat: The pattern that we are counting
            idx: The index of our pattern in the multi-pattern list
        """
        # Keep this table if the big component is the current component
        keep_table = (self.big_component is decomp)

        # Get a table object for this decomposition from the CountCombiner
        table = self.combiners[idx].table(decomp)

        # create a post order traversal ordering with a DFS to use in the DP
        ordering = []
        q = deque([decomp.root])
        # print decomp.root, len(decomp),
        # print [(i+1,self.coloring[i]) for i in decomp]
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
                for pattern in pattern_class.allPatterns(pat,
                                                         decomp.depth()):
                    # print "  Pattern:  ", pattern
                    computeLeaf(v, pattern, pat)
            # If the vertex is internal:
            else:
                # Get counts for tuples of its children (join case)
                for c_idx in range(2, len(decomp.children(v))+1):
                    leftChildren = tuple(decomp.children(v)[:c_idx])
                    for pattern in pattern_class.allPatterns(pat,
                                                             decomp.depth()):
                        # print "  Pattern:  ", pattern
                        computeInnerVertexSet(leftChildren, pattern, pat)
                    # Possibly clean up some unneeded data structures
                    computeInnerVertexSetCleanup(leftChildren, pat)
                # Combine child counts (forget case)
                for pattern in pattern_class.allPatterns(pat,
                                                         decomp.depth()):
                    computeInnerVertex(v, pattern, pat)

        # leaf = G.leaves().pop()
        # for pattern in patternClass.allPatterns(H, G.depth()):
        #     print G.isIsomorphism(leaf, pattern), pattern

        # Get the total count for the whole TDD
        trivialPattern = pattern_class(pat.nodes, None, pat)

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

        # Make a list to store counts of patterns specified
        final_count = [0]*len(self.multi)

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
            for idx, pat in enumerate(self.multi):
                count = self.count_patterns_from_TDD(tdd, pat, idx)
                # Combine the count from the TDD
                self.combiners[idx].combine_count(count)

        # Populate the list of counts that will be returned
        for idx in range(len(self.multi)):
            final_count[idx] += self.combiners[idx].get_count()

        # Write the largest component to a file
        if self.big_component_file is not None:
            from lib.graph.graphformats import write_edgelist
            write_edgelist(self.big_component, self.big_component_file)

        # Write the TDD of the largest component to a file
        if self.tdd_file is not None:
            for v in self.big_component.nodes:
                parent = self.big_component.vertexRecords[v].parent
                if parent is not None:
                    print >> self.tdd_file, v, parent

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
                        self.dp_table_file.write(
                            str(vString) + "; " + str(bString) + "\n")
                self.dp_table_file.write("}\n")

        # Return the totals for the whole graph
        return final_count
