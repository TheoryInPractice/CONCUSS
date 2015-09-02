#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#



from lib.util.memorized import memorized
import collections
from lib.graph.graph import TFGraph


# Generate a low degree orientation of the graph additional
# the undirected fraternal edges
def low_degree_orientation(g, weight=None):
    res = TFGraph(g.nodes)

    if weight is None:
        weight = collections.defaultdict(int)

    degdict = {}
    buckets = collections.defaultdict(set)
    for v in g:
        d = g.degree(v) + weight[v]
        degdict[v] = d
        buckets[d].add(v)

    seen = set()
    for i in xrange(0, len(g)):
        d = 0
        while len(buckets[d]) == 0:
            d += 1
        v = iter(buckets[d]).next()
        buckets[d].remove(v)

        for u in g.neighbours(v):
            if u in seen:
                continue
            d = degdict[u]
            buckets[d].remove(u)
            buckets[d-1].add(u)
            degdict[u] -= 1
            # Orient edges towards v
            res.add_arc(u, v, 1)

        seen.add(v)
    return res
# end def
