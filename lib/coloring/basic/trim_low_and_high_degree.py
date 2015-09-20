#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import math


def trim_low_and_high_degree(g):
    n = len(g)
    # Good threshold, at least for 4-centered colorings.
    thres = int(math.sqrt(math.sqrt(n)) + .5)*4

    zero_degree = []
    one_degree = []
    small_degree = []
    high_degree = []
    for v in g:
        deg = g.degree(v)
        if deg == 0:
            zero_degree.append(v)
        elif deg == 1:
            u = [i for i in g.neighbours(v)][0]
            if g.degree(u) > 1:
                one_degree.append(v)
            else:
                small_degree.append(v)
        elif deg < thres:
            small_degree.append(v)
        else:
            high_degree.append(v)
    #print ("    removed {} zero degree, {} one degree, and {} high degree"
    #       " vertices").format(len(zero_degree), len(one_degree),
    #        len(high_degree))
    gsmall = g.subgraph(small_degree)

    # postprocessing
    def restore_high_degree(coloring):
        #print ("    restored {} zero degree, {} one degree, and {} high degree"
        #       " vertices").format(len(zero_degree), len(one_degree), 
        #       len(high_degree))

        for v in zero_degree:
            coloring[v] = 0

        one_color = len(coloring)
        print "one_color", one_color

        for v in one_degree:
            coloring[v] = one_color

        for v in high_degree:
            coloring[v] = len(coloring)

        col_norm = coloring.normalize()
        #print set(col_norm[v] for v in one_degree)
        return col_norm

    return gsmall, restore_high_degree
