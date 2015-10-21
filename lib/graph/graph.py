#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#


import sys
import pickle
import argparse
import itertools
import operator
from collections import defaultdict
import hashlib


def generate_palette(cols):
    import numpy as np
    import matplotlib

    tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14),
                 (255, 187, 120), (44, 160, 44), (152, 223, 138),
                 (214, 39, 40), (255, 152, 150), (148, 103, 189),
                 (197, 176, 213), (140, 86, 75), (196, 156, 148),
                 (227, 119, 194), (247, 182, 210), (127, 127, 127),
                 (199, 199, 199), (188, 189, 34), (219, 219, 141),
                 (23, 190, 207), (158, 218, 229)]
    for i in range(len(tableau20)):
        r, g, b = tableau20[i]
        tableau20[i] = (r / 255., g / 255., b / 255.)

    LinL = np.array(tableau20)
    if cols < len(LinL):
        return LinL

    assert False  # Need to implement upsampling...

    b3 = LinL[:, 2]  # value of blue at sample n
    b2 = LinL[:, 2]  # value of blue at sample n
    b1 = np.linspace(0, 1, len(b2))  # position of sample n-ranges from 0 to 1

    # setting up columns for list
    g3 = LinL[:, 1]
    g2 = LinL[:, 1]
    g1 = np.linspace(0, 1, len(g2))

    r3 = LinL[:, 0]
    r2 = LinL[:, 0]
    r1 = np.linspace(0, 1, len(r2))

    # creating list
    R = zip(r1, r2, r3)
    G = zip(g1, g2, g3)
    B = zip(b1, b2, b3)

    # transposing list
    RGB = zip(R, G, B)
    rgb = zip(*RGB)
    # print rgb

    # creating dictionary
    k = ['red', 'green', 'blue']
    LinearL = dict(zip(k, rgb))
    return matplotlib.colors.LinearSegmentedColormap('tab20', LinearL)


class Coloring(object):
    def __init__(self):
        """ Initialize this Coloring object """
        self.color = {}
        self.usedcols = set()

    def __getitem__(self, v):
        """ Defining __getitem__ lets you """
        return self.color[v] if v in self.color else None

    def __contains__(self, v):
        """ Check if color v is in the set of colors used in the coloring"""
        return v in self.color

    def __setitem__(self, v, col):
        self.usedcols.add(col)
        self.color[v] = col

    def __len__(self):
        """ Lets you call len(obj) on the coloring object """
        return len(self.usedcols)

    def __iter__(self):
        """
        :return: returns an iterator for the coloring
        """
        return iter(self.color)

    def colors(self):
        """
        :return:Return colors used
        """
        return set(self.usedcols)

    def real_colors(self):
        """
        Map integers (colors used) to actual colors (rgb colors) and return
        a list of those colors
        :return: the list of actual colors
        """
        pal = generate_palette(len(self.usedcols))
        return map(lambda x: pal[self.color[x]], self.color)

    def select(self, colors, vertices=None):
        """
        Given specific colors, yield all vertices that have those colors

        :param colors: The colors we want to look at
        :param vertices: (optional) If want to look at only specific vertices
        :return: A generator for vertices
        """
        cols = set(colors)
        if vertices is None:
            vertices = self.color

        for v in vertices:
            if self.color[v] in cols:
                yield v

    def frequencies(self, vertices=None):
        """
        Find out and return the frequencies of colors given specific
        colored vertices. If no vertices are specified, return frequencies of
        colors in the coloring of our graph

        :param vertices: Vertices whose color frequencies are to be computed
        :return: A dict where keys are colors and values are their frequencies
        """
        freqs = {}
        if vertices is None:
            vertices = self.color

        for v in vertices:
            col = self.color[v]
            if col not in freqs:
                freqs[col] = 0
            freqs[col] += 1
        return freqs

    def __eq__(self, other):
        """
        Check to see if two colorings are the same
        """
        if other is None:
            return False
        if self.usedcols != other.usedcols:
            return False
        for v in self.color:
            if v not in other.color:
                return False
            if self.color[v] != other.color[v]:
                return False
        return True

    def is_proper(self, graph):
        """
        Make sure each vertex in the graph has a color and no
        two adjacent vertices (connected by an edge) have the same
        color

        :param graph: The graph we want to check
        :return: True if the graph has a proper coloring, False otherwise
        """
        for v in graph:
            if v not in self.color:
                raise Exception("Missing color for vertex " + str(v))
        for s, t in graph.edges():
            if s != t and self.color[s] == self.color[t]:
                return False
        return True

    def normalize(self):
        """
        Normalize this coloring based on color frequency
        :return: A normalized coloring
        """
        res = Coloring()
        # Sort color by frequencies: most common colors get lower indices
        freq = self.frequencies()
        order = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
        indices = {}
        for i, (col, freq) in enumerate(order):
            indices[col] = i
        for v in self.color:
            res[v] = indices[self.color[v]]

        return res

    # For memoization
    def __str__(self):
        return str(hash(frozenset(self.color.items())))

    def __reduce__(self):
        """ Used for pickling """
        lst = [type(self)]

        for v in self.color:
            lst.extend((v, self.color[v]))

        return (coloring_from_pickle, (lst,))


def coloring_from_pickle(lst):
    """ Load a coloring from pickle """
    cls = lst.pop(0)  # load class object
    c = Coloring()

    while lst:
        v = lst.pop(0)
        c[v] = lst.pop(0)

    return c


class Graph(object):
    def __init__(self):
        """ Initialize the graph object """
        self.adj = []
        self.nodes = set()

    def __contains__(self, u):
        """
        Check to see if vertex u is in our graph
        """
        return u in self.nodes

    def __iter__(self):
        """ An iterator for the graph's nodes """
        return iter(self.nodes)

    def __len__(self):
        """ Calling len(graph) will return the number of nodes in it """
        return len(self.nodes)

    def get_max_id(self):
        """ Return the maximum id """
        return max(self.nodes)

    def edges(self):
        """
        A generator for edges in the graphs
        Edges are returned as 2-tuples

        """
        for u in self:
            for v in self.adj[u]:
                if u <= v:
                    yield (u, v)

    def num_edges(self):
        """ Return the count of edges in the graph """
        return sum(1 for _ in self.edges())

    def add_node(self, u):
        """ Add a node to the graph """
        self.nodes.add(u)

    def add_nodes_from(self, u):
        """ Add multiple nodes to the graph """
        self.nodes.update(u)

    def add_edge(self, u, v):
        """
        Add an edge to the graph

        :param u: First vertex in edge
        :param v: Second vertex in edge

        """
        self.nodes.add(u)
        self.nodes.add(v)

        if u < len(self.adj):
            self.adj[u].add(v)
        else:
            self.adj.extend([set() for x in range(len(self.adj), u + 1)])
            self.adj[u].add(v)

        if v < len(self.adj):
            self.adj[v].add(u)
        else:
            self.adj.extend([set() for x in range(len(self.adj), v + 1)])
            self.adj[v].add(u)

    def remove_edge(self, u, v):
        """
        Remove an edge from the graph

        :param u: Vertex 1 in edge
        :param v: Vertex 2 in edge

        """
        if u < len(self.adj):
            self.adj[u].discard(v)
        if v < len(self.adj):
            self.adj[v].discard(u)

    def remove_loops(self):
        """
        Remove edges that loop to the same vertex

        """
        for v in self:
            self.remove_edge(v, v)

    def adjacent(self, u, v):
        """
        Check to see if two vertices are joined by an edge
        :param u: first vertex
        :param v: second vertex
        :return: True if adjacent, False otherwise
        """
        return v in self.adj[u]

    def neighbours(self, u):
        """
        Return the neighbors of a vertex

        :param u: The vertex whose neighbors are to be returned
        :return: A frozenset of containing neighbors of the vertex
        """
        return self.adj[u]

    def neighbours_set(self, centers):
        """
        Given a set of vertices, find all their neighbors

        :param centers: The vertices whose neighbors we want
        :return: The set of neighbors

        """
        res = reduce(lambda x, y: x | self.neighbours(y), centers, set())
        # for v in centers:
        #    res = res | self.neighbours(v)
        return (res - centers)

    def degree(self, u):
        """
        Return the degree of a vertex i.e. the number
        of outgoing edges it has.

        :param u: The vertex
        :return: The degree of the vertex
        """
        return len(self.adj[u])

    def degree_sequence(self):
        """
        Return a list containing the degree of each node

        :return: the degree sequence
        """
        return [self.degree(u) for u in self.nodes]

    def degree_dist(self):
        """
        Compute and return the degree distribution.

        :return: A dictionary where degrees are keys and
                 number of vertices with that degree are values
        """
        res = []
        for u in self.nodes:
            res.extend([0 for x in range(len(res), u + 1)])
            res[self.degree(u)] += 1
        return res

    def cum_degree_dist(self):
        """
        Cumulative degree distribution of the vertices

        :return: A dictionary where:
            keys: vertices
            values: sum of all degrees of vertices with id less than
                    or equal to the id of the vertex (key)
        """
        i = 1
        total = 0
        dd = self.degree_dist()
        n = len(self)
        res = [dd[0]]
        while total < n:
            total = res[i - 1] + dd[i]
            res.append( total )
            i = i + 1
        return res

    def calc_average_degree(self):
        """
        The average degree of the graph
        :return: the average degree
        """

        num_edges = len([e for e in self.edges()])
        return float(2 * num_edges) / len(self.nodes)

    def calc_degeneracy(self):
        """
        Calculates the degeneracy of the graph
        :return: The degeneracy of the graph
        """

        degbuckets = []
        degrees = []
        degen = 0
        mindeg = n = len(self)
        removed = set()
        for v in self:
            deg = self.degree(v)
            mindeg = min(mindeg, deg)
            degbuckets.extend([set() for x in range(len(degbuckets), deg + 1)])
            degbuckets[deg].add(v)
            degrees.extend([set() for x in range(len(degrees), v + 1)])
            degrees[v] = deg

        while len(removed) < n:
            while not degbuckets[mindeg]:
                mindeg += 1
            v = iter(degbuckets[mindeg]).next()
            degbuckets[mindeg].remove(v)
            removed.add(v)
            degen = max(degen, mindeg)

            for w in self.neighbours(v):
                if w in removed:
                    continue
                deg = degrees[w]
                degrees[w] -= 1
                degbuckets[deg].remove(w)
                degbuckets[deg - 1].add(w)
                mindeg = min(mindeg, deg - 1)

        return degen

    def subgraph(self, vertices):
        """
        Given a set of vertices, returns the subgraph
        that the vertices induce on the graph

        :param vertices: vertices in the subgraph
        :return: the induced subgraph
        """
        res = Graph()
        selected = set(vertices)
        for v in self:
            if v in selected:
                res.add_node(v)

        for u, v in self.edges():
            if u in selected and v in selected:
                res.add_edge(u, v)
        return res

    def normalize(self):
        """
        Returns graph with node indices from 0 to n-1 and
        a mapping dictionary to recover the original ids

        """
        res = Graph()
        backmapping = dict(enumerate(self))
        mapping = {k: v for (v, k) in backmapping.iteritems()}

        for u in self:
            res.nodes.add(mapping[u])
        for u, v in self.edges():
            res.add_edge(mapping[u], mapping[v])

        return res, backmapping

    @staticmethod
    def generate(name):
        res = Graph()

        # Ki, Pi, Ci
        t = name[0]
        if t in ['K', 'P', 'C']:
            if t == 'K':
                parts = map(int, name[1:].split(','))
                if len(parts) == 1:
                    size = parts[0]
                    for x, y in itertools.combinations(xrange(0, size), 2):
                        res.add_edge(x, y)
                else:
                    print "Generating", name
                    indices = []
                    size = 0
                    for s in parts:
                        indices.append((size, size + s))
                        size += s
                    for a, b in itertools.combinations(xrange(0, len(parts)),
                                                       2):
                        for x in xrange(indices[a][0], indices[a][1]):
                            for y in xrange(indices[b][0], indices[b][1]):
                                res.add_edge(x, y)

            elif t == 'P' or t == 'C':
                size = int(name[1:])
                for x in xrange(0, size - 1):
                    res.add_edge(x, x + 1)
                if t == 'C':
                    res.add_edge(size - 1, 0)

            return res

        raise Exception("Unknown name " + name)

    # For memoization
    def __str__(self):
        return graph_hash(self)

    def __reduce__(self):
        """ Used for pickling the graph """
        lst = []
        lst.append(type(self))

        for u, v in self.edges():
            lst.append(u)
            lst.append(v)

        return (graph_from_pickle, (lst,))

    def get_components(self, vertices=None):
        """
        Given a set of vertices, find the ones that are connected
        and return the connected components

        :param vertices: The set of vertices to generate connected
                         components from
        :return: A generator for the connected components
        """
        if vertices is None:
            vertices = set(self.nodes)
        else:
            vertices = set(vertices)

        # While we have more vertices to look at
        while vertices:
            # Pop a vertex at random and make a set containing that vertex
            comp = {vertices.pop()}
            # Find its neighbors that are also in 'vertices'
            exp = self.neighbours_set(comp) & vertices
            # While we have more neighbors
            while exp:
                # Add those vertices to our component
                comp.update(exp)
                # Compute new neighbors
                exp = self.neighbours_set(comp) & vertices
            # We found a component, delete those vertices from original
            # set of vertices
            vertices = vertices - comp
            # Yield the component
            yield comp

    def get_color_classes(self, vertices, coloring):
        """
        Given a coloring and a set of vertices, create a mapping of
        colors and vertices that are colored those colors.

        :param vertices: The set of vertices
        :param coloring: A coloring of the vertices
        :return: A dictionary where,
                 keys: colors
                 values: set of vertices colored that color (key)
        """
        # Make a dictionary with colors as keys and empty sets as values
        colorClasses = {coloring[v]: set() for v in vertices}
        # Populate the values
        for vertex in vertices:
            colorClasses[coloring[vertex]].add(vertex)
        # Return our dictionary
        return colorClasses


def graph_from_pickle(lst):
    """ Make a new graph from pickle """
    cls = lst.pop(0)  # load class object
    g = Graph()

    while lst:
        u = lst.pop(0)
        g.add_edge(u, lst.pop(0))

    return g


class TFGraph(object):
    def __init__(self, nodes):
        """ Initialize a TFGraph object """
        self.nodes = nodes
        self.inarcs = defaultdict(dict)
        self.inarcs_weight = defaultdict(lambda: defaultdict(set))

    def __contains__(self, u):
        """ Checks to see if vertex u is a node in the graph"""
        return u in self.nodes

    def __len__(self):
        """ Returns number of nodes in graph """
        return len(self.nodes)

    def __iter__(self):
        """ An iterator for the graph's nodes """
        return iter(self.nodes)

    def add_node(self, u):
        """ Add a node to the graph """
        self.nodes.add(u)

    def add_arc(self, u, v, weight):
        """ Add an arc to the graph with the given weight """
        self.inarcs[v][u] = weight
        self.inarcs_weight[v][weight].add(u)

    def remove_arc(self, u, v):
        """
        Remove the arc between vertices u and v from the graph,
        if one exists
        """
        if u not in self.inarcs[v]:
            return
        weight = self.inarcs[v][u]
        del self.inarcs[v][u]
        self.inarcs_weight[v][weight].remove(u)
        assert not self.adjacent(u, v)

    def arcs(self):
        """ Return a generator for the arcs in the graph"""
        for u in self:
            for v, weight in self.in_neighbours(u):
                yield (v, u, weight)

    def edges(self):
        """ For compatibility reasons (coloring etc.) """
        for u in self:
            for v, _ in self.in_neighbours(u):
                yield (v, u)

    def weight(self, u, v):
        """ Return the weight of arc uv """
        return self.inarcs[v][u] if u in self.inarcs[v] else None

    # Returns whether the arc uv exists
    def adjacent(self, u, v):
        return u in self.inarcs[v]

    def in_neighbours(self, u):
        """Return the in_neighbors of u"""
        inbs = self.inarcs[u]
        for v in inbs:
            yield v, inbs[v]

    def in_neighbours_weight(self, u, weight):
        """ Return weight of """
        inbs = self.inarcs_weight[u][weight]
        for v in inbs:
            yield v

    def in_degree(self, u):
        """ Return the in-degree of vertex u"""
        return len(self.inarcs[u])

    def in_degree_weight(self, u):
        res = {}
        for weight in self.inarcs_weight[u]:
            res[weight] = len(self.inarcs_weight[u][weight])
        return res

    def undirected(self):
        """ Returns an undirected copy """
        res = Graph()
        for v in self.nodes:
            res.nodes.add(v)  # For degree-0 nodes!
        for u, v, _ in self.arcs():
            res.add_edge(u, v)
        return res

    def trans_trips(self, u):
        """ Returns transitive triples (x, u, weightsum) """
        inbs = frozenset(self.inarcs[u].items())
        for (y, wy) in inbs:
            for x, wx in self.in_neighbours(y):
                if not self.adjacent(x, u):
                    yield (x, u, wx + wy)

    def trans_trips_weight(self, u, weight):
        """
        Returns transitive triples (x, y, weightsum) whose weightsum
        is precisely 'weight'
        """
        for wy in xrange(1, weight):
            wx = weight - wy
            inbs = frozenset(self.inarcs_weight[u][wy])
            for y in inbs:
                for x in self.in_neighbours_weight(y, wx):
                    if not self.adjacent(x, u):
                        yield (x, u, weight)

    def frat_trips(self, u):
        """ Returns fraternal triples (x, y, weightsum) """
        inbs = frozenset(self.inarcs[u].items())
        for (x, wx), (y, wy) in itertools.combinations(inbs, 2):
            if not (self.adjacent(x, y) or self.adjacent(y, x)):
                yield (x, y, wx + wy)

    def frat_trips_weight(self, u, weight):
        """
        Returns fraternal triples (x, y, weightsum) whose weightsum
        is precisely 'weight'

        Since we draw all vertices from the same in-neighbourhood,
        the considered sets have usually different weights and
        are thus disjoint. Only for even weights do we have to consider
        the slightly annoying case of (weight/2, weight/2).
        """
        wh = (weight + 1) / 2
        for wx in xrange(1, wh):
            wy = weight - wx
            for x in self.in_neighbours_weight(u, wx):
                for y in self.in_neighbours_weight(u, wy):
                    if not (self.adjacent(x, y) or self.adjacent(y, x)):
                        yield (x, y, weight)

        if weight % 2 == 0:
            wy = wx = weight / 2
            inbs = frozenset(self.inarcs_weight[u][wh])
            for x, y in itertools.combinations(inbs, 2):
                if not (self.adjacent(x, y) or self.adjacent(y, x)):
                    yield (x, y, weight)

    # For memoization
    def __str__(self):
        return graph_hash(self)

    def __reduce__(self):
        """ Used for pickling a tfgraph"""
        lst = []
        lst.append(type(self))
        # Store nodes
        lst.append(len(self))
        for u in self:
            lst.append(u)

        # save every arc & weight
        for u, v, weight in self.arcs():
            lst.append(u)
            lst.append(v)
            lst.append(weight)

        return (tfgraph_from_pickle, (lst,))


def tfgraph_from_pickle(lst):
    """ Load a tfgraph from pickle """
    cls = lst.pop(0)
    nodes = []
    n = int(lst.pop(0))
    for i in xrange(n):
        nodes.append(lst.pop(0))

    g = TFGraph(nodes)

    while lst:
        u = lst.pop(0)
        v = lst.pop(0)
        g.add_arc(u, v, lst.pop(0))

    return g


def from_networkx(nxgraph):
    """Make a graph object given a networkx graph """
    import networkx as nx

    if isinstance(nxgraph, nx.Graph):
        res = Graph()
        for v in nxgraph.nodes():
            res.add_node(v)
        for u, v in nxgraph.edges():
            res.add_edge(u, v)
        return res
    elif isinstance(nxgraph, nx.DiGraph):
        res = TFGraph()
        for v in nxgraph.nodes():
            res.add_node(v)
        for u, v in nxgraph.edges():
            res.add_arc(u, v)
        return res
    raise Exception('Unsupported networkx graph type.')


def graph_hash(g):
    """ Compute the hash for a graph"""
    if isinstance(g, TFGraph):
        deg = defaultdict(int)
        for v in g:
            indegs = g.in_degree_weight(v)
            for w in indegs:
                deg[(indegs[w], w)] += 1
        m = hashlib.md5()
        for d in sorted(deg.keys()):
            m.update(str(deg[d] ** (d[0] * d[1])))
        return m.hexdigest()
    elif isinstance(g, Graph):
        deg = defaultdict(int)
        for v in g:
            deg[g.degree(v)] += 1
        m = hashlib.md5()
        for d in sorted(deg.keys()):
            m.update(str(deg[d] ** d))
        return m.hexdigest()


def show_graph(g, coloring=None, size=None):
    """Plot the graph using matplotlib """

    import matplotlib.pyplot as plt
    from networkx import graphviz_layout
    import networkx as nx
    import numpy

    if size is None:
        size = (10, 10)

    plt.figure(figsize=size)

    if isinstance(g, TFGraph):
        res = nx.DiGraph()
        for v in g:
            res.add_node(v)
        labels = {}
        for s, t, w in g.arcs():
            res.add_edge(s, t)
            labels[(s, t)] = w

        pos = nx.graphviz_layout(res, prog="neato")
        nx.draw(res, pos, node_color='#ffffff',
                edge_color='#cccccc',
                width=1, edge_cmap=plt.cm.Blues, with_labels=True, arrows=True)
        nx.draw_networkx_edge_labels(res, pos, edge_labels=labels)
    if isinstance(g, Graph):
        res = nx.Graph()
        for v in g:
            res.add_node(v)
        for s, t in g.edges():
            res.add_edge(s, t)

        col = '#ffffff' if coloring is None else coloring.real_colors()

        pos = nx.graphviz_layout(res, prog="neato")
        nx.draw(res, node_color=col,
                edge_color='#cccccc',
                width=1, edge_cmap=plt.cm.Blues, with_labels=True,
                arrows=False)
    plt.show()
