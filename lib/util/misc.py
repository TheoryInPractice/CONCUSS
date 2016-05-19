#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import sys


def clear_output_line():
    sys.stdout.write('\r')
    sys.stdout.write(''.ljust(40))
    sys.stdout.write('\r')
# end def


def percent_output(current, total):
    clear_output_line()
    sys.stdout.write('  ')
    sys.stdout.write(str(current))
    sys.stdout.write('/')
    sys.stdout.write(str(total))
    sys.stdout.write(' (')
    sys.stdout.write(str(100*current/total))
    sys.stdout.write('%)')
    sys.stdout.flush()
# end def
