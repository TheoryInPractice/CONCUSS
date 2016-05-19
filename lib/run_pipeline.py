#!/usr/bin/env python2.7
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import sys
import os
import shutil
from zipfile import ZipFile
import cProfile
import pstats
import ConfigParser

from lib.util.parse_config_safe import parse_config_safe
from lib.coloring.generate_coloring import (ccalgorithm_factory,
    import_colmodules, save_file)
from lib.graph.graphformats import load_graph as load_graph
from lib.pattern_counting.pattern_counter import PatternCounter
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


def p_centered_coloring(graph, td, cfgfile, verbose, execdata):
    """Start running the p-centered coloring"""
    m = ccalgorithm_factory(cfgfile, not verbose, execdata)
    col = m.start(graph, td)
    return col


def pattern_argument_error_msg():
    print "\nThe argument provided for 'pattern' is invalid.\n"
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


def is_basic_pattern(pattern):
    name, ext = os.path.splitext(pattern)
    return ext == ""


def get_pattern_from_file(filename):
    # Argument is a filename
        try:
            # Try to load the graph from file
            H = load_graph(filename)
            # Return pattern along with lower bound on its treedepth
            return H, treedepth(H)
        except Exception:
            # Invalid file extension
            pattern_argument_error_msg()


def get_pattern_from_generator(pattern):
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
            pattern_argument_error_msg()

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
            pattern_argument_error_msg()
    else:
        # Number of vertices not provided in argument
        pattern_argument_error_msg()

def parse_pattern_argument(pattern):
    """
    Parses the 'pattern' command line argument.
    Checks to see if this argument is a filename or
    a description of the pattern

    :param pattern: Filename or description of pattern
    :return: A tuple with the pattern graph and a lower
             bound on its treedepth
    """
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
                pattern_argument_error_msg()

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
                pattern_argument_error_msg()
        else:
            # Number of vertices not provided in argument
            pattern_argument_error_msg()
    else:
        # Argument is a filename
        try:
            # Try to load the graph from file
            H = load_graph(pattern)
            # Return pattern along with lower bound on its treedepth
            return H, treedepth(H)
        except Exception:
            # Invalid file extension
            pattern_argument_error_msg()


def runPipeline(graph, pattern, cfgFile, colorFile, color_no_verify, output,
                verbose, profile, execution_data):
    """Basic running of the pipeline"""

    # If execution_data flag is set
    execdata = execution_data is not None
    if execdata:
        # Check if directory exists already
        if os.path.isdir("./execdata"):
            # delete it, if it does exist
            shutil.rmtree("./execdata")
        # make new directory called "execdata"
        os.mkdir("./execdata")

    if profile:  # time profiling
        readProfile = cProfile.Profile()
        readProfile.enable()

    basic_pattern = is_basic_pattern(pattern)

    if basic_pattern:
        H, td_lower = get_pattern_from_generator(pattern)
    else:
        H, td_lower = get_pattern_from_file(pattern)

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
        coloring = p_centered_coloring(G, td, cfgFile, verbose, execdata)
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

    patternClass = import_modules("lib.pattern_counting.dp." + kpat_name)
    count_class = import_modules('lib.pattern_counting.double_count.' +
                                 count_name)
    sweep_class = import_modules('lib.decomposition.' + sweep_name)

    # Output for Count stage
    if execdata:
        count_path = 'execdata/count/'
        if not os.path.exists(count_path):
            os.makedirs(count_path)
        big_component_file = open(count_path+'big_component.txt', 'w')
        tdd_file = open(count_path+'tdd.txt', 'w')
        dp_table_file = open(count_path+'dp_table.txt', 'w')
    else:
        big_component_file = None
        tdd_file = None
        dp_table_file = None

    # Output for Combine stage
    if execdata:
        combine_path = 'execdata/combine/'
        if not os.path.exists(combine_path):
            os.makedirs(combine_path)
        # Open the file that needs to be passed to the count combiner
        colset_count_file = open('execdata/combine/counts_per_colorset.txt',
                                 'w')
    else:
        # If execution data is not requested, we don't need to open a file
        colset_count_file = None

    if count_name != "InclusionExclusion" and execdata:
        print "CONCUSS can only output execution data using the",
        print "InclusionExclusion combiner class."
        sys.exit(1)

    # Count patterns
    pattern_counter = PatternCounter(G, H, td_lower, coloring,
                                     pattern_class=patternClass,
                                     table_hints=table_hints,
                                     decomp_class=sweep_class,
                                     combiner_class=count_class,
                                     verbose=verbose,
                                     big_component_file=big_component_file,
                                     tdd_file=tdd_file,
                                     dp_table_file=dp_table_file,
                                     colset_count_file=colset_count_file)
    patternCount = pattern_counter.count_patterns()
    print "Number of occurrences of H in G: {0}".format(patternCount)

    if execdata:
        # Close count stage files
        big_component_file.close()
        tdd_file.close()
        dp_table_file.close()
        # Close the color set file
        colset_count_file.close()

        # if execution data flag is set
        # make and write to visinfo.cfg
        with open('execdata/visinfo.cfg', 'w') as visinfo:
            write_visinfo(visinfo, graph, pattern)

        # write execution data to zip
        with ZipFile(execution_data, 'w') as exec_zip:
            # exec_zip.write("execdata/visinfo.cfg", "visinfo.cfg")

            # Write data from 'execdata' directory to the zip:
            rootDir = './execdata/'
            for dir_name, _, file_list in os.walk(rootDir):
                for f_name in file_list:
                    full_path = dir_name + '/' + f_name
                    exec_zip.write(
                        full_path,
                        '/'.join(full_path.split('/')[2:]))

            exec_zip.write(cfgFile, os.path.split(cfgFile)[1])
            exec_zip.write(graph, os.path.split(graph)[1])

            # Check to see if the user specified a basic pattern
            if basic_pattern:
                from lib.graph.graphformats import write_edgelist
                # Write the pattern graph object to a file as an edgelist
                with open(pattern + '.txt', 'w') as pattern_file:
                    write_edgelist(H, pattern_file)
                # Write the file to the zip
                exec_zip.write(
                    pattern + '.txt',
                    os.path.split(pattern + '.txt')[1])
                # File written to zip, delete it
                os.remove(pattern + '.txt')
            else:
                exec_zip.write(pattern, os.path.split(pattern)[1])

        # delete execution data stored in folder
        shutil.rmtree('./execdata')

    if profile:  # time profiling
        patternProfile.disable()
        printProfileStats("pattern counting", patternProfile)


def write_visinfo(visfile, graph, pattern):
    """
    Write to the visinfo.cfg file

    :param visfile: File handle to the config file
    :param graph: The name of the graph used
    :param pattern: The name of the pattern used

    """
    # Create configuration object
    config = ConfigParser.SafeConfigParser()

    # Pipeline info
    config.add_section('pipeline')
    config.set('pipeline', 'name', 'concuss')
    config.set('pipeline', 'command', ' '.join(sys.argv))

    # Graph and motif info
    config.add_section('graphs')
    config.set('graphs', 'graph', os.path.split(graph)[1])
    if is_basic_pattern(pattern):
        config.set('graphs', 'motif', os.path.split(pattern + '.txt')[1])
    else:
        config.set('graphs', 'motif', os.path.split(pattern)[1])

    # Write configuration to the visinfo file
    config.write(visfile)

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
