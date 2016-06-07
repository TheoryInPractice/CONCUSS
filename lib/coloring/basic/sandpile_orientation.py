#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#



from lib.util.memorized import memorized
from collections import defaultdict
from lib.graph.graph import TFGraph


# Generate an acyclic low degree orientation,
# then improve by sandpiling.
def sandpile_orientation(g, weight=None):
    res = TFGraph(g.nodes)

    if len(res) == 0:
        return res

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

    while True:
        topple = []
        forbidden = set()
        for v in res:
            if v in forbidden:
                continue
            d = res.in_degree(v) + weight[v]
            cand = None
            candd = d-2
            for w, _ in res.in_neighbours(v):
                if w in forbidden:
                    continue
                if res.in_degree(w) + weight[w] <= candd:
                    cand = w
                    candd = res.in_degree(w)+weight[w]
            if cand is not None:
                topple.append((cand, v))

        if len(topple) == 0:
            break

        for v, w in topple:
            res.remove_arc(v, w)
            res.add_arc(w, v, 1)

    return res
# end def
