#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import defaultdict, Counter
from itertools import product
from math import ceil, log

from lib.util.itertools_ext import choose
from dptable import DPTable


class BVColorDPTable(DPTable):
    """
    Dynamic programming table for computing graph isomorphisms.
    See http://arxiv.org/pdf/1406.2587v4.pdf for the algorithm
    and explanations of the table and pattern operations

    This DPTable subclass is similar to ColorDPTable in function, but
    stores table entries as bit vectors rather than dictionaries.  This
    allows us to change some of the DP methods which perform addition
    between two different dicts in time O(n) into a single addition,
    taking only O(1).  Also, storage overhead is often (somewhat
    surprisingly) reduced as a result of using ints instead of dicts.
    """

    def __init__(self, G, p, colors, reuse=True):
        """
        Arguments
                G: TDDecomposition object

        Optional arguments
                reuse: True to enable clearing/storing of dicts
                    used in table entries.
        """
        self.table = defaultdict(lambda: defaultdict(Counter))
        self.G = G
        # Size in bits of a field in the table's ints
        self.field_width = max(int(ceil(log(len(G)**p, 2))), 1)
        # Mask for picking out a single field
        self.mask = (1 << self.field_width) - 1
        # Mapping of colors to the bits that represent them
        self.colors = {val: 1 << i for i, val in enumerate(sorted(colors))}

        # If we got reuse=True, delete unused Counters to save space.
        self.reuse = reuse

    def computeLeaf(self, v, pattern1, mem_motif=None):
        """
        Compute table entry for a given leaf and k-pattern

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        patternSum = 0
        # Localize functions to speed up the loop
        self_isIsomorphism = self.isIsomorphism
        # Iterate through all patterns that become pattern1 when they forget
        # the depth of v.
        for pattern2 in pattern1.inverseForget(self.G.depth(v), mem_motif):
            patternSum += self_isIsomorphism(v, pattern2, mem_motif)
        # Update appropriate table entry
        self.table[(v,)][pattern1] = patternSum

    def computeInnerVertex(self, v, pattern1, mem_motif=None):
        """
        Compute table entry for a given single non-leaf and k-pattern

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        patternSum = 0
        # Localize functions to speed up the loop
        self_table = self.table
        ch_v = tuple(self.G.children(v))
        self_reuse = self.reuse
        # Iterate through all patterns that become pattern1 when they forget
        # the depth of v.
        for pattern2 in pattern1.inverseForget(self.G.depth(v), mem_motif):
            # patternSum += self.safeLookup(tuple(v.children), pattern2)
            pattern2_in_table = pattern2 in self_table[ch_v]
            if pattern2_in_table:
                patternSum += self_table[ch_v][pattern2]

            if self_reuse and pattern2_in_table:
                del self_table[ch_v][pattern2]
        # Update appropriate table entry
        self_table[(v,)][pattern1] = patternSum

    def computeInnerVertexSet(self, v_list, pattern1, mem_motif=None):
        """
        Compute table entry for a given set of vertices and k-pattern

        Arguments:
                v_list:  ordered iterable of Vertex
                pattern1:  kPattern
        """
        patternSum = 0
        # Split last vertex from the rest
        v_last = v_list[-1:]
        v_front = v_list[:-1]
        # Localize the table to speed up the loop
        self_table = self.table
        self_field_width = self.field_width
        self_mask = self.mask
        color_sets = range(1 << len(self.colors))
        tab_front = self_table[v_front]
        tab_last = self_table[v_last]
        # Iterate through all pattern pairs whose join yields pattern1.
        for pattern2, pattern3 in pattern1.inverseJoin(mem_motif):
            # patternSum += self.safeLookup(v_front, pattern2)* \
            #     self.safeLookup(v_last, pattern3)
            # Get the table entry [v_front][pattern2]
            e1 = tab_front[pattern2]
            # For each color set integer:
            for cs1 in color_sets:
                # If there's nothing left in the table entry, quit now
                if e1 == 0:
                    break
                # Otherwise, mask out the next count and shift e1 over
                val1 = e1 & self_mask
                e1 >>= self_field_width
                # If the value we got was 0, quit now since we would otherwise
                # waste our time adding 0's to the table
                if val1 == 0:
                    continue
                # Get the table entry [v_last][pattern3]
                e2 = tab_last[pattern3]
                # For each color set integer:
                for cs2 in color_sets:
                    # If there's nothing left in the second table entry, quit
                    if e2 == 0:
                        break
                    # Otherwise, mask out the next second count and shift e2
                    val2 = e2 & self_mask
                    e2 >>= self_field_width
                    # Add the product of the two counts to the right color set
                    patternSum += (val1 * val2) << (self_field_width * (cs1 |
                                                                        cs2))
        # Update appropriate table entry
        self_table[v_list][pattern1] = patternSum

    def computeInnerVertexSetCleanup(self, leftChildren, mem_motif=None):
        """Free counters after running computeInnerVertexSet"""
        if self.reuse:
            v_last = leftChildren[-1:]
            v_front = leftChildren[:-1]
            del self.table[v_last]
            del self.table[v_front]

    def isIsomorphism(self, v, pattern, mem_motif=None):
        """
        Determine whether the root path is an isomorphism to the boundary of
        the k-pattern

        Arguments:
                v:  vertex
                pattern:  kPattern
        Return value:
                True if the path from the root to v is isomorphic to the
                boundary of the k-pattern
        """
        # Throw away patterns that cannot have isomorphisms
        if (pattern.vertices != pattern.boundaryVertices or
                pattern.numVertices() > self.G.depth(v) + 1):
            return 0
        # if pattern.numVertices() <= 1:
        #     return True
        P_v = self.G.rootPath(v)

        # Create mapping of vertices of H to vertices of G
        HtoGMap = defaultdict(lambda: None)
        for u, idx in pattern.boundaryIter(mem_motif):
            try:
                HtoGMap[u] = P_v[idx]
            except IndexError:
                return 0
                # print pattern.vertices
                # print P_v
                # raise

        # Create mapping of vertices of G to vertices of H
        # NOTE: not used, so commented out
        # GtoHMap = dict(reversed(i) for i in HtoGMap.iteritems())

        # Ensure the neighborhoods of a vertex and its image are the same
        HinG = frozenset(HtoGMap.itervalues())
        for u in pattern.boundaryVertexIter():
            # Image of u in G
            u_prime = HtoGMap[u]
            # Images in G of the neighbors of u
            N_prime = set()
            for x in pattern.graph.adj[u]:
                N_prime.add(HtoGMap[x])
            N_prime.discard(None)
            if N_prime ^ (self.G.adj[u_prime] & HinG):
                return 0
        # Figure out what color set integer we need (where in the bit vector we
        # should be storing a 1
        colors = 0
        for c in (self.G.coloring.color[u] for u in HinG):
            colors += self.colors[c]
        # Return a 1 shifted into the right place in the bit vector
        return 1 << (self.field_width * colors)

        # for u1, u2 in itertools.combinations([v for v,
        #                                      i in pattern.boundaryIter()],
        #                                      2):
        #       neighborsInH = u1 in pattern.graph.adj[u2]
        #       neighborsInG = HtoGMap[u1] in self.adj[HtoGMap[u2]]
        #       if not neighborsInH == neighborsInG:
        #               return [False, frozenset()]
        # print HtoGMap
        # print frozenset([self.coloring.color[u]
        #                 for u in HtoGMap.itervalues()])
        # return (True, frozenset([self.coloring.color[u] for u in
        #        HtoGMap.itervalues()]))
