#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from dptable import DPTable


class ForwardDPTable(DPTable):
    def __init__(self, G):
        super(ForwardDPTable, self).__init__(G)

    def computeLeaf(self, v, pattern1, mem_motif=None):
        """
        Compute contributions of a given k-pattern to the DP
        table for a given leaf

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        # find the pattern when forgetting the depth of v
        try:
            pattern2 = pattern1.forget(self.G.depth(v))
        # might not be separator
        except ValueError:
            pass
        else:
            isomorphismCount = self.isIsomorphism(v, pattern1)
            # update appropriate table entry
            self.table[(v,)][pattern2] += isomorphismCount

    def computeInnerVertex(self, v, pattern1, mem_motif=None):
        """
        Compute contributions of a given k-pattern to a single non-leaf

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        # find the pattern when forgetting the depth of v
        try:
            pattern2 = pattern1.forget(self.G.depth(v))
        # might not be separator
        except ValueError:
            pass
        else:
            # update appropriate table entry
            self.table[(v,)][pattern2] += self.lookup(
                tuple(self.G.children(v)), pattern1)

    def computeInnerVertexSet(self, v_list, pattern1, mem_motif=None):
        """
        Compute table entry for a given set of vertices and k-pattern

        Arguments:
                v_list:  ordered iterable of Vertex
                pattern1:  kPattern
        """

        # split last vertex from the rest
        v_last = v_list[-1],
        v_front = tuple(v_list[:-1])
        # iterate through all patterns that can be formed by a
        # join with pattern1
        for pattern2 in pattern1.allCompatible():
            joinedPattern = pattern1.join(pattern2)
            # update appropriate table entry
            self.table[tuple(v_list)][joinedPattern] += self.lookup(
                v_front, pattern1)*self.lookup(v_last, pattern2)
