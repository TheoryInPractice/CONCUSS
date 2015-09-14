#!/usr/bin/env python2.7
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import sys
import os
import argparse
#import ConfigParser
from lib.util.parse_config_safe import parse_config_safe
from lib.coloring.generate_coloring import ccalgorithm_factory, \
     import_colmodules, save_file
from lib.graph.graphformats import load_graph as load_graph
from lib.pattern_counting.pattern_counter import PatternCounter
import cProfile
import pstats
from lib.graph.graph import Coloring
import lib.graph.pattern_generator as pattern_gen
from lib.graph.treedepth import treedepth

def import_modules(name):
    """
    Return namespace of module

    Arguments:
        name:  name of module to import
    """
    if not name:
        return None
    funcname = name.split('.')[-1]
    modname = '.'.join(name.split('.')[:-1])
    module = __import__(modname, fromlist=[funcname])
    return getattr(module, funcname)


def coloring_from_file(filename, graph, td, cfgfile, verbose, verify=False):
    """Read a coloring from a file"""
    # Load the coloring from the file
    coloring = Coloring()
    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            vertex, color = line.split(": ")
            coloring[int(vertex)] = int(color)

    if verify:
        # Verify that the coloring is correct
        if verbose:
            print "Verifying coloring..."

        Config = parse_config_safe(cfgfile)
        ldo = import_colmodules(Config.get('color',
                                           'low_degree_orientation'))
        ctd = import_colmodules(Config.get('color',
                                           'check_tree_depth'))
        orig, _ = graph.normalize()

        correct = True
        try:
            correct, _ = ctd(orig, ldo(orig), coloring, td)
        except TypeError:
            correct = False
        assert correct, \
            "Coloring is not a valid p-centered coloring for host graph"

        if verbose:
            print "Coloring is correct"

    # Return the coloring
    return coloring


def p_centered_coloring(graph, td, cfgfile, verbose):
    """Start running the p-centered coloring"""
    m = ccalgorithm_factory(cfgfile, not verbose)
    col = m.start(graph, td)
    return col


def runPipeline(graph, pattern, cfgFile, colorFile, color_no_verify, output,
                verbose, profile):
    """Basic running of the pipeline"""

    if profile:  # time profiling
        readProfile = cProfile.Profile()
        readProfile.enable()

    # If the user specifies the pattern name for ex. as -> clique 4
    if len(pattern) == 2:
        # Get pattern type and number of vertices
        pattern_type = pattern[0]
        try:
            pattern_num_vertices = int(pattern[1])
        except ValueError:
            print "\nPlease provide an integer as the second argument " \
                  "to the -m flag\n"
            sys.exit(1)
        # Get the generator for that type of pattern
        generator = pattern_gen.get_generator(pattern_type)
        # Generate the pattern
        H = generator(pattern_num_vertices)
        # Compute lower bound given the pattern
        td_lower = treedepth(H, pattern_type)
    else:
        # Load pattern from file
        H = load_graph(pattern[0])
        # Computer lower bound
        td_lower = treedepth(H)

    # Read graphs from file
    G = load_graph(graph)
    td = len(H)

    G_path, G_local_name = os.path.split(graph)
    G_name, G_extension = os.path.splitext(G_local_name)

    if verbose:
        print "G has {0} vertices and {1} edges".format(len(G), G.num_edges())

    if profile:  # time profiling
        readProfile.disable()
        printProfileStats("reading graphs", readProfile)
        colorProfile = cProfile.Profile()
        colorProfile.enable()

    # Find p-centered coloring
    if colorFile is None:
        coloring = p_centered_coloring(G, td, cfgFile, verbose)
        save_file(coloring, 'colorings/' + G_name + str(td), False, verbose)
    else:
        coloring = coloring_from_file(colorFile, G, td, cfgFile, verbose,
                                      not color_no_verify)

    if profile:  # time profiling
        colorProfile.disable()
        printProfileStats("coloring", colorProfile)
        patternProfile = cProfile.Profile()
        patternProfile.enable()

    # Get configuration settings for dynamic programming
    cfgParser = parse_config_safe(cfgFile)
    kpat_name = cfgParser.get('compute', 'k_pattern')
    # tab_name  = cfgParser.get('dp', 'tab')
    table_hints = {
        'forward': cfgParser.getboolean('compute', 'table_forward'),
        'reuse': cfgParser.getboolean('compute', 'table_reuse')
    }
    count_name = cfgParser.get('combine', 'count')
    sweep_name = cfgParser.get('decompose', 'sweep')

    patternClass = import_modules("lib.pattern_counting.dp."+kpat_name)
    count_class = import_modules('lib.pattern_counting.double_count.' +
                                       count_name)
    sweep_class = import_modules('lib.decomposition.' + sweep_name)

    # Count patterns
    pattern_counter = PatternCounter(G, H, td_lower, coloring,
                                     pattern_class=patternClass,
                                     table_hints=table_hints,
                                     decomp_class=sweep_class,
                                     combiner_class=count_class,
                                     verbose=verbose)
    patternCount = pattern_counter.count_patterns()
    print "Number of occurrences of H in G: {0}".format(patternCount)

    if profile:  # time profiling
        patternProfile.disable()
        printProfileStats("pattern counting", patternProfile)


def printProfileStats(name, profile, percent=1.0):
    """
    Prints out the function call statistics using the cProfile and
    pstats libraries

    Arguments:
        name:  string labelling the purpose of the statistics
        profile:  cProfile to print
        percent:  decimal proportion of list to print.  Default prints
                all (1.0)
    """
    sortby = 'time'
    restrictions = ""
    ps = pstats.Stats(profile).strip_dirs().sort_stats(sortby)
    print "Stats from {0}".format(name)
    ps.print_stats(restrictions, percent)
