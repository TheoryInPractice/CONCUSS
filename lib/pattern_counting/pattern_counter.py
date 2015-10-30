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

    def __init__(self, G, multi, td_lower, coloring, pattern_class=KPattern, table_hints={},
                 decomp_class=CombinationsSweep,
                 combiner_class=InclusionExclusion, verbose=False):
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
        self.combiner = combiner_class(len(max(multi, key=len)), coloring, table_hints, td=td_lower)
        # TODO: calculate a lower bound on treedepth
        self.decomp_generator = decomp_class(G, coloring, len(max(multi, key=len)),
                                             self.combiner.tree_depth,
                                             [self.combiner.before_color_set],
                                             [self.combiner.after_color_set],
                                             self.verbose)

    def count_patterns_from_TDD(self, decomp, pat):
        """
        Count the number of occurrences of our pattern in the given treedepth
        decomposition.

        Arguments:
            decomp:  Treedepth decomposition of a graph
        """
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
                    computeInnerVertexSetCleanup(leftChildren)
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

        # print "Return value", retVal
        # print table

        return retVal

    def count_patterns(self):
        """Count the number of occurrences of our pattern in our host graph."""

        final_count = [0]*len(self.multi)
        # For every TDD given to us by the decomposition generator
        #tdd_store = [tdd for tdd in self.decomp_generator]

        # for idx, pat in enumerate(self.multi):
        #     print idx, str(pat)
        #     print idx, [e for e in pat.edges()]
        #
        # import sys
        # sys.exit(1)


        for tdd in self.decomp_generator:
            # Count patterns in that TDD
            for idx, pat in enumerate(self.multi):
                count = self.count_patterns_from_TDD(tdd, pat)
                # Combine the count from the TDD
                final_count[idx] += self.combiner.combine_count(count)
        # Return the total for the whole graph
        return final_count
