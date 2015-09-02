#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


# import snap
from lib.coloring.coloring.ordering import color_by_ordering, \
     next_free_color, most_used_color, least_used_color


def max_deg(orig, g, trans, frat, col, silent=True):
    undir_g = g.undirected()
    degBuckets = {}
    degrees = {}  # Keep track of remaining degree
    maxdegree = 0
    for v in undir_g:
        d = undir_g.degree(v)
        if d not in degBuckets:
            degBuckets[d] = set()
        degBuckets[d].add(v)
        degrees[v] = d
        maxdegree = max(maxdegree, d)

    for d in xrange(0, maxdegree+1):
        if d not in degBuckets:
            degBuckets[d] = set()

    def vchoice(uncolored, coloring, graph):
        maxdeg = maxdegree
        while len(degBuckets[maxdeg]) == 0:
            maxdeg -= 1

        v = iter(degBuckets[maxdeg]).next()  # Just get any
        degBuckets[maxdeg].remove(v)

        # Update neighbours
        for w in graph.neighbours(v):
            if w not in degrees or w == v:
                continue  # Was already processed
            deg = degrees[w]
            degBuckets[deg].remove(w)
            degBuckets[deg-1].add(w)
            degrees[w] -= 1

        del degrees[v]
        return v

    return color_by_ordering(undir_g, vchoice, next_free_color)
