#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import Counter

from count_combiner import CountCombiner


class ColorCount(CountCombiner):
    """
    Perform dynamic programming with a special table which keeps track
    of colors.

    By keeping track of colors, ColorCount allows us to not have to
    look at smaller sets of colors.  This gets passed all the way back
    to the DecompGenerator, so the decompositions with fewer than p
    colors are never even created.  After processing all decompositions
    with one set of colors, we fill the counts found into a large table
    called totals.  If an entry of totals is already full, we don't
    change it; if it's 0, we can put our new count in.  When returning
    the final count, we simply add all the entries in totals.
    """

    def __init__(self, p, coloring, table_hints, td, execdata_file=None):
        """Create tables for keeping track of the separate counts"""
        super(ColorCount, self).__init__(p, coloring, table_hints, td)
        self.totals = Counter()
        self.raw_count = Counter()
        self.tree_depth = self.min_p
        self.n_colors = None
        from lib.pattern_counting.dp import ColorDPTable
        self.table_type = ColorDPTable

    def table(self, G):
        """Make an appropriate DPTable, given the hints specified"""
        return self.table_type(G, reuse=self.table_hints['reuse'])

    def before_color_set(self, colors):
        """Clear the raw_count for the new color set"""
        self.n_colors = len(colors)
        self.raw_count.clear()

    def combine_count(self, count):
        """Add the count returned from dynamic programming on one TDD"""
        if self.tree_depth <= self.n_colors <= self.min_p:
            self.raw_count += count

    def after_color_set(self, colors):
        """Combine the count for this color set into the total count"""
        self.totals |= self.raw_count

    def get_count(self):
        """Return the total number of occurrences of the pattern seen"""
        return sum(self.totals.itervalues())
