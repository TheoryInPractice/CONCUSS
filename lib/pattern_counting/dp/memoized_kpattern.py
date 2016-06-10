#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import itertools

from kpattern import KPattern
from lib.util.itertools_ext import xpowerset


class MemoizedKPattern(KPattern):
    allPatternLookup = {}
    separatorLookup = {}

    # def isSeparator(self):
    #       try:
    #               s = self.separatorLookup[self]
    #       except KeyError:
    #               s = kPattern.isSeparator(self)
    #               self.separatorLookup[self] = s
    #       return s

    @classmethod
    def allPatterns(cls, motif, k):
        """Return all k-patterns from a given vertex set"""
        # print [(i, len(j)) for i, j in cls.allPatternLookup.iteritems()]
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
            cls.allPatternLookup[(motif, k)] = patterns
        return iter(patterns)
