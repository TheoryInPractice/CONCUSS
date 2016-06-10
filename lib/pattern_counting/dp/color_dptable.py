#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import defaultdict, Counter
from itertools import product

from dptable import DPTable


class ColorDPTable(DPTable):
    """
    Dynamic programming table for computing graph isomorphisms.
    See http://arxiv.org/pdf/1406.2587v4.pdf for the algorithm
    and explanations of the table and pattern operations

    This DPTable subclass counts how many times the pattern was seen in each
    set of colors in the TDD.  This allows us to count patterns in fewer sub-
    graphs as we can get all the information we need about smaller sets of
    colors by looking at only the top level.

    Because this table keeps track of more information than the standard
    DPTable, it is not directly compatible.  The dynamic programming can
    be run the same way (and is - PatternCounter doesn't care which DPTable
    class is being used).  However, the table entries can not be used by
    InclusionExclusion, so ColorCounts must be used.  Since the CountCom-
    biner decides which DPTable it uses, there isn't a problem.
    """
    __counters = defaultdict(list)

    def __init__(self, G, reuse=True):
        """
        Arguments
                G: TDDecomposition object

        Optional arguments
                reuse: True to enable clearing/storing of dicts
                    used in table entries.
        """
        self.table = defaultdict(lambda: defaultdict(Counter))
        self.G = G
        self.reuse = reuse
        # If we got reuse=True, store unused Counters for reuse.
        if reuse:
            self.getCounter = ColorDPTable.__getCounter
            self.freeCounter = ColorDPTable.__freeCounter
        # Else, just make new counters and never get rid of old ones.
        else:
            self.getCounter = ColorDPTable.__getCounter
            self.freeCounter = lambda _, mem_motif: None

    @classmethod
    def __getCounter(cls, mem_motif, reuse=True):
        """Return an empty counter, either from the list or newly created"""
        if reuse and mem_motif in cls.__counters and cls.__counters[mem_motif]:
            return cls.__counters[mem_motif].pop()

        return Counter()

    @classmethod
    def __freeCounter(cls, counter, mem_motif):
        """Clear a counter and store it in a list for later reuse"""
        if counter:
            counter.clear()
            cls.__counters[mem_motif].append(counter)

    def computeLeaf(self, v, pattern1, mem_motif=None):
        """
        Compute table entry for a given leaf and k-pattern

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        patternSum = self.getCounter(mem_motif, self.reuse)
        # Localize functions to speed up the loop
        self_isIsomorphism = self.isIsomorphism
        patternSum_update = patternSum.update
        # Iterate through all patterns that become pattern1 when they forget
        # the depth of v.
        for pattern2 in pattern1.inverseForget(self.G.depth(v), mem_motif):
            patternSum_update(self_isIsomorphism(v, pattern2, mem_motif))
        # Update appropriate table entry
        self.table[(v,)][pattern1] = patternSum

    def computeInnerVertex(self, v, pattern1, mem_motif=None):
        """
        Compute table entry for a given single non-leaf and k-pattern

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        patternSum = self.getCounter(mem_motif, self.reuse)
        # Localize functions to speed up the loop
        self_table = self.table
        ch_v = tuple(self.G.children(v))
        DPTable_freeCounter = self.freeCounter
        patternSum_update = patternSum.update
        # Iterate through all patterns that become pattern1 when they forget
        # the depth of v.
        for pattern2 in pattern1.inverseForget(self.G.depth(v), mem_motif):
            # patternSum += self.safeLookup(tuple(v.children), pattern2)
            if pattern2 in self_table[ch_v]:
                patternSum_update(self_table[ch_v][pattern2])
                DPTable_freeCounter(self_table[ch_v][pattern2], mem_motif)
        # Update appropriate table entry
        self_table[(v,)][pattern1] = patternSum

    def computeInnerVertexSet(self, v_list, pattern1, mem_motif=None):
        """
        Compute table entry for a given set of vertices and k-pattern

        Arguments:
                v_list:  ordered iterable of Vertex
                pattern1:  kPattern
        """
        patternSum = self.getCounter(mem_motif, self.reuse)
        # Split last vertex from the rest
        v_last = v_list[-1:]
        v_front = v_list[:-1]
        # Localize the table to speed up the loop
        self_table = self.table
        # Iterate through all pattern pairs whose join yields pattern1.
        for pattern2, pattern3 in pattern1.inverseJoin(mem_motif):
            # patternSum += self.safeLookup(v_front, pattern2)*
            #                               self.safeLookup(v_last, pattern3)
            for pair in product(self_table[v_front][pattern2].iteritems(),
                                self_table[v_last][pattern3].iteritems()):
                patternSum[pair[0][0] | pair[1][0]] += pair[0][1] * pair[1][1]
        # Update appropriate table entry
        self_table[v_list][pattern1] = patternSum

    def computeInnerVertexSetCleanup(self, leftChildren, mem_motif=None):
        """Free counters after running computeInnerVertexSet"""
        v_last = leftChildren[-1:]
        v_front = leftChildren[:-1]
        motif_arg_last = [mem_motif]*len(self.table[v_last])
        motif_arg_front = [mem_motif]*len(self.table[v_front])
        freeCounter = self.freeCounter
        map(freeCounter, self.table[v_last].itervalues(), motif_arg_last)
        map(freeCounter, self.table[v_front].itervalues(), motif_arg_front)

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
            return {frozenset(): 0}
        # if pattern.numVertices() <= 1:
        #       return True
        P_v = self.G.rootPath(v)

        # Create mapping of vertices of H to vertices of G
        HtoGMap = defaultdict(lambda: None)
        for u, idx in pattern.boundaryIter(mem_motif):
            try:
                HtoGMap[u] = P_v[idx]
            except IndexError:
                return {frozenset(): 0}
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
                return {frozenset(): 0}
        return {frozenset([self.G.coloring.color[u] for u in HinG]): 1}

        # for u1, u2 in itertools.combinations([v for v,
        #                                       i in pattern.boundaryIter()],
        #                                       2):
        #       neighborsInH = u1 in pattern.graph.adj[u2]
        #       neighborsInG = HtoGMap[u1] in self.adj[HtoGMap[u2]]
        #       if not neighborsInH == neighborsInG:
        #               return [False, frozenset()]
        # print HtoGMap
        # print frozenset([self.coloring.color[u] for u in
        #                 HtoGMap.itervalues()])
        # return (True, frozenset([self.coloring.color[u] for u in
        #        HtoGMap.itervalues()]))
