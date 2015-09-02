#!/usr/bin/env python2.7
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

import sys
import networkx as nx
from networkx.algorithms import isomorphism
import cProfile
import pstats
from lib.run_pipeline import printProfileStats
# If we're running PyPy, make sure we can load networkx
if 'PyPy' in sys.version:
    sys.path.insert(0, '/usr/lib/python2.7/site-packages')


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

if __name__ == "__main__":
    G_file = sys.argv[1]
    H_file = sys.argv[2]
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
    patternProfile.disable()
    printProfileStats("counting patterns", patternProfile)
