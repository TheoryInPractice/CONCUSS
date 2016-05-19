#!/usr/bin/env python2.7
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#

import sys
import argparse
import itertools
from lib.graph.graphformats import load_graph
from lib.graph.graphformats import load_coloring
from lib.graph.graphformats import remove_loops
from lib.graph.graph import Coloring
from lib.coloring.basic.check_tree_depth import check_tree_depth

SILENT = True

def recolor(cols, vertices, c):
    for v in vertices:
        cols[v] = c

def independent_colors(G, c1, c2):
    #for v in c1:
    #    if not G.neighbours(v).isdisjoint(c2):
    #        return False
    #for v in c2:
    #    if not G.neighbours(v).isdisjoint(c1):
    #        return False
    #return True
    return all(G.neighbours(v).isdisjoint(c2) for v in c1)

def echo(*text):
    if not SILENT:
        print " ".join(map(str, text))

def same_color(cols, vertices, c):
    for v in vertices:
        if cols[v] != c:
            return False
    return True
    #return all(cols[v] == c for v in vertices)

def merge_colors(graph, cols, p):
    # order the coloring by frequency
    ordered_col = cols.normalize()

    # create lookup of vertices by color
    color_sets = [set() for i in ordered_col.colors()]
    for v in graph:
        color_sets[ordered_col[v]].add(v)
    num_colors = len(ordered_col)
    echo(len(ordered_col))
    # iterate through all colors
    for c1 in range(num_colors):
        # vertices with color c1
        c1_vertices = color_sets[c1]

        # skip ahead if we've already merged c1 with another color
        if len(c1_vertices) == 0:
            continue
        echo("\n", c1, c1_vertices)
        # otherwise iterate through all colors with fewer vertices
        
        for c2 in range(c1+1,num_colors):
            # vertices with color c2
            c2_vertices = color_sets[c2]

            # skip ahead if we've already merged c2 with another color
            if len(c2_vertices) == 0:
                continue
            echo("\t", c2, c2_vertices)
            # check whether c1 and c2 together form an independent set
            if independent_colors(graph, c1_vertices, c2_vertices):
                 # temporarily color all c2 vertices with c1
                 recolor(ordered_col, c2_vertices, c1)
                 echo("\t\t",list(ordered_col[v] for v in c2_vertices))
                 #assert same_color(ordered_col, c2_vertices, c1)
                 #assert same_color(ordered_col, c1_vertices, c1)
                 # check if merge would be p-centered
                 is_p_centered, _ = check_tree_depth(graph, graph, ordered_col,
                                                     p)
                 echo("\t\t", is_p_centered, _)
                 if is_p_centered:
                     # merge the vertices of c2 into c1
                     c1_vertices |= c2_vertices
                     c2_vertices.clear()
                     echo("\t\tNew c1:", c1_vertices)
                 else:
                     # restore the c2 vertices to their original color
                     echo("\t\tNot", p+1, "centered")
                     recolor(ordered_col, c2_vertices, c2)
                     #assert same_color(ordered_col, c2_vertices, c2)
            else:
                echo("\t\tDependent")
    # ensure the final coloring has no unused colors
    c_idx = 0
    final_coloring = Coloring()
    for v_set in color_sets:
        echo(v_set)
        if len(v_set) > 0:
            recolor(final_coloring, v_set, c_idx)
            c_idx += 1
        else:
            echo("skipped")
    return final_coloring
    

def write_coloring(cols, output):
    print "Writing result to {0}".format(output)
    f = open(output, 'w')
    for v in cols:
        f.write(str(v)+': '+str(cols[v])+'\n')
    f.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("graph", help="A graph in any supported format "
                        "(see graphformats.py)")
    parser.add_argument("colors", help="A vertex coloring file")
    parser.add_argument("p", help="the number of color classes that yield "
                        "low-td components, i.e. the coloring is (p+1)-"
                        "centered coloring",
                        type=int)
    args = parser.parse_args()

    graph = load_graph(args.graph)
    remove_loops(graph)

    cols = load_coloring(args.colors)
    p = args.p

    print "Loaded {0} and coloring {1} ({2} colors)".format(args.graph,
                                                            args.colors,
                                                            len(cols))
    res = cols.is_proper(graph) and check_tree_depth(graph, graph, cols, p)
    print "{0}-centered coloring: {1}".format(p+1, res)
    print ""

    optcols = merge_colors(graph, cols, p)
    size = len(optcols)
    print "Best coloring found has size", size
    print "Paranoia-check: ",
    is_p_centered,_ = check_tree_depth(graph, graph, optcols, p)
    if optcols.is_proper(graph) and is_p_centered:
        print "Yes! All is good!"
        write_coloring(optcols, args.colors + ".opt")
    else:
        print "Oh nooooooo!"
