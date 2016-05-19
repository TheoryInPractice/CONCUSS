#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import sys
import os
import itertools

from lib.graph.graph import Graph, Coloring
from lib.util.recordtype import *

# Define a record type of information about the vertices
# Attributes:
#     parent:  vertex that is the parent in the decomposition.  None iff vertex
#         is the root
#     children:  list of vertices that are children of this vertex
#     depth:  integer of the depth of the vertex.  Root has depth 0.
VertexInfo = recordtype('VertexInfo', 'parent children depth')


class TDDecomposition(Graph):
    """
    A subclass of Graph with additional data structures to describe a
    treedepth decomposition.

    Attributes:
        maxDepth:  The depth of the decomposition
        vertexRecords:  A dictionary mapping a vertex to its VertexInfo
            record (see above)
        root:  the root of the decomposition
    """

    def __init__(self):
        super(TDDecomposition, self).__init__()
        self.maxDepth = 0
        self.vertexRecords = []
        self.root = None
        self.coloring = None

    @classmethod
    def fromSubgraph(cls, graph, vertices, coloring):
        """
        Creates a TDDecomposition graph object from the subgraph induced on
        vertices.

        Arguments:
            graph:  a Graph object
            vertices:  iterable of vertices of graph
        """
        result = cls()
        selected = set(vertices)
        result.add_nodes_from(selected)
        for v in selected:
            # Add edges from this vertex to each of the ones
            # adjacent to it
            if v < len(result.adj):
                result.adj[v] |= graph.neighbours(v) & selected
            else:
                result.adj.extend([set() for x in range(len(result.adj), v + 1)])
                result.adj[v] |= graph.neighbours(v) & selected
        result.coloring = coloring
        return result

    def update_parent_child(self, v, parent):
        """Sets parent to be parent of v and v to be the child of parent"""
        # print "\t\tupdating %s with parent %s"%(v, parent)
        if parent is None:
            self.root = v
            self.vertexRecords[v].depth = 0
        else:
            self.vertexRecords[v].parent = parent
            self.vertexRecords[parent].children.append(v)
            self.vertexRecords[v].depth = self.vertexRecords[parent].depth + 1
            if self.vertexRecords[v].depth + 1 > self.maxDepth:
                self.maxDepth = self.vertexRecords[v].depth + 1

    def update_parent_children(self, children, parent):
        """
        Sets the parent of all 'children' to 'parent'
        and updates the maxDepth if necessary

        :param children: children
        :param parent: parent
        """
        # Localize vertexRecords for the loop
        vertexRecords = self.vertexRecords
        parent_vertex_record = vertexRecords[parent]
        parent_depth = parent_vertex_record.depth
        # For all children
        for v in children:
            # Set parent
            vertexRecords[v].parent = parent
            # Add child to parent
            parent_vertex_record.children.append(v)
            # Set depth of child
            vertexRecords[v].depth = parent_depth + 1
        # Check if we have new maxDepth
        if parent_depth + 2 > self.maxDepth:
            self.maxDepth = parent_depth + 2

    def add_node(self, u):
        Graph.add_node(self, u)
        self.vertexRecords.extend(
            [None for x in range(len(vertexRecords), u + 1)])
        self.vertexRecords[u] = VertexInfo(parent=None, children=[],
                                           depth=None)

    def add_nodes_from(self, u):
        """Adds an iterable of nodes at once to save time"""
        Graph.add_nodes_from(self, u)
        # Make a local reference to self.vertexRecords for use in the loop
        vertexRecords = self.vertexRecords
        for n in u:
            self.vertexRecords.extend(
                [None for x in range(len(vertexRecords), n + 1)])
            vertexRecords[n] = VertexInfo(parent=None, children=[], depth=None)

    def depth(self, v=None):
        """
        Returns the depth of a vertex.

        Arguments:
            v (vertex, optional): If omitted, the depth of the graph (the
                maximum depth of all vertices) is returned
        """
        if v is None:
            return self.maxDepth
        else:
            return self.vertexRecords[v].depth

    def children(self, v):
        """
        Returns the children of a vertex.

        Arguments:
            v (vertex)
        """
        return self.vertexRecords[v].children

    def parent(self, v):
        """
        Returns the parent of a vertex.

        Arguments:
            v (vertex)
        """
        return self.vertexRecords[v].parent

    def sanityCheck(self):
        """Ensure that the parent-child relationships are consistent."""
        for v in self:
            if self.depth(v) == 0:
                assert self.parent(v) is None, "Root cannot have a parent"
            else:
                assert self.depth(self.parent(v)) == self.depth(v) - 1, \
                    "Vertex %s has depth %d, but its parent has depth %d" % (
                    v, self.depth(v), self.depth(self.parent(v)))
            for c in self.children(v):
                assert self.parent(c) == v, \
                    "Vertex %s claims to be the parent of %s, but %s claims " \
                    "%s to be its parent.  Call Jerry Springer!" % \
                    (v, c, c, self.parent(c))

    def leaves(self):
        """Returns the leaves of the treedepth decomposition"""
        myLeaves = set()
        for v in self:
            if self.hasLeaf(v):
                myLeaves.add(v)
        return myLeaves

    def hasLeaf(self, v):
        """Tests whether v is a leaf of the decomposition"""
        return not self.vertexRecords[v].children

    def rootPath(self, v):
        """
        Find the path from v to the root.
        Arguments:
            v (vertex)
        Return value:
            A list of the vertices in order on the path from the root to v
        """
        assert v in self, "Vertex %s is not in the graph" % (v)
        path = []
        curr = v
        while curr is not None:
            path.append(curr)
            curr = self.vertexRecords[curr].parent
        # put the root at the beginning of the path
        return [i for i in reversed(path)]
