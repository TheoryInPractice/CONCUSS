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
def treedepth(G, pattern_type=None):
    """
    Return a lower bound on the treedepth of graph G
    """

    if pattern_type:
        return locals()[pattern_type](G)
    else:
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
    # TODO: Implement this
    pass


def path(pattern):
    """
    Compute the lower bound on treedepth of a path.

    :param pattern: the pattern
    :return: the treedepth
    """

    # Import math library
    import math
    # return lower bound
    return int(math.ceil(math.log(len(pattern) + 1, 2)))


def clique(pattern):
    """
    Compute the lower bound on treedepth of a clique.

    :param pattern: the pattern
    :return: the treedepth
    """

    # The treedepth of a clique is the number of nodes in it
    return len(pattern)


def biclique(pattern):
    """
    Compute the lower bound on treedepth of a biclique.

    :param pattern: the pattern
    :return: the treedepth
    """

    # The treedepth of a biclique is the number of nodes in it
    return len(pattern)


def cycle(pattern):
    """
    Compute the lower bound on treedepth of a cycle.

    :param pattern: the pattern
    :return: the treedepth
    """

    # TODO: Implement this
    pass

def grid(pattern):
    """
    Compute the lower bound on treedepth of a grid.

    :param pattern: the pattern
    :return: the treedepth
    """

    # TODO: Implement this
    pass

def quasi_clique(pattern):
    """
    Compute the lower bound on treedepth of a quasi_clique.

    :param pattern: the pattern
    :return: the treedepth
    """

    # TODO: Implement this
    pass

if __name__ == "__main__":
    G = load_graph(sys.argv[1])
    print treedepth(G)
