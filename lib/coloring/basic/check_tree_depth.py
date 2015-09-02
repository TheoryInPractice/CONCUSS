#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#



from lib.util.recordtype import *
from lib.util.memorized import memorized
from lib.util.misc import clear_output_line, percent_output
import copy
import sys


def number_of_combis(c, t):
    # return sum(i=1..t, binomial(c, i))

    res = 0

    for i in xrange(1, t+1):
        binom = 1

        for j in xrange(1, i+1):
            binom *= (c - i + j)
            binom /= j

        res += binom

    return res
# end def


CtdColor = recordtype('CtdColor', 'isInSet number nodes')

# bool isInSet: for each color, save whether the color is in the combination
# int  number:  store the frequency of each color
# set<int> nodes


CtdData = recordtype('CtdData', 'numColors treeDepth currentDepth combi ' +
                     'lastColor responsible color unionFind')

# int numColors:          number of all colors, whose frequency are at least 2
# int treeDepth:          the tree depth, which is checked
# int currentDepth:       current number of colors in the combination
# set<int> combi:         store the colors, which are in the combination,
#                             without the last color
# int lastColor:          store the last color, which is in the combination
# set<int>* responsible:  the set of vertices, which are responsible for the
#                             failure
# ctdColor* color
# map<set<int>, mint64*> unionFind


# union find structure:
# every vertex store information in one mint64
# every mint64 contains following bits:
# -----------------------------------------------
# |  type   | parent index ...                  |
# |  type   | color 0 | color 1 | ... | color 30|
# -----------------------------------------------
# |  0 |  1 |  2 |  3 |  4 |  5 | ... | 62 | 63 |
# -----------------------------------------------
#
# type can be
#      00 = the vertex will be ignored (the color is not in the combination)
#      01 = the vertex is a root in a connected component (color-bits are used)
#      10 = the vertex is a child (the parent-bits are used)
# color can be
#      00 = frequency is 0
#      01 = frequency is 1
#      10 = frequency is at least 2


UFS_TYPE_MASK = 0b11
UFS_TYPE_ROOT = 0b01
UFS_TYPE_CHILD = 0b10
UFS_COLOR_MASK = 0b11
UFS_COLOR_NULL = 0b00
UFS_COLOR_ONE = 0b01
UFS_COLOR_MORE = 0b10
UFS_LOW = 0x5555555555555554  # 0b010101..01010100
UFS_HIGH = 0xAAAAAAAAAAAAAAA8  # 0b101010..10101000

'''
def ufs_isChild(ufs, node):
    return ((ufs[node] & UFS_TYPE_MASK) == UFS_TYPE_CHILD)

def ufs_isRoot(ufs, node):
    return ((ufs[node] & UFS_TYPE_MASK) == UFS_TYPE_ROOT)

def ufs_getParent(ufs, node):
    return (ufs[node] >> 2)

def ufs_setParent(ufs, node, parent):
    ufs[node] = UFS_TYPE_CHILD | ((parent) << 2)

def ufs_setColor(ufs, node, color):
    ufs[node] = (ufs[node] & UFS_TYPE_MASK) | (color)

def ufs_makeSet(ufs, node, color):
    ufs[node] = UFS_TYPE_ROOT | (UFS_COLOR_ONE << ((color)*2))
'''


def ufs_find(ufs, node):
    save = node

    # (ufs_isChild(ufs, node)):
    while ((ufs[node] & UFS_TYPE_MASK) == UFS_TYPE_CHILD):
        # ufs_getParent(ufs, node)
        node = (ufs[node] >> 2)

    # (ufs_isChild(ufs, save)):
    if ((ufs[save] & UFS_TYPE_MASK) == UFS_TYPE_CHILD):
        # ufs_setParent(ufs, save, node)
        ufs[save] = UFS_TYPE_CHILD | ((node) << 2)

    # if not ufs_isRoot(ufs, node):
    #     print "AAAHHH"
    #     exit()

    return node
# end def


def check_graph_center(g, col, data):
    n = g.get_max_id()+1

    if (data.currentDepth == 1):
        ufs = [0] * n
        for v in data.color[data.lastColor].nodes:
            # ufs_makeSet(ufs, it, data.currentDepth)
            ufs[v] = UFS_TYPE_ROOT | (UFS_COLOR_ONE << ((data.currentDepth)*2))
    else:
        # ufs = copy.deepcopy(data.unionFind[data.currentDepth-2])
        ufs = copy.copy(data.unionFind[data.currentDepth-2])
        for v in data.color[data.lastColor].nodes:
            # ufs_makeSet(ufs, it, data.currentDepth)
            ufs[v] = UFS_TYPE_ROOT | (UFS_COLOR_ONE << ((data.currentDepth)*2))

            for u in g.neighbours(v):
                if data.color[col[u]].isInSet:
                    a = ufs_find(ufs, v)
                    b = ufs_find(ufs, u)

                    if (a != b):
                        ca = ufs[a]
                        cb = ufs[b]

                        # add the color frequency in both connected components
                        # for each color bits:
                        #   00 + 00  :=  00
                        #   00 + 01 = 01 + 00  :=  01
                        #   00 + 10 = 10 + 00 = 10 + 10  :=  10
                        nc = ((ca & UFS_LOW) + (cb & UFS_LOW)) | \
                             (ca & UFS_HIGH) | (cb & UFS_HIGH)
                        nc = (nc & UFS_HIGH) | (nc & (~((nc & UFS_HIGH) >> 1)))

                        # check whether the component dont have a center
                        if ((nc & UFS_LOW) == 0):
                            if data.responsible is not None:
                                # ufs_setParent(ufs, a, b)
                                ufs[a] = UFS_TYPE_CHILD | ((b) << 2)
                                # ufs_setColor(ufs, b, nc)
                                ufs[b] = (ufs[b] & UFS_TYPE_MASK) | (nc)

                                # search all vertices of this component
                                for i in xrange(0, n):
                                    if (ufs_find(ufs, i) == b):
                                        data.responsible.add(i)

                            return False
                        # end if

                        # ufs_setParent(ufs, a, b)
                        ufs[a] = UFS_TYPE_CHILD | ((b) << 2)
                        # ufs_setColor(ufs, b, nc)
                        ufs[b] = (ufs[b] & UFS_TYPE_MASK) | (nc)
                    # end if
                # end if
            # end for
        # end for
    # end else

    data.combi.add(data.lastColor)
    data.unionFind.append(ufs)

    return True
# end def


# @memorized(['orig', 'col', 'treeDepth'])
def check_tree_depth(orig, g, col, treeDepth, output=False):
    col = col.normalize()
    numColors = len(col)

    data = CtdData(
        responsible=set(),
        numColors=numColors,
        treeDepth=treeDepth,
        color=[],
        combi=set(),
        currentDepth=0,
        lastColor=0,
        unionFind=[]
    )

    for i in xrange(0, numColors):
        data.color.append(CtdColor(
            isInSet=False,
            number=0,
            nodes=set()
        ))
    # end for

    for v in g:
        data.color[col[v]].number += 1

    sub = sum(1 if num == 1 else 0 for c, num in col.frequencies().items())

    for v in g:
        data.color[col[v]].number += 1
        data.color[col[v]].nodes.add(v)

    if output:
        print "ignore colors:", sub

    # Colors with frequency one are the very last once. We ignore them
    # by iteration only over the remaining colors.
    data.numColors -= sub
    data.currentDepth = 0
    data.lastColor = -1

    result = True
    finished = False

    if data.numColors == 0:
        # Every vertex got its own color
        finished = True

    # only important for the output
    zzz = 0  # count combinations

    numbCombi = number_of_combis(data.numColors, data.treeDepth)

    while not finished:
        # insert the next color (lastColor+1) into the combination
        # 1, 4, 6 and lastcolor=8  ==>  1, 4, 6, 9
        data.lastColor += 1
        data.color[data.lastColor].isInSet = True
        data.currentDepth += 1

        # the lastColor is not inserted into the combi-set
        # check_graph_center does it

        zzz += 1
        if (output and (zzz % 100 == 0)):
            percent_output(zzz, numbCombi)

        if not check_graph_center(orig, col, data):
            # combination without a center
            if output:
                clear_output_line()
                sys.stdout.write("  combination: ")
                for it in data.combi:
                    sys.stdout.write(str(it))
                    sys.stdout.write(", ")
                sys.stdout.write(str(data.lastColor))
                sys.stdout.write("\n")

            result = False
            finished = True

        else:
            # if 'lastColor' is the maximal color  (2, 9 with 10 colors)
            # or the number of colors is 'treeDepth'
            #     (1, 4, 5, 6 with tree depth 4)
            if (data.lastColor == data.numColors-1) or \
               (data.currentDepth == data.treeDepth):

                again = True
                while again:
                    again = False

                    # delete the union find of the combination
                    del data.unionFind[data.currentDepth-1]

                    # erase the lastColor from the combination
                    # 1, 4, 6  ==>  1, 4  (in the next step  ==>  1, 4, 7)
                    data.combi.discard(data.lastColor)
                    data.color[data.lastColor].isInSet = False
                    data.currentDepth -= 1

                    # if 'lastColor' is the maximal color
                    #     (1, 4, 9 with 10 colors)
                    if (data.lastColor == data.numColors-1):
                        if not data.combi:
                            # the combination consisted only of the maximal
                            # color all combinations are checked
                            finished = True

                        else:
                            # set 'lastColor' to the highest colors in the
                            # combi-set and erase also this color from the
                            # combi-set 1, 4, 9  ==>  1, 4  ==>  1  (in the
                            # next step  ==>  1, 5)
                            data.lastColor = max(data.combi)
                            again = True
                # end while
            # end if
        # end if
    # end while

    if output:
        clear_output_line()
        print "number of combinations:", zzz

    return result, data.responsible
# end def
