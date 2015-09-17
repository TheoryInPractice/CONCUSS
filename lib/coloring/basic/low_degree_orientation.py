#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#



from lib.util.memorized import memorized
from lib.graph.graph import TFGraph
from collections import defaultdict


# Generate a low degree orientation of the graph additional
# the undirected fraternal edges
def low_degree_orientation(g, weight=None):
    res = TFGraph(g.nodes)

    if weight is None:
        weight = defaultdict( int )

    deglist = []
    buckets = []
    for v in g:
        d = g.degree(v) + weight[v]

        # Flexible  deglist[v] = d
        if v < len(deglist):
            deglist[v] = d
        else:
            deglist.extend([0 for x in range(len(deglist), v)])
            deglist.insert( v, d )

        # Flexible  buckets[d].add(v)
        if d < len(buckets):
            buckets[d].add(v)
        else:
            buckets.extend([set() for x in range(len(buckets), d)])
            buckets.insert(d,{v})

    seen = set()
    for i in xrange(0, len(g)):
        d = 0
        while len(buckets[d]) == 0:
            d += 1
        v = buckets[d].pop()

        for u in g.neighbours(v):
            if u in seen:
                continue
            d = deglist[u]
            buckets[d].remove(u)
            buckets[d-1].add(u)
            deglist[u] -= 1
            # Orient edges towards v
            res.add_arc(u, v, 1)

        seen.add(v)
    return res
# end def
