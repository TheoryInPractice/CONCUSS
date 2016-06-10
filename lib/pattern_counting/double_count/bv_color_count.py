#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import Counter

from count_combiner import CountCombiner


class BVColorCount(CountCombiner):
    """
    Perform dynamic programming with a special table which keeps track
    of colors in bit vectors.

    By keeping track of colors, BVColorCount allows us to not have to
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
        super(BVColorCount, self).__init__(p, coloring, table_hints, td)
        self.totals = Counter()
        self.raw_count = Counter()
        self.tree_depth = self.min_p

        from lib.pattern_counting.dp import BVColorDPTable
        self.table_type = BVColorDPTable

    def table(self, G):
        """Make an appropriate DPTable, given the hints specified"""
        self.tableobj = self.table_type(G, self.p, self.colors,
                                        reuse=self.table_hints['reuse'])
        return self.tableobj

    def before_color_set(self, colors):
        """Clear the raw_count for the new color set"""
        self.raw_count.clear()
        self.colors = colors

    def combine_count(self, count):
        """Add the count returned from dynamic programming on one TDD"""
        if self.tree_depth <= len(self.colors) <= self.min_p:
            # Localize variables for the loop
            field_width = self.tableobj.field_width
            mask = self.tableobj.mask
            colors = self.tableobj.colors
            # For every color set (represented as an integer)
            for i in range(1 << len(colors)):
                # Get the count for this subset of colors
                setcount = (count >> (i * field_width)) & mask
                # Add it to the counts for the current set of colors if it's > 0
                if setcount:
                    color_set = set()
                    for c in colors.iterkeys():
                        if colors[c] & i:
                            color_set.add(c)
                    self.raw_count[frozenset(color_set)] += setcount

    def after_color_set(self, colors):
        """Combine the count for this color set into the total count"""
        if self.tree_depth <= len(self.colors) <= self.min_p:
            self.totals |= self.raw_count

    def get_count(self):
        """Return the total number of occurrences of the pattern seen"""
        return sum(self.totals.itervalues())
