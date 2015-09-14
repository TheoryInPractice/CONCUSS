#!/usr/bin/env python2.7

#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

from lib.graph.graph import Graph
import sys

def get_generator(pattern_name):
    """
    Return a pattern generator method depending
    on the kind of pattern that needs to be
    generated

    :param pattern_name: Name of pattern
    :return: Callback to method that generates the pattern
    """

    if pattern_name == "clique":
        return clique
    elif pattern_name == "cycle":
        return cycle
    elif pattern_name == "path":
        return path
    elif pattern_name == "star":
        return star
    elif pattern_name == "wheel":
        return wheel
    else:
        print "\nPattern name should be one of these:\n" \
                  "\nclique\ncycle\nwheel\nstar\npath\n"
        sys.exit(1)


def clique(num_vertices):
    """
    Creates a clique of size num_vertices and
    returns a Graph object representing it

    :param num_vertices: The number of vertices in the clique
    :return: A Graph object representing clique

    """

    # Instantiate a Graph
    pattern = Graph()
    # Populate it
    for u in range(num_vertices):
        for v in range(u + 1, num_vertices):
            pattern.add_edge(u, v)
    # Return the clique
    return pattern


def cycle(num_vertices):
    """
    Creates a cycle of size num_vertices and
    returns a Graph object representing it

    :param num_vertices: The number of vertices in the cycle
    :return: A Graph object representing cycle

    """

    # Instantiate a Graph
    pattern = Graph()
    # Populate it
    for u in range(num_vertices):
        pattern.add_edge(u, (u + 1) % num_vertices)
    # Return the cycle
    return pattern


def path(num_vertices):
    """
    Creates a path of size num_vertices and
    returns a Graph object representing it

    :param num_vertices: The number of vertices in the path
    :return: A Graph object representing path

    """

    # Instantiate a Graph
    pattern = Graph()
    # Populate it
    for u in range(num_vertices - 1):
        pattern.add_edge(u, u + 1)
    # Return the path
    return pattern


def star(num_vertices):
    """
    Creates a star of size num_vertices and
    returns a Graph object representing it

    :param num_vertices: The number of vertices in the star
    :return: A Graph object representing star

    """

    # Instantiate a Graph
    pattern = Graph()
    # Populate it
    for v in range(num_vertices):
        if v != 0:
            pattern.add_edge(0, v)

    # Return the star
    return pattern


def wheel(num_vertices):
    """
    Creates a wheel of size num_vertices and
    returns a Graph object representing it

    :param num_vertices: The number of vertices in the wheel
    :return: A Graph object representing wheel

    """

    # Instantiate a cycle
    pattern = cycle(num_vertices - 1)
    # Populate it
    middle_vertex = num_vertices - 1
    for v in range(num_vertices - 1):
        pattern.add_edge(v, middle_vertex)

    # Return the wheel
    return pattern
