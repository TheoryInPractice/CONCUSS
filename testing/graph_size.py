#!/usr/bin/env python2.7
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import sys
import os
import argparse
import ConfigParser
from lib.graph import graph
from lib.coloring.coloring import *
from lib.graph.graphformats import load_graph
from lib.run_pipeline import parse_pattern_argument

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("pattern", help="filename of the pattern graph",
                        type=str)
    args = parser.parse_args()
    h, _ = parse_pattern_argument(args.pattern)
    print len(h)
