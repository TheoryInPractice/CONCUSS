#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import sys
from collections import deque
from lib.graph.graphformats import load_graph


# TODO:  Get a tighter lower bound on the treedepth
#        Could potentially use log of the length of
#        the longest path.  Also could replace function
#        with command line argument
def treedepth(G):
    """
    Return a lower bound on the treedepth of graph G
    """
    return 2

if __name__ == "__main__":
    G = load_graph(sys.argv[1])
    print treeDepth(G)
