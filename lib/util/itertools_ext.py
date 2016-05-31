#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import itertools


def powerset(iterable):
    s = iterable  # list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in
                                         range(len(s)+1))


def xpowerset(iterable):
    return powerset(iterable)


def choose(n, m):
    assert n >= m, "Cannot choose {0} elements from {1}".format(m, n)
    result = 1
    for n_i, m_i in zip(range(n, m, -1), range(1, m+1)):
        result *= n_i
        result /= m_i
    return result
