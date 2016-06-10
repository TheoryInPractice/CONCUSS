#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from abc import ABCMeta, abstractmethod


class DecompGenerator(object):
    __metaclass__ = ABCMeta

    def prune(self, component, min_vertices):
        """
        Method to decide whether to prune a given component based on
        the given number of vertices

        :param component: The component we wish to check whether to
                prune
        :param min_vertices: The minimum number of vertices we expect in
                the component
        :return: True if to prune, False otherwise
        """
        return len(component) < min_vertices

    def __init__(self, G, coloring, p, td_H, multi_pat_min_p, before_color_set,
                 after_color_set, verbose=False):
        """Initialize this object"""
        self.G = G
        self.coloring = coloring
        self.p = p
        self.td_H = td_H
        self.multi_pat_min_p = multi_pat_min_p
        self.before_color_set = before_color_set
        self.after_color_set = after_color_set
        self.verbose = verbose

    @abstractmethod
    def __iter__(self):
        """
        An iterator for decompositions based on sizes of color sets we
        are looking at
        :return:
        """
        pass
