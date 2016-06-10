#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from count_combiner import CountCombiner
from lib.util.itertools_ext import choose


class InclusionExclusion(CountCombiner):
    """
    An inclusion-exclusion-based count combiner implementation

    For inclusion/exclusion, we count patterns in subgraphs with fewer than p
    colors and adjust our total based on the number of patterns counted in
    those smaller sets of colors.
    """

    def __init__(self, p, coloring, table_hints, td, execdata_file=None):
        """
        Set up inclusion-exclusion-specific variables

        Most of this method serves to build the __in_ex list, which holds
        coefficients for the counts from particular sizes of sets of colors.
        The totals returned from dynamic programming are multiplied by these
        coefficients before they are added into our final count.
        """
        super(InclusionExclusion, self).__init__(p, coloring, table_hints, td,
                                                 execdata_file)
        self.pattern_count = 0
        self.tree_depth = td
        self.__in_ex = []
        # This causes us to throw an exception if we somehow don't call
        # before_color_set before combine_count.  We'd be getting the wrong
        # count anyway, so it's better to fail early.
        self.n_colors = None

        # Field that stores count for current color set
        self.current_color_set_count = 0

        # Iterate over all sizes of colors
        for n_colors in range(self.min_p, min(self.tree_depth, self.min_p)-1,
                              -1):
            # For inclusion/exclusion principle, we either need to add or
            # subtract the count for a specific set of colors in order to avoid
            # double counting. We count the number of times a color combination
            # of size numColors was counted in the color combinations of size
            # greater than numColors and adjust our count accordingly.
            discrepancy = self.min_p - n_colors
            remaining_colors = self.chi_p - n_colors
            in_ex_modifier = 1 - sum([choose(remaining_colors, discrepancy-i) *
                                      mod for i, mod in
                                      enumerate(self.__in_ex)])
            self.__in_ex.append(in_ex_modifier)

        # Get the appropriate DPTable class
        if table_hints['forward']:
            from lib.pattern_counting.dp import ForwardDPTable
            self.table_type = ForwardDPTable
        else:
            from lib.pattern_counting.dp import DPTable
            self.table_type = DPTable

    def table(self, G):
        """Make an appropriate DPTable, given the hints specified"""
        return self.table_type(G)

    def before_color_set(self, colors):
        """Remember how many colors we're looking at currently"""
        self.n_colors = len(colors)
        # If execution data file has been specified
        if self.execdata_file:
            # Reset the count for the color set
            self.current_color_set_count = 0
            # Write the color set to the file
            self.execdata_file.write(
                ",".join([str(color) for color in colors]) + " : ")

    def combine_count(self, count):
        """
        Add the count returned from dynamic programming on one TDD

        We use the number of colors remembered in before_color_set to index
        the __in_ex list.  This gives us a coefficient by which we multiply
        the count.  This modified count gets added into our total.  In the
        end, this corrects all the double-counting.
        """

        if self.tree_depth <= self.n_colors <= self.min_p:
            self.pattern_count += self.__in_ex[self.min_p - self.n_colors] * count
            self.current_color_set_count += count

    def after_color_set(self, colors):
        # If execution data file has been specified
        if self.execdata_file:
            # Write the count for that color set to the file
            self.execdata_file.write(str(self.current_color_set_count) + "\n")

    def get_count(self):
        """Return the total number of occurrences of the pattern seen"""
        return self.pattern_count

