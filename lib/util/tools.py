#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


def rev_bfs(v, graph, maxdepth):
    visited = set([v])
    current = set([v])
    depth = 0
    while len(current) > 0 and depth <= maxdepth:
        yield(current)
        nbs = set()
        for w in current:
            nbs = nbs | set(in_neighbours(w, graph))
        current = nbs - visited
        visited = visited | current
        depth += 1
