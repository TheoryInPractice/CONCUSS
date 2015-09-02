#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


from lib.util.memorized import memorized
from lib.util.priority_dictionary import priorityDictionary as \
     priorityDictionary
from lib.graph.graph import Coloring as Coloring
import sys


def next_free_color(neighCols, usedCols):
    for c in xrange(0, len(neighCols)+1):
        if c not in neighCols:
            return c


def color_freq(vertices, coloring):
    res = priorityDictionary()
    for v in vertices:
        c = coloring[v]
        if c not in res:
            res[c] = 0
        res[c] += 1
    return res


def most_used_color(neighCols, usedCols):
    candidate = -1
    frequency = sys.maxint
    for c in usedCols:
        if c in neighCols:
            continue
        if usedCols[c] < frequency:
            frequency = usedCols[c]
            candidate = c

    # Fallback
    if candidate == -1:
        return next_free_color(neighCols, usedCols)
    return candidate


def least_used_color(neighCols, usedCols):
    candidate = -1
    frequency = 0
    for c in usedCols:
        if c in neighCols:
            continue
        if usedCols[c] > frequency:
            frequency = usedCols[c]
            candidate = c

    # Fallback
    if candidate == -1:
        return next_free_color(neighCols, usedCols)
    return candidate


def color_by_ordering(graph, vchoice, cchoice, upd=None):
    cols = Coloring()
    n = len(graph)
    usedCols = priorityDictionary()
    uncolored = set(graph.nodes)

    while len(uncolored) > 0:
        v = vchoice(uncolored, cols, graph)
        neighbourCols = {}
        for w in graph.neighbours(v):
            if w in cols:
                if cols[w] not in neighbourCols:
                    neighbourCols[cols[w]] = 0
                neighbourCols[cols[w]] += 1
        cols[v] = cchoice(neighbourCols, usedCols)
        if cols[v] not in usedCols:
            usedCols[cols[v]] = 0
        usedCols[cols[v]] += 1
        uncolored.remove(v)
        if upd:
            upd(v, cols, usedCols, graph)

    return cols
