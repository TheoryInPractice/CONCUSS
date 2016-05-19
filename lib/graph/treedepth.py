#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import sys
from math import ceil, log

from lib.graph.graphformats import load_graph
from lib.graph.pattern_generator import supported_patterns

# TODO:  Get a tighter lower bound on the treedepth
#        Could potentially use log of the length of
#        the longest path.  Also could replace function
#        with command line argument


def treedepth(G, *pattern_info):
    """
    Return a lower bound on the treedepth of graph G
    """

    if len(pattern_info):
        # return known treedepth
        try:
            # Extract the necessary pieces from pattern_info
            pattern_name = pattern_info[0]
            num_elem_tuple = pattern_info[1:]

            # Used for internal error checking
            if len(num_elem_tuple) == 0:
                raise IndexError

            return globals()[pattern_name](num_elem_tuple)
        except (KeyError, IndexError):
            print "\nPattern '" + pattern_info[0] + "' is not supported."
            print "\n\nor\n\nNumber of vertices in pattern have not been passed."
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

    :param num_vertices: Tuple containing number of elements
    :return: the treedepth
    """

    # The treedepth of a star is always 2
    return 2


def wheel(num_vertices):
    """
    Compute the lower bound on treedepth of a wheel pattern.

    :param num_vertices: Tuple containing number of elements
    :return: the treedepth
    """

    return int(ceil(log(num_vertices[0] - 1, 2))) + 2


def path(num_vertices):
    """
    Compute the lower bound on treedepth of a path.

    :param num_vertices: Tuple containing number of elements
    :return: the treedepth
    """

    # return lower bound
    return int(ceil(log(num_vertices[0] + 1, 2)))


def clique(num_vertices):
    """
    Compute the lower bound on treedepth of a clique.

    :param num_vertices: Tuple containing number of elements
    :return: the treedepth
    """

    # The treedepth of a clique is the number of nodes in it
    return num_vertices[0]


def cycle(num_vertices):
    """
    Compute the lower bound on treedepth of a cycle.

    :param num_vertices: Tuple containing number of elements
    :return: the treedepth
    """

    # return lower bound
    return int(ceil(log(num_vertices[0], 2))) + 1


def biclique(num_vertices):
    """
    Compute the lower bound on treedepth of a clique.

    :param num_vertices: 2-Tuple containing number of elements in
                         first and second set
    :return: the treedepth
    """

    # The treedepth of a biclique is the number of nodes in
    # the smaller set + 1
    return min(num_vertices[0], num_vertices[1]) + 1


if __name__ == "__main__":
    G = load_graph(sys.argv[1])
    print treedepth(G)
