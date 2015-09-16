#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import sys
from lib.graph.graphformats import load_graph
from math import ceil, log
from lib.graph.pattern_generator import supported_patterns

# TODO:  Get a tighter lower bound on the treedepth
#        Could potentially use log of the length of
#        the longest path.  Also could replace function
#        with command line argument


def treedepth(G, pattern_info=None):
    """
    Return a lower bound on the treedepth of graph G
    """

    if pattern_info:
        # return known treedepth of pattern type
        try:
            pattern_name = pattern_info[0]
            num_vertices = pattern_info[1]
            return globals()[pattern_name](num_vertices)
        except KeyError:
            print "\nPattern '" + pattern_info[0] + "' is not supported."
            print "\nSupported patterns:\n"
            print "\n".join(supported_patterns.iterkeys())
            print
            sys.exit(1)
    else:
        # return the degeneracy as the lower bound, or 2,
        # whichever is larger
        return max(2, G.calc_degeneracy())


def star(num_vertices):
    """
    Compute the lower bound on treedepth of a star pattern.

    :param pattern: the pattern
    :return: the treedepth
    """

    # The treedepth of a star is always 2
    return 2


def wheel(num_vertices):
    """
    Compute the lower bound on treedepth of a wheel pattern.

    :param pattern: the pattern
    :return: the treedepth
    """

    return int(ceil(log(num_vertices - 1, 2))) + 2


def path(num_vertices):
    """
    Compute the lower bound on treedepth of a path.

    :param pattern: the pattern
    :return: the treedepth
    """

    # return lower bound
    return int(ceil(log(num_vertices + 1, 2)))


def clique(num_vertices):
    """
    Compute the lower bound on treedepth of a clique.

    :param pattern: the pattern
    :return: the treedepth
    """

    # The treedepth of a clique is the number of nodes in it
    return num_vertices


def cycle(num_vertices):
    """
    Compute the lower bound on treedepth of a cycle.

    :param pattern: the pattern
    :return: the treedepth
    """

    # return lower bound
    return int(ceil(log(num_vertices, 2))) + 1

def biclique(m):
    """
    Compute the lower bound on treedepth of a clique.

    :param m: size of smaller set
    :return: the treedepth
    """

    # The treedepth of a biclique is the number of nodes in
    # the smaller set + 1
    return m + 1


if __name__ == "__main__":
    G = load_graph(sys.argv[1])
    print treedepth(G)
