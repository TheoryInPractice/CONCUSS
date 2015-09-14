#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import sys
from lib.graph.graphformats import load_graph
from math import ceil, log

# TODO:  Get a tighter lower bound on the treedepth
#        Could potentially use log of the length of
#        the longest path.  Also could replace function
#        with command line argument
def treedepth(G, pattern_type=None):
    """
    Return a lower bound on the treedepth of graph G
    """

    if pattern_type:
        # return known treedepth of pattern type
        try:
            return globals()[pattern_type](G)
        except KeyError:
            print "\nPattern type should be one of these:\n" \
                  "\nclique\ncycle\nwheel\nstar\npath\n"
            sys.exit(1)
    else:
        # return the degeneracy as the lower bound, or 2,
        # whichever is larger
        return max(2, G.calc_degeneracy())


def star(pattern):
    """
    Compute the lower bound on treedepth of a star pattern.

    :param pattern: the pattern
    :return: the treedepth
    """

    # The treedepth of a star is always 2
    return 2


def wheel(pattern):
    """
    Compute the lower bound on treedepth of a wheel pattern.

    :param pattern: the pattern
    :return: the treedepth
    """

    return int(ceil(log(len(pattern) - 1, 2))) + 2


def path(pattern):
    """
    Compute the lower bound on treedepth of a path.

    :param pattern: the pattern
    :return: the treedepth
    """

    # return lower bound
    return int(ceil(log(len(pattern) + 1, 2)))


def clique(pattern):
    """
    Compute the lower bound on treedepth of a clique.

    :param pattern: the pattern
    :return: the treedepth
    """

    # The treedepth of a clique is the number of nodes in it
    return len(pattern)


def cycle(pattern):
    """
    Compute the lower bound on treedepth of a cycle.

    :param pattern: the pattern
    :return: the treedepth
    """

    # return lower bound
    return int(ceil(log(len(pattern), 2))) + 1


if __name__ == "__main__":
    G = load_graph(sys.argv[1])
    print treedepth(G, "nishant")
