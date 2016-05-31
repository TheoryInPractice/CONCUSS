#!/usr/bin/python2.7

#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import math

from kpattern import KPattern


class BVKPattern(KPattern):
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
    def __init__(self, vertices, boundary, graph):
        self.graph = graph
        self.k = len(self.graph)
        # number of bits needed to represent the number of vertices
        # plus a null value
        self.idBitLength = int(math.ceil(math.log(self.k+1, 2)))
        # bitmask for a null value (all 1's) of length idBitLength
        self.nullMask = (2 ** (self.idBitLength)) - 1
        # initialize bijection of vertices to integers
        self.intMapping = sorted(iter(self.graph))
        self.vertexMapping = []
        for (num, v) in enumerate(self.intMapping):
            self.vertexMapping.extend(
                [0 for x in range(len(self.vertexMapping), v + 1)])
            self.vertexMapping[v] = num

        # initialize boundary
        if vertices is None:
            vertices = 0
        try:  # if vertices are already a bitvector
            self.vertices = int(vertices)
        except TypeError:  # if vertices are in an iterable
            # initialize vertex bitmap
            self.vertices = 0
            for v in vertices:
                vIntId = 1 << self.vertexMapping[v]
                self.vertices |= vIntId

        # initialize boundary
        if boundary is None:
            boundary = (2 ** (self.k*self.idBitLength)) - 1
        try:  # if boundary is a compressed lookup
            self.boundary = int(boundary)
        except TypeError:  # boundary is iterable
            # initialize boundary to all 1's
            self.boundary = (2 ** (self.k*self.idBitLength)) - 1
            for v, i in boundary.iteritems():
                self.boundary &= (self.vertexMapping[v] <<
                                  i*self.idBitLength) | ~(self.nullMask <<
                                                          i*self.idBitLength)

        # intialize boundary vertices
        self.boundaryVertices = 0
        for i in range(self.k):
            entry = self.boundaryIndexLookup(i)
            # check if the entry is null
            if entry is not None:
                self.boundaryVertices |= (1 << entry)

        self.hashValue = self.__generateHashValue()
        """
        print vertices
        print self.vertices
        print boundary
        print self.boundary
        r = raw_input()
        """

    def __eq__(self, other):
        try:
            return (isinstance(other, BVKPattern) and
                    self.boundary == other.boundary and
                    self.vertices == other.vertices)
        except:
            return False

    def __cmp__(self, other):
        """
        Determine whether other is "before" this k-pattern

        For use in creating an ordered DP table printout.
        """
        # discriminate by boundary first
        boundaryCmp = cmp(self.boundary, other.boundary)
        if boundaryCmp == 0:
            # then discriminate by vertices
            vertexCmp = cmp(self.vertices, other.vertices)
            return vertexCmp
        else:
            return boundaryCmp

    def __generateHashValue(self):
        return hash((self.boundary, self.vertices))

    def __str__(self):
        """Allow the pattern to be printed as a string"""
        vString = []
        bString = []

        for i in range(self.k):
            vOffset = i
            bOffset = i*self.idBitLength
            v = self.intMapping[i]
            if (1 << vOffset) & self.vertices > 0:
                vString.append(str(v))

            bEntry = (self.boundary >> bOffset) & self.nullMask
            if bEntry != self.nullMask:
                try:
                    bString.append(str(self.intMapping[bEntry]) +
                                   " -> " + str(i))
                except IndexError:
                    print "Out of bounds is:", bEntry, self.nullMask
                    print self.intMapping
                    print self.vertexMapping
                    print self.boundary
                    print self.boundaryVertices
                    print self.vertices
                    raise

        stringRep = "Boundary: " + str(bString) + "; Vertices: " + str(vString)
        return stringRep

    def inverseJoin(self, mem_motif=None):
        """Generator of all pattern pairs whose joins give this pattern"""
        nonBoundaryVertices = self.vertices - self.boundaryVertices
        for v_set in range(2 ** self.k):
            # ensure the vertex set is a subset of the vertex set
            if v_set & self.vertices == v_set:
                pattern2 = self.__class__(v_set | self.boundaryVertices,
                                          self.boundary, self.graph)
                pattern3 = self.__class__(self.vertices-v_set, self.boundary,
                                          self.graph)
                if pattern2.isSeparator() and pattern3.isSeparator:
                    yield (pattern2, pattern3)

    def inverseForget(self, i, mem_motif=None):
        """
        Generator of all patterns that give this pattern when it forgets index
        i

        Arguments:
            i:  integer index to forget
        """
        if self.boundaryIndexLookup(i) is None:
            yield self
            nonBoundaryVertices = self.vertices - self.boundaryVertices
            # find vertices that can be promoted to the boundary
            for promotee in range(self.k):
                if nonBoundaryVertices & (1 << promotee) > 0:
                    # remove null mask from entry to update
                    b = self.boundary & ~(self.nullMask << i*self.idBitLength)
                    # add new entry to table
                    b = b | (promotee << i*self.idBitLength)
                    pattern2 = self.__class__(self.vertices, b, self.graph)
                    yield pattern2

    def join(self, pattern2):
        """
        Join two patterns

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
        Generator of all patterns that can be created by joining with this
        pattern
        """
        allVertices = (2 ** self.k) - 1
        for otherVertices in range(allVertices):
            if otherVertices & self.vertices == self.boundary:
                pattern2 = self.__class__(otherVertices, self.boundary,
                                          self.graph)
                if pattern2.isSeparator():
                    yield pattern2

    def forget(self, i):
        """
        Forget an index

        Arguments:
            i:  integer index to forget
        """
        offsetNullMask = self.nullMask << i
        b = self.boundary & offsetNullMask
        forgetPattern = self.__class__(self.vertices, b, self.graph)
        if forgetPattern.isSeparator():
            return forgetPattern
        else:
            raise ValueError("Pattern boundary is not a separator")

    def boundaryIndexLookup(self, i):
        """Return the vertex that maps to i"""
        entry = (self.boundary >> i*self.idBitLength) & self.nullMask
        if entry == self.nullMask:
            return None
        else:
            return entry

    def isSeparator(self):
        """
        Return whether the boundary of the pattern is a separator for the
        vertex set
        """
        nonBoundaryVertices = self.vertices - self.boundaryVertices
        for v, i in enumerate(self.vertexMapping):
            # check only the vertices part of the non-boundary
            if nonBoundaryVertices & (1 << i) > 0:
                # ensure each neighbor is in the pattern
                for u in self.graph.neighbours(v):
                    if (1 << self.vertexMapping[u]) & self.vertices == 0:
                        return False
        return True

    def boundaryIter(self, mem_motif=None):
        """Returns an iterator to the boundary items"""
        for i in range(self.k):
            entry = (self.boundary >> i*self.idBitLength) & self.nullMask
            if entry != self.nullMask:
                v = self.intMapping[entry]
                yield (v, i)

    def boundaryVertexIter(self):
        """Return an iterator to the boundary vertices"""
        # Iterate over all bits
        for i in xrange(self.k):
            # If we have a 1 bit, yield its position
            if self.boundaryVertices & 1 << i:
                yield i
            # If the rest of the boundaryVertices is 0, stop early
            if self.boundaryVertices >> i == 0:
                break

    def numVertices(self):
        # count = 0
        # for i in range(self.k):
        #        count += (self.vertices >> i) & 1
        # return count
        #  For some reason it's actually faster to turn self.vertices
        #  into a string representation of the number in binary, then
        #  count the 1's in that string.
        return bin(self.vertices).count('1')
