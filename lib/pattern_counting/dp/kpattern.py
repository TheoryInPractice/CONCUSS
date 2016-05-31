#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from copy import copy
import itertools

from lib.util.itertools_ext import xpowerset


class KPattern(object):
    """
    k-patterns for computing dynamic programming
    """

    def __init__(self, vertices, boundary, graph):
        """
        Arguments:
            vertices: iterable of vertices
            boundary: dictionary injectively mapping vertices to unique
                integers
            graph: Graph of vertices with the potential to be in the k-pattern
        """
        if vertices is None:
            vertices = frozenset()
        self.vertices = frozenset(vertices)

        if boundary is None:
            boundary = {}

        self.graph = graph
        self.boundary = boundary
        self.boundaryVertices = frozenset(self.boundary.keys())
        # check if boundary is valid
        assert self.vertices >= self.boundaryVertices
        # generate hash value
        self.hashValue = self.__generateHashValue()

    def __eq__(self, other):
        """
        Test if two k-patterns are identical

        Argument:
            other:  k-pattern used for comparison
        """
        try:
            # vertex sets must be the same
            if self.vertices == other.vertices:
                # boundary vertices must be the same
                if self.boundaryVertices == other.boundaryVertices:
                    # return false if a boundary vertex does not map
                    # to the same integer in both patterns
                    for bv in self.boundaryVertices:
                        if self.boundary[bv] != other.boundary[bv]:
                            return False
                    # else return true
                    return True
            return False
        except:
            return False

    def __ne__(self, other):
        """
        Test if two k-patterns are distinct

        Argument:
            other:  k-pattern used for comparison
        """
        return not self == other

    def __cmp__(self, other):
        """
        Determine whether other is "before" this k-pattern

        For use in creating an ordered DP table printout.
        """
        # compare two sequences
        def compareSeq(x, y):
            if len(x) != len(y):
                if len(x) < len(y):
                    return -1
                else:
                    return 1
            for i, j in zip(x, y):
                if i < j:
                    return -1
                elif i > j:
                    return 1
            return 0

        # discriminate by boundary first
        boundaryCmp = compareSeq(sorted(self.boundary.items()),
                                 sorted(other.boundary.items()))
        if boundaryCmp == 0:
            # then discriminate by vertices
            vertexCmp = compareSeq(sorted(self.vertices),
                                   sorted(other.vertices))
            return vertexCmp
        else:
            return boundaryCmp

    def __hash__(self):
        """Define the hash value of a k-pattern for use in DP lookup tables"""
        return self.hashValue

    def __generateHashValue(self):
        v_hash = hash(self.vertices)
        b_hash = hash(frozenset(self.boundary.items()))
        return v_hash ^ b_hash

    def __str__(self):
        """Allow the pattern to be printed as a string"""
        vString = [str(v) for v in self.vertices]
        bString = [str(v) + " -> " + str(i) for v, i in
                   self.boundary.iteritems()]
        stringRep = "Boundary: " + str(bString) + "; Vertices: " \
                    + str(vString)
        return stringRep

    def inverseJoin(self, mem_motif=None):
        """Generator of all pattern pairs whose joins give this pattern"""
        # Create set of vertices not on the boundary
        nonBoundaryVertices = self.vertices - self.boundaryVertices

        # Iterate over all divisions of boundary vertices into 2 sets
        for v_list in xpowerset(nonBoundaryVertices):
            v_set = set(v_list)
            # print "Inverse join: " + str(v_set)
            pattern2 = self.__class__(v_set | self.boundaryVertices,
                                      self.boundary, self.graph)
            pattern3 = self.__class__(self.vertices-v_set, self.boundary,
                                      self.graph)
            if pattern2.isSeparator() and pattern3.isSeparator():
                yield (pattern2, pattern3)

    def inverseForget(self, i, mem_motif=None):
        """
        generator of all patterns that give this pattern when it
        forgets index i

        Arguments:
                i:  integer index to forget
        """
        if self.boundaryIndexLookup(i) is None:
            yield self
            nonBoundaryVertices = self.vertices - self.boundaryVertices
            for v in nonBoundaryVertices:
                b = copy(self.boundary)
                b[v] = i
                pattern2 = self.__class__(self.vertices, b, self.graph)
                yield pattern2

    def join(self, pattern2):
        """
        Join 2 patterns

        Arguments:
            pattern2:  kPattern to join with
        """
        assert self.boundary == pattern2.boundary
        assert self.vertices & pattern2.vertices == self.boundaryVertices
        joinedPattern = self.__class__(self.vertices | pattern2.vertices,
                                       self.boundary, self.graph)
        if joinedPattern.isSeparator():
            return joinedPattern
        else:
            raise ValueError("Pattern is not a separator")

    def allCompatible(self):
        """
        Generator of all patterns that are compatible for joining with this
        pattern
        """
        v_set = self.graph.nodes
        for otherVertices in xpowerset(v_set-self.vertices):
            pattern2 = self.__class__(set(otherVertices) |
                                      self.boundaryVertices, self.boundary,
                                      self.graph)
            if pattern2.isSeparator():
                yield pattern2

    def forget(self, i):
        """
        Forget an index

        Arguments:
                i:  integer index to forget
        """
        b = copy(self.boundary)
        try:
            del b[self.boundaryIndexLookup(i)]
        except KeyError:
            pass
        forgetPattern = self.__class__(self.vertices, b, self.graph)
        if forgetPattern.isSeparator():
            return forgetPattern
        else:
            raise ValueError("Pattern boundary is not a separator")

    def boundaryIndexLookup(self, i):
        """Return the vertex that maps to i"""
        for v in self.boundary.keys():
            if self.boundary[v] == i:
                return v
        return None  # TODO should this be an exception?

    def isSeparator(self):
        """
        Return whether the boundary of the pattern is a separator for the
        vertex set
        """
        nonBoundaryVertices = self.vertices - self.boundaryVertices
        for v in nonBoundaryVertices:
            for u in self.graph.neighbours(v):
                if u not in self.vertices:
                    return False
        return True

    def boundaryIter(self, pat):
        """Returns an iterator to the boundary items"""
        return self.boundary.iteritems()

    def boundaryVertexIter(self):
        """Return an iterator to the boundary vertices"""
        return self.boundaryVertices

    def numVertices(self):
        return len(self.vertices)

    @classmethod
    def allPatterns(cls, graph, k):
        """Return all k-patterns from a given vertex set"""
        # iterate over power set of vertices
        vertexSet = graph.nodes
        for v_set in xpowerset(vertexSet):
            # iterate over all possible boundary sizes
            for boundarySize in range(min([k, len(v_set)])+1):
                # iterate over all possible boundaries
                for boundary in itertools.combinations(v_set, boundarySize):
                    # iterate over all possible boundary mappings
                    for mapping in itertools.permutations(range(k),
                                                          boundarySize):
                        d = dict(zip(boundary, mapping))
                        kp = cls(v_set, d, graph)
                        if kp.isSeparator():
                            yield kp

    @classmethod
    def allLeafPatterns(cls, graph, k):
        """
        Return all k-patterns for which the boundary and the vertex set are the
        same
        """
        v_set = graph.vertices
        for boundarySize in range(min([k, len(v_set)])+1):
            # iterate over all possible boundaries
            for boundary in itertools.combinations(v_set, boundarySize):
                # iterate over all possible boundary mappings
                for mapping in itertools.permutations(range(k), boundarySize):
                    d = dict(zip(boundary, mapping))
                    yield cls(boundary, d, graph)
