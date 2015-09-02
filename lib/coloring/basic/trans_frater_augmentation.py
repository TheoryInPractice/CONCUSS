#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#



from lib.util.memorized import memorized
from lib.graph.graph import Graph


# Calculate one transitive-fraternal-augmentation-step and
# result a tuple (newgraph, transedges, fratedges)
@memorized(['orig', 'step'])
def trans_frater_augmentation(orig, g, trans, frat, col,
                              nodes, step, td, ldoFunc):
    fratGraph = Graph()
    newTrans = {}

    for v in g:
        for x, y, _, in g.trans_trips(v):
            newTrans[(x, y)] = step
            assert (not g.adjacent(x, y)), \
                "{0} {1} transitive but adjacent".format(x, y)
        for x, y, _ in g.frat_trips(v):
            fratGraph.add_edge(x, y)
            assert (not g.adjacent(x, y)), \
                "{0} {1} fraternal but adjacent".format(x, y)

    for (s, t) in newTrans.keys():
        g.add_arc(s, t, 1)
        fratGraph.remove_edge(s, t)

    # TODO: support dict to see current in-degree...
    fratDigraph = ldoFunc(fratGraph)

    # calculate result
    trans.update(newTrans)

    for s, t, _ in fratDigraph.arcs():
        frat[(s, t)] = step
        g.add_arc(s, t, 1)

    return (g, trans, frat)
# end def
