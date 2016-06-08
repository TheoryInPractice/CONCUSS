#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import Counter, OrderedDict
from itertools import combinations

from count_combiner import CountCombiner
from lib.pattern_counting.dp import ColorDPTable
from lib.util.itertools_ext import powerset


class HybridCount(CountCombiner):
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

    def __init__(self, p, coloring, table_hints, td, execdata_file=None):
        """
        Build a list of sets of colors on which we perform color-tracking
        dynamic programming.
        """
        super(HybridCount, self).__init__(p, coloring, table_hints, td)
        self.totals = Counter()
        self.raw_count = Counter()
        self.tree_depth = self.min_p
        self.overcount = Counter()
        self.colors = None
        if table_hints['forward']:
            from lib.pattern_counting.dp import ForwardDPTable
            self.uncolored_table = ForwardDPTable
        else:
            from lib.pattern_counting.dp import DPTable
            self.uncolored_table = DPTable

        # Set up the dict of small sets
        # NOTE: which dict class we use affects the number of sets produced,
        # but there isn't a clear-cut winner which always produces fewer sets.
        # OrderedDict is usually better than dict, but in some cases dict wins.
        # Maybe we should try with both and use the lower one.  Ideally we
        # should figure out the best order and always use that, but maybe there
        # isn't an order that's always best (or rather, such an order may be
        # hard to describe).
        # d = {}
        d = OrderedDict()
        # The list of sets for which we will do ColorDP
        self.color_dp_list = []
        # Local reference to self.color_dp_list.append for the loop
        cdpappend = self.color_dp_list.append
        for c in combinations(self.coloring.usedcols, self.min_p-1):
            d[frozenset(c)] = False

        # For each number of sets which can be duplicated:
        j = 0
        while False in d.itervalues():
            j += 1
            # For each set of size min_p-1:
            for k in d.iterkeys():
                # If we haven't seen it yet:
                if not d[k]:
                    # Loop over all colors
                    for i in self.coloring.usedcols:
                        # If the set already has this color, try the next color
                        if i in k:
                            continue
                        # Add the color to the set
                        k2 = k | frozenset((i,))
                        # Ensure we aren't duplicating too many other sets
                        add = j
                        for c in combinations(k2, self.min_p-1):
                            if d[frozenset(c)] > 0:
                                add -= 1
                            if not add:
                                break
                        # If we haven't duplicated too many sets, add the big
                        # set to our list of ones to perform ColorDP on.
                        if add:
                            for c in combinations(k2, self.min_p-1):
                                d[frozenset(c)] = True
                            # Equivalent to self.color_dp_list.append(k2)
                            cdpappend(k2)

    def table(self, G):
        """
        Make an appropriate DPTable object

        For HybridCount, we must consider both the hints and the set of
        colors.  Since there's no ForwardColorDPTable, we only use the
        'reuse' hint there, and since there's no reuse option for the
        standard DPTable, we only respect the 'forward' hint there.
        """
        if self.use_color_dp:
            return ColorDPTable(G, reuse=self.table_hints['reuse'])
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
            self.colors = fc
        # Otherwise, we're going to perform cheaper DP for a larger set.
        else:
            self.colors = fc

    def combine_count(self, count):
        """Store the count returned from dynamic programming on one TDD"""
        if self.tree_depth <= len(self.colors) <= self.min_p:
            if self.use_color_dp:
                self.raw_count += count
            else:
                self.overcount[self.colors] += count

    def after_color_set(self, colors):
        """Combine the count for this color set into the total count"""
        # If we're counting a small set, and thus acting like ColorCount,
        # combine raw_count into totals.
        if self.use_color_dp:
            self.totals |= self.raw_count

    def get_count(self):
        """Return the sum of the counts for all color sets"""
        # Local reference to self.totals for the loop
        totals = self.totals

        total_count = 0
        for oc_set, oc in self.overcount.iteritems():
            # TODO: powerset is inefficient here (generates sets too small to
            # have anything in them).  Replace with something better.
            oc -= reduce(lambda x, y: x + totals[frozenset(y)],
                         powerset(oc_set), 0)
            total_count += oc
        return sum(totals.itervalues()) + total_count
