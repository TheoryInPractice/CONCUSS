#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import math


def trim_high_degree(g):
    n = len(g)
    # Good threshold, at least for 4-centered colorings.
    thres = int(math.sqrt(math.sqrt(n)) + .5)*4

    zero_degree = []
    small_degree = []
    high_degree = []
    for v in g:
        deg = g.degree(v)
        if deg == 0:
            zero_degree.append(v)
        elif deg < thres:
            small_degree.append(v)
        else:
            high_degree.append(v)
    gsmall = g.subgraph(small_degree)

    # postprocessing
    def restore_high_degree(coloring):
        for v in zero_degree:
            coloring[v] = 0
        for v in high_degree:
            coloring[v] = len(coloring)+1
        return coloring.normalize()

    return gsmall, restore_high_degree
