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
from lib.graph.pattern_generator import clique, path, star
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


def pattern_argument_error_msg(pat_arg):
    print "\nThe argument '" + pat_arg + "' provided for 'pattern' is invalid.\n"
    print "Please use format:\n\n" \
          "\033[1mfilename.txt \033[0m\n" \
          "For example: ./path_to_file/K3.txt" \
          "\n\nor\n\n" \
          "Basic patterns:\n\n" \
          "Usage: \033[1mpattern_nameint\033[0m\n" \
          "For example: clique3\n" \
          "\nor for bipartite patterns:\n" \
          "Usage: \033[1mpattern_nameint,int\033[0m\n" \
          "For example: biclique3,4\n" \
          "\nSupported basic patterns:\n"
    print "\n".join(pattern_gen.supported_patterns)
    print
    sys.exit(1)

def parse_pattern_argument(pattern):
    """
    Parses the 'pattern' command line argument.
    Checks to see if this argument is a filename or
    a description of the pattern

    :param pattern: Filename or description of pattern
    :return: A tuple with the pattern graph and a lower
             bound on its treedepth
    """

    import os

    # Get the name of the file and the file extension
    name, ext = os.path.splitext(pattern)
    # There is no extension, so argument is a description
    # of the pattern
    if ext == "":
        import re
        p = re.compile(r'(\d*)')
        # Parse out the different parts of the argument
        args = filter(lambda x: x != "" and x != ",", p.split(pattern))
        # There are two parts
        if len(args) == 2 and args[0] not in pattern_gen.bipartite_patterns:
            try:
                # Get the generator for the pattern type
                generator = pattern_gen.get_generator(args[0])
                # Get the number of vertices provided
                pattern_num_vertices = int(args[1])
                # Generate the pattern
                H = generator(pattern_num_vertices)
                # Return the pattern along with its treedepth
                return H, treedepth(H, args[0], pattern_num_vertices)
            except KeyError:
                pattern_argument_error_msg(pattern)

        # Bipartite pattern type provided
        elif len(args) == 3 and args[0] in pattern_gen.bipartite_patterns:
            # Make sure it is a valid bipartite pattern
            try:
                generator = pattern_gen.get_generator(args[0])
                # Try to get the two set sizes
                m = int(args[1])
                n = int(args[2])
                # Generate the pattern
                H = generator(m, n)
                # Return the pattern along with its treedepth
                return H, treedepth(H, args[0], m, n)
            except (KeyError, ValueError):
                # Invalid sizes provided
                pattern_argument_error_msg(pattern)
        else:
            # Number of vertices not provided in argument
            pattern_argument_error_msg(pattern)
    else:
        # Argument is a filename
        try:
            # Try to load the graph from file
            H = load_graph(pattern)
            # Return pattern along with lower bound on its treedepth
            return H, treedepth(H)
        except Exception:
            # Invalid file extension
            pattern_argument_error_msg(pattern)


def parse_multifile(multifile):
    if multifile:
        try:
            m_file = multifile[0]
            if m_file:
                pattern_reader = open(m_file, 'r')
                patterns = [line[:-1] for line in pattern_reader]
                multi=[]
                td_lower=sys.maxint
                for pat in patterns:
                    graph, td = parse_pattern_argument(pat)
                    multi.append(graph)
                    td_lower = min(td, td_lower)
                return multi, td_lower
            else:
                print "\nPlease provide a valid multi-pattern file while using argument 'multi'\n"
                sys.exit(1)
        except IOError:
            print "\nPlease provide a valid multi-pattern file while using argument 'multi'\n"
            sys.exit(1)
    else:
        print "\nPlease provide a valid multi-pattern file while using argument 'multi'\n"
        sys.exit(1)


def runPipeline(graph, pattern, cfgFile, colorFile, color_no_verify, output,
                verbose, profile, multifile):
    """Basic running of the pipeline"""

    if profile:  # time profiling
        readProfile = cProfile.Profile()
        readProfile.enable()

    if pattern == 'multi':
        multi, td_lower = parse_multifile(multifile)
    else:
        pat, td_lower = parse_pattern_argument(pattern)
        multi = list(pat)

    # Read graphs from file
    G = load_graph(graph)
    #td = len(H)

    #multi = [path(3), star(3), clique(3)]

    td = len(max(multi, key=len))
    #td_lower = 2

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
    # pattern_counter = PatternCounter(G, H, td_lower, coloring,
    #                                  pattern_class=patternClass,
    #                                  table_hints=table_hints,
    #                                  decomp_class=sweep_class,
    #                                  combiner_class=count_class,
    #                                  verbose=verbose)

    pattern_counter = PatternCounter(G, multi, td_lower, coloring,
                                     pattern_class=patternClass,
                                     table_hints=table_hints,
                                     decomp_class=sweep_class,
                                     combiner_class=count_class,
                                     verbose=verbose)

    patternCount = pattern_counter.count_patterns()
    pattern_names = [pat[:-1] for pat in open(multifile[0], 'r')]
    for i in range(len(pattern_names)):
        print "Number of occurrences of {0} in G: {1}".format(pattern_names[i], patternCount[i])

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
