#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#



from lib.util.memorized import memorized
import sys
import copy
import random


# @memorized(['g', 'trans', 'frat', 'col', 'i'])
def optimization_interval(orig, g, trans, frat, col, i, treeDepth, mobj):
    # print "  remove transitive and fraternal edges"

    # remove all transitive and fraternal edges of the last step
    edges = {}
    optcols = copy.deepcopy(col)  # avoid side effects
    col = copy.deepcopy(col)      # avoid side effects

    for (s, t) in trans.keys():
        step = trans[(s, t)]
        if (step == i):
            g.remove_arc(s, t)
            edges[(s, t)] = (True, trans[(s, t)])
            del trans[(s, t)]

    for (s, t) in frat.keys():
        step = frat[(s, t)]
        if (step == i):
            g.remove_arc(s, t)
            edges[(s, t)] = (False, frat[(s, t)])
            del frat[(s, t)]

    numbAdded = 0
    numbAdd = len(edges) / 2
    attempts = 0
    resColors = 0
    MAX_ATTEMPTS = 2

    while True:
        mod = len(edges)
        ra = numbAdd
        addedEdges = {}

        for (s, t) in edges.keys():
            isTrans, value = edges[(s, t)]

            # add randomly 'numbAdd' edges from the list 'restEdges'
            rand = random.randint(0, mod-1)

            if (rand < ra):
                g.add_arc(s, t, 0)

                if isTrans:
                    trans[(s, t)] = value
                else:
                    frat[(s, t)] = value

                addedEdges[(s, t)] = isTrans
                del edges[(s, t)]

                ra -= 1
                if (ra == 0):
                    break

            mod -= 1
        # end for

        # sys.stdout.write("  check with " + str(numbAdded+numbAdd) + " edges")

        newcol = mobj.col(orig, g, trans, frat, col)
        correct, nodes = mobj.ctd(orig, g, newcol, treeDepth)

        # sys.stdout.write(" -> " + str(correct))

        if correct:
            if len(newcol) < len(optcols):
                optcols = copy.deepcopy(newcol)
            numColors = len(newcol)
            # sys.stdout.write(", colors: " + str(numColors) + '\n')
        # else:
            # sys.stdout.write('\n')

        attempts += 1

        if (correct or (attempts < MAX_ATTEMPTS)):
            for ((s, t), isTrans) in addedEdges.iteritems():
                if isTrans:
                    edges[(s, t)] = (True, trans[(s, t)])
                    del trans[(s, t)]
                else:
                    edges[(s, t)] = (False, frat[(s, t)])
                    del frat[(s, t)]

                g.remove_arc(s, t)
            # end for
        else:
            numbAdded += numbAdd

        if (correct or (attempts == MAX_ATTEMPTS)):
            attempts = 0
            numbAdd = numbAdd / 2

        if (numbAdd == 0):
            break

    # end while
    return optcols
# end def
