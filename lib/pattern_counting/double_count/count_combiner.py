#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


from abc import ABCMeta, abstractmethod


class CountCombiner(object):
    """
    Abstract base class for all count combiners.

    Count combiners take the output from running dynamic programming on
    treedepth decompositions and combine them, however necessary, to get a
    single count.  The count combiner decides what table class it wants to
    use, as some of them are specialized in ways that need particular table
    classes (e.g. ColorCounts needs to use ColorDPTable).

    The count combiner also provides hooks for the DecompGenerator which
    are run before and after it makes TDDs of a common set of colors.
    These hooks are necessary for performing various bookkeeping in the
    count combiner; exactly what they do varies between classes.
    """
    __metaclass__ = ABCMeta

    def __init__(self, p, coloring, table_hints, td, execdata_file=None):
        """
        Common initialization needed by many CountCombiner subclasses

        Arguments:
            p: The size of the pattern graph
            coloring: The coloring of the host graph
            table_hints: Configuration options for the DPTable.  These
                may specify options such as what class is imported or
                details internal to a specific class.  They may also be
                ignored entirely by an implementation.
        """
        self.p = p
        self.coloring = coloring
        self.chi_p = len(coloring)
        self.table_hints = table_hints
        self.min_p = min(p, self.chi_p)
        self.execdata_file = execdata_file

    @abstractmethod
    def table(self, G):
        """Construct and return a DPTable for the given graph G"""
        pass

    def before_color_set(self, colors):
        """
        Hook run by the DecompGenerator before processing TDDs with a
        new set of colors.
        """
        pass

    @abstractmethod
    def combine_count(self, count):
        """Add the count returned from dynamic programming on one TDD"""
        pass

    def after_color_set(self, colors):
        """
        Hook run by the DecompGenerator after processing TDDs with a
        common set of colors.
        """
        pass


    @abstractmethod
    def get_count(self):
        """
        Return the total number of occurrences of the pattern seen

        This method is only guaranteed to return the correct result once
        all TDDs have been processed.  Before then, it is possible (and
        likely!) that the count will be wrong, not even correctly repres-
        enting the number of occurrences of the pattern seen in the TDDs
        that have been processed.
        """
        pass
