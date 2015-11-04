#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


from lib.coloring.coloring.ordering import color_by_ordering, \
     next_free_color, most_used_color, least_used_color


def dsatur(orig, g, trans, frat, col, silent=True):
    satdeg = {}
    ncols = {}
    for v in g:
        satdeg[v] = 0
        ncols[v] = set()

    def upd(v, coloring, colorstats, graph):
        vcol = coloring[v]
        for w in graph.neighbours(v):
            if w in ncols and vcol not in ncols[w]:
                ncols[w].add(vcol)
                satdeg[w] += 1

    def vchoice(uncolored, coloring, graph):
        # First choice: some max deg vertex
        if len(coloring) == 0:
            maxv = None
            maxdeg = -1
            for v in graph:
                d = graph.degree(v)
                if d > maxdeg:
                    maxdeg = d
                    maxv = v
            del satdeg[v]
            del ncols[v]
            return v
        # Now choose vertex that sees a maximum num of colors
        # Todo: us a priority queue here.
        res = maxsat = -1
        for v in satdeg:
            if satdeg[v] > maxsat:
                maxsat = satdeg[v]
                res = v

        del satdeg[res]
        del ncols[res]
        return res

    return color_by_ordering(g.undirected(), vchoice, next_free_color, upd)