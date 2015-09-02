#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#



from lib.util.memorized import memorized
from lib.graph.graph import Coloring


def choose_color(colset):
    for c in range(0, len(colset)+1):
        if c not in colset:
            return c


# Generate a correct coloring and return a tuple
# (col[], numberOfColors)
#
@memorized(['g'])
def greedy_coloring(orig, g, trans, frat, col, silent=True):
    maxCol = 0

    g = g.undirected()

    for v in g:
        seenCols = set([col[w] for w in g.neighbours(v)])
        seenCols -= set([None])

        # assert col[v] == None
        col[v] = choose_color(seenCols)

        maxCol = max(col[v], maxCol)

    if not silent:
        print "max in-degree:", maxDeg
        print "number of colors:", maxCol

    # Sanity check
    for v in g:
        assert col[v] != None, "Vertex {0} is uncolored! \n {1}".format(
            v, col.color)

    return col
# end def
