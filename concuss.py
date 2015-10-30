#!/usr/bin/env python2.7

#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#

import argparse
from lib.run_pipeline import runPipeline
import sys


def main():
    """
    Parse all the flags and arguments the user provides for running the
    pipeline and run the pipeline.

    """
    parser = argparse.ArgumentParser()

    # Add arguments to the argument parser
    parser.add_argument("graph", help="filename of the large graph",
                        type=str)
    parser.add_argument("pattern", help="filename of the pattern graph",
                        type=str)
    parser.add_argument("config",
                        help="filename of the configuration settings",
                        nargs='?', type=str, default='config/default.cfg')
    parser.add_argument("-o", "--output", help="filename of the result",
                        type=str, nargs='?', default=None)
    parser.add_argument("-v", "--verbose", help="verbose output",
                        action="store_true")
    parser.add_argument("-p", "--profile", help="profile function calls",
                        action="store_true")
    parser.add_argument("-c", "--coloring",
                        help="filename of existing p-centered coloring",
                        type=str, nargs='?', default=None)
    parser.add_argument("-C", "--coloring-no-verify",
                        help="do not verify correctness of existing coloring",
                        action="store_true")
    parser.add_argument("-m", "--multi_pat_file", help="File with multiple patterns",
                        nargs=1, type=str)

    # Parse the arguments provided by the user to pass them to the
    # runPipeline method
    args = parser.parse_args()

    # Run the pipeline
    runPipeline(args.graph, args.pattern, args.config, args.coloring,
                args.coloring_no_verify, args.output, args.verbose,
                args.profile, args.multi_pat_file)

if __name__ == "__main__":
    main()
