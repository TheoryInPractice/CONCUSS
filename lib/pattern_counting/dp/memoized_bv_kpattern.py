#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import itertools
import math

from kpattern import KPattern
from bv_kpattern import BVKPattern
from lib.util.itertools_ext import xpowerset


class MemoizedBVKPattern(BVKPattern):
    """
    k-patterns for computing dynamic programming using integers

    Storage Format:
        vertices: bit vector.  The int ids of the vertices range from 0 to k-1
            and are determined by sorting the vertices
        boundaryVertices: same as vertices
        boundary: each value in the co-domain of the injective function (0 to
            k-1) has a log(k)+1 bit entry which is the id of the vertex that
            maps to this value, or all 1's if no vertex maps to this value.

    Arguments:
        vertices: iterable of vertices or int representation thereof (see
            above)
        boundary: dictionary injectively mapping vertices to unique integers or
            int representation thereof (see above)
    """

    allPatternLookup = {}
    separatorLookup = {}
    joinLookup = {}
    forgetLookup = {}
    boundaryIterLookup = {}

    def inverseJoin(self, mem_motif=None):
        """Return all pattern pairs whose joins give this pattern"""
        bd = self.boundary
        v = self.vertices
        if (bd, v, mem_motif) not in self.__class__.joinLookup:
            nonBoundaryVertices = self.vertices - self.boundaryVertices
            # Localize lookups for extra speed
            separatorLookup = self.__class__.separatorLookup
            bv = self.boundaryVertices
            g = self.graph
            self.__class__.joinLookup[(bd, v, mem_motif)] = []
            lu = self.__class__.joinLookup[(bd, v, mem_motif)]
            for v_set in range(2 ** self.k):
                # ensure the vertex set is a subset of the vertex set
                if v_set & v == v_set:
                    try:
                        pattern2 = separatorLookup[(v_set | bv, bd, g)]
                        pattern3 = separatorLookup[(v-v_set, bd, g)]
                        lu.append((pattern2, pattern3))
                    except KeyError:
                        pass
        return self.__class__.joinLookup[(bd, v, mem_motif)]

    def inverseForget(self, i, mem_motif=None):
        """
        Return all patterns that give this pattern when it forgets index i

        Arguments:
            i:  integer index to forget
        """
        v = self.vertices
        bd = self.boundary
        if (v, bd, i, mem_motif) not in self.__class__.forgetLookup:
            if self.boundaryIndexLookup(i) is None:
                # Localize lookups for extra speed
                nm = self.nullMask
                idbl = self.idBitLength
                separatorLookup = self.__class__.separatorLookup
                v = self.vertices
                g = self.graph
                bd = self.boundary
                self.__class__.forgetLookup[(v, bd, i, mem_motif)] = []
                lu = self.__class__.forgetLookup[(v, bd, i, mem_motif)]
                lu.append(self)

                nonBoundaryVertices = v - self.boundaryVertices
                # find vertices that can be promoted to the boundary
                for promotee in xrange(self.k):
                    if nonBoundaryVertices & (1 << promotee) > 0:
                        # remove null mask from entry to update
                        b = bd & ~(nm << i*idbl)
                        # add new entry to table
                        b = b | (promotee << i*idbl)
                        try:
                            pattern2 = separatorLookup[(v, b, g)]
                            lu.append(pattern2)
                        except KeyError:
                            pass
            else:
                return ()
        return self.__class__.forgetLookup[(v, bd, i, mem_motif)]

    def join(self, pattern2):
        """
        Join two k-patterns

        Arguments:
            pattern2:  kPattern to join with
        """
        assert self.boundary == pattern2.boundary
        assert self.vertices & pattern2.vertices == self.boundaryVertices
        try:
            joinedPattern = self.__class__.separatorLookup[(self.vertices |
                                                            pattern2.vertices,
                                                            self.boundary,
                                                            self.graph)]
            return joinedPattern
        except KeyError:
            raise ValueError("Pattern is not a separator")

    def allCompatible(self):
        """
        Generator of all patterns that can be created by joining with this
        pattern
        """
        allVertices = (2 ** self.k) - 1
        for otherVertices in range(allVertices):
            if otherVertices & self.vertices == self.boundary:
                try:
                    pattern = self.__class__.separatorLookup[(otherVertices,
                                                              self.boundary,
                                                              self.graph)]
                    yield pattern
                except KeyError:
                    pass

    def forget(self, i):
        """
        Forget an index

        Arguments:
            i:  integer index to forget
        """
        offsetNullMask = self.nullMask << i
        b = self.boundary & offsetNullMask
        try:
            forgetPattern = self.__class__.separatorLookup[(self.vertices,
                                                            b, self.graph)]
            return forgetPattern
        except KeyError:
            raise ValueError("Pattern boundary is not a separator")

    def boundaryIter(self, mem_motif=None):
        """Returns an iterator to the boundary items"""
        vt = self.vertices
        bd = self.boundary
        if (bd, vt, mem_motif) not in self.__class__.boundaryIterLookup:
            self.__class__.boundaryIterLookup[(bd, vt, mem_motif)] = []
            lookup = self.__class__.boundaryIterLookup[(bd, vt, mem_motif)]
            for i in range(self.k):
                entry = (bd >> i*self.idBitLength) & self.nullMask
                if entry != self.nullMask:
                    v = self.intMapping[entry]
                    lookup.append((v, i))
        return iter(self.__class__.boundaryIterLookup[(bd, vt, mem_motif)])

    @classmethod
    def allPatterns(cls, motif, k):
        """
        Return all k-patterns from a given vertex set
        """

        if (motif, k) in cls.allPatternLookup:
            patterns = cls.allPatternLookup[(motif, k)]
        else:
            patterns = []
            # iterate over power set of vertices
            vertexSet = motif.nodes
            for v_set in xpowerset(vertexSet):
                # iterate over all possible boundary sizes
                for boundarySize in range(min([k, len(v_set)])+1):
                    # iterate over all possible boundaries
                    for boundary in itertools.combinations(v_set,
                                                           boundarySize):
                        # iterate over all possible boundary mappings
                        for mapping in itertools.permutations(range(k),
                                                              boundarySize):
                            d = dict(zip(boundary, mapping))
                            kp = cls(v_set, d, motif)
                            if kp.isSeparator():
                                patterns.append(kp)
                                cls.separatorLookup[(kp.vertices, kp.boundary,
                                                     motif)] = kp
            cls.allPatternLookup[(motif, k)] = patterns
        return iter(patterns)
