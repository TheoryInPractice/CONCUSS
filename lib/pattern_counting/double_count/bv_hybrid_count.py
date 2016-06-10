#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import Counter, OrderedDict
from itertools import combinations

from hybrid_count import HybridCount
from lib.pattern_counting.dp import BVColorDPTable
from lib.util.itertools_ext import powerset


class BVHybridCount(HybridCount):
    """
    Combine counts like ColorCount, but smarter

    In HybridCount, we perform ColorCount-like dynamic programming to
    get counts for a few of the sets of colors.  We carefully choose
    which of these sets of colors we use so that all of the smaller
    sets are counted at least once (ideally exactly once).  For all of
    the other large sets of colors, we use the cheaper dynamic
    programming from InclusionExclusion.  We use the ColorCount to
    adjust the totals, but doing so is simpler than in InEx because
    the counts are mutually exclusive.

    Because we can't force a particular DecompGenerator, we could be
    seeing the sets of colors in any order.  This means we need to
    keep track of both types of count in parallel, then combine them
    together at the end.  For each set of colors on which we did
    InclusionExclusion-like dynamic programming, we subtract all the
    counts from its color subsets.  Then we add all those counts
    together with all the counts from ColorCount, and return the
    sum.
    """

    def table(self, G):
        """
        Make an appropriate DPTable object

        For HybridCount, we must consider both the hints and the set of
        colors.  Since there's no ForwardColorDPTable, we only use the
        'reuse' hint there, and since there's no reuse option for the
        standard DPTable, we only respect the 'forward' hint there.
        """
        if self.use_color_dp:
            self.tableobj = BVColorDPTable(G, self.p, self.colors,
                                           reuse=self.table_hints['reuse'])
            return self.tableobj
        else:
            return self.uncolored_table(G)

    def before_color_set(self, colors):
        """
        Perform necessary bookkeeping for the new color set

        First, we determine which kind of dynamic programming we'll be
        doing.  If we're using ColorDP, we clear the raw_count as in
        ColorCount.  If we're using standard DP, we store the set of
        colors we're looking at.
        """
        fc = frozenset(colors)
        self.use_color_dp = (fc in self.color_dp_list)

        # If we're counting a small set, and will thus be acting like
        # ColorCount, clear raw_count.
        if self.use_color_dp:
            self.raw_count.clear()
        # Both procedures need the colors later
        self.colors = fc

    def combine_count(self, count):
        """Store the count returned from dynamic programming on one TDD"""
        if self.tree_depth <= len(self.colors) <= self.min_p:
            if self.use_color_dp:
                # Localize variables for the loop
                field_width = self.tableobj.field_width
                mask = self.tableobj.mask
                colors = self.tableobj.colors
                # For every color set (represented as an integer)
                for i in range(1 << len(colors)):
                    # Get the count for this subset of colors
                    setcount = (count >> (i * field_width)) & mask
                    # Add it to the counts for the current set of colors if
                    # it's > 0
                    if setcount:
                        color_set = set()
                        for c in colors.iterkeys():
                            if colors[c] & i:
                                color_set.add(c)
                        self.raw_count[frozenset(color_set)] += setcount
            else:
                self.overcount[self.colors] += count
