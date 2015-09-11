#!/usr/bin/env python2.7
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


from lib.graph.graphformats import load_graph as load_graph
import sys
import os
import argparse
#import ConfigParser
from lib.util.parse_config_safe import parse_config_safe
from lib.graph.graph import Coloring
from lib.coloring.basic.merge_colors import merge_colors

#Config = ConfigParser.ConfigParser()


def save_file(col, filename, override=False, verbose=False):
    num = len(col)
    if not override:
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                before = int(f.readline())
                if (before > num):
                    override = True
                    if verbose:
                        print "coloring is better, override result (before:", \
                               before, ", now:", num, ")"
                else:
                    if verbose:
                        print "don't override (before:", before, ", now:", num, ")"
        else:
            override = True
            print "there is still no coloring, create result"

    if override:
        with open(filename, 'w') as f:
            f.write(str(num) + '\n')
            for v in col:
                f.write("{0}: {1} \n".format(v, col[v]))
# end def


def import_colmodules(name):
    if not name:
        return None

    funcname = name.split('.')[-1]
    modname = "lib.coloring."+name
    module = __import__(modname, fromlist=[funcname])
    return getattr(module, funcname)
# end def


def ccalgorithm_factory(cfgfile, silent):
    Config = parse_config_safe(cfgfile)

    func_ldo = import_colmodules(Config.get('color',
                                            'low_degree_orientation'))
    func_step = import_colmodules(Config.get('color', 'step'))
    func_col = import_colmodules(Config.get('color', 'coloring'))
    func_ctd = import_colmodules(Config.get('color', 'check_tree_depth'))
    if Config.has_option('color', 'optimization'):
        func_opt = import_colmodules(Config.get('color', 'optimization'))
    else:
        func_opt = None

    if Config.has_option('color', 'preprocess'):
        func_preprocess = import_colmodules(Config.get('color',
                                                       'preprocess'))
    else:
        func_preprocess = None

    return CCAlgorithm(
            preprocess=func_preprocess,
            ldo=func_ldo,
            step=func_step,
            col=func_col,
            ctd=func_ctd,
            opt=func_opt,
            silent=silent)


class CCAlgorithm(object):

    def __init__(self, preprocess=None, ldo=None, step=None, col=None,
                 ctd=None, opt=None, silent=False):
        self.preprocess = preprocess
        self.ldo = ldo
        self.step = step
        self.col = col
        self.ctd = ctd
        self.opt = opt
        self.td = None
        self.silent = silent

    def echo(self, *msg):
        if not self.silent:
            print " ".join(map(str, msg))

    def start(self, rawgraph, treeDepth):
        self.td = treeDepth

        col = Coloring()

        trans = {}
        frat = {}

        if self.preprocess:
            self.echo("Preprocess coloring optimizations")
            pp_graph, postprocess = self.preprocess(rawgraph)

        # Normalize graph so that its vertices are named 0, ..., n-1
        pp_graph.remove_loops()
        orig, mapping = pp_graph.normalize()
        for i in xrange(0, len(orig)):
            assert i in orig, "Vertex {0} not contained in " \
                    "norm. graph of size {1}".format(i, len(orig))

        g = self.ldo(orig)
        col = self.col(orig, g, trans, frat, col)

        correct, nodes = self.ctd(orig, g, col, treeDepth)

        i = 0
        while (not correct):
            i += 1
            self.echo("step", i)

            g, trans, frat = self.step(orig, g, trans, frat, col, nodes, i,
                                       treeDepth, self.ldo)

            col = self.col(orig, g, trans, frat, col)
            correct, nodes = self.ctd(orig, g, col, treeDepth)

            if correct:
                self.echo("  step", i, "is correct")
                break

        # end while
        self.echo("number of colors:", len(col))

        if self.opt:
            self.echo("Optimizing...")
            col = self.opt(orig, g, trans, frat, col, i, treeDepth, self)
            self.echo("number of colors:", len(col))

        # Map coloring back to original vertex labels
        colrenamed = Coloring()
        for v in col:
            colrenamed[mapping[v]] = col[v]

        if self.preprocess:
            self.echo("Postprocessing")
            postprocess(colrenamed)
            self.echo("number of colors:", len(colrenamed))

        self.echo("Merging color classes")
        col_merged = merge_colors(rawgraph, colrenamed, treeDepth)
        self.echo("number of colors:", len(col_merged))

        return col_merged
    # end def

# end classgit


def start_coloring(filename, td, cfgfile, output):
    m = ccalgorithm_factory(cfgfile, False)

    p, fn = os.path.split(filename)
    graphname, e = os.path.splitext(fn)

    col = m.start(load_graph(filename), td)

    # Store results in common folder and, if supplied, in output file
    save_file(col, 'colorings/' + graphname + str(td), False)
    if output:
        save_file(col, output, True)
# end def

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", help="filename of the graph", type=str)
    parser.add_argument("treeDepth", help="tree depth", type=int)
    parser.add_argument("config", help="filename of the config file", type=str,
                        nargs='?', default='config/default.cfg')
    parser.add_argument("-o", "--output", help="filename of the result",
                        type=str, nargs='?', default=None)
    args = parser.parse_args()

    start_coloring(args.graph, args.treeDepth, args.config, args.output)
