#!/usr/bin/env python2.7
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#

import sys
import os
import networkx as nx
import cProfile
import pstats
from networkx.algorithms import isomorphism
# In order to import CONCUSS modules, we will need to add CONCUSS to sys.path
sys.path.insert(0, os.getcwd().split('concuss')[0] + 'concuss')
from lib.run_pipeline import get_pattern_from_generator, is_basic_pattern
from lib.graph.graphformats import write_edgelist

# If we're running PyPy, make sure we can load networkx
if 'PyPy' in sys.version:
    sys.path.insert(1, '/usr/lib/python2.7/site-packages')


def readGraph(filename, type):
    extension = filename.split(".")[-1]
    print '"'+extension+'"'
    if extension == "txt":
        return nx.read_edgelist(filename, create_using=type)
    elif extension == "gml":
        return nx.read_gml(filename)
    elif extension == "leda":
        return nx.read_leda(filename, create_using=type)
    elif extension == "gexf":
        return nx.read_gexf(filename, create_using=type)
    elif extension == "graphml":
        return nx.read_graphml(filename, create_using=type)
    elif extension == "json":
        return nx.read_json(filename, create_using=type)
    else:
        raise Exception("File format .{0} not supported".format(extension))


def printProfileStats(name, profile, percent=1.0):
    """
    Prints out the function call statistics using the cProfile and
    pstats libraries

    Arguments:
        name:  string labelling the purpose of the statistics
        profile:  cProfile to print
        percent:  decimal proportion of list to print.  Default prints
                all (1.0)
    """
    sortby = 'time'
    restrictions = ""
    ps = pstats.Stats(profile).strip_dirs().sort_stats(sortby)
    print "Stats from {0}".format(name)
    ps.print_stats(restrictions, percent)

if __name__ == "__main__":
    G_file = sys.argv[1]
    H_name = sys.argv[2]

    # Check to see if we have a basic pattern
    if is_basic_pattern(H_name):
        H, _ = get_pattern_from_generator(H_name)
        with open(H_name + '.txt', 'w') as pattern_file:
            write_edgelist(H, pattern_file)
        H_file = H_name + '.txt'
    else:
        H_file = H_name

    directed = len(sys.argv) > 3

    if directed:
        graphType = nx.DiGraph
        matchType = isomorphism.DiGraphMatcher
    else:
        graphType = nx.Graph
        matchType = isomorphism.GraphMatcher

    readProfile = cProfile.Profile()
    readProfile.enable()
    G = readGraph(G_file, graphType())
    H = readGraph(H_file, graphType())
    readProfile.disable()
    printProfileStats("reading graphs", readProfile)

    patternProfile = cProfile.Profile()
    patternProfile.enable()
    matcher = matchType(G, H)
    patternCount = sum([1 for i in matcher.subgraph_isomorphisms_iter()])

    print "Number of occurrences of H in G: {0}".format(patternCount)

    # Delete the motif file created (if it exists)
    if os.path.isfile(H_name + '.txt'):
        os.remove(H_name + '.txt')

    patternProfile.disable()
    printProfileStats("counting patterns", patternProfile)
