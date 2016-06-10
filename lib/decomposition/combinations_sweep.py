#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import sys
from itertools import combinations

from decomp_generator import DecompGenerator
from lib.graph.td_decomposition import TDDecomposition


class CombinationsSweep(DecompGenerator):

    # Set to store all vertices, given a specific set of colors
    coloredVertices = set()
    # Keys are colors, and values are vertices that are those colors
    colorClasses = {}

    def __iter__(self):
        """
        Return an iterator based on size of color sets we are looking at

        :return: An iterator for decompositions
        """

        return self.induced_color_components()

    def walk_color_space(self):
        """
        Walk color space using Python's built in itertools.combinations
        function.

        :return: Connected components
        """
        for numColors in range(self.p, min(self.td_H, self.p)-1, -1):
            for colorSet in combinations(self.coloring.colors(), numColors):
                # find the components of the graph induced on the color set and
                # create a TD decomposition from the coloring
                # map a color to the vertices of that color
                self.colorClasses = dict((color, set()) for color in colorSet)
                # add the vertices to their corresponding color mappings
                for v in self.G:
                    # print v, coloring[v]
                    try:
                        self.colorClasses[self.coloring[v]].add(v)
                    except KeyError:
                        pass
                # aggregate all the vertices of the colors of interest
                self.coloredVertices = reduce(lambda x, y: x | y,
                                              self.colorClasses.values())

                # If the verbose flag is provided
                if self.verbose:
                    sys.stdout.write("\t"+str(colorSet)+"\n")

                # Processing to be done before we generate components
                for fn in self.before_color_set:
                    fn(colorSet)

                # Yield the component
                for component in self.G.get_components(self.coloredVertices):
                    if not self.prune(component, self.multi_pat_min_p):
                        yield component

                # Processing to be done after we are done generating components
                # for this color set
                for fn in self.after_color_set:
                    fn(colorSet)

    def induced_color_components(self):
        """
        Produces decompositions by walking through color space

        :return: Decomposition given a specific component
        """

        def buildTDD(vertices, colorClasses, decomp, parent=None):
            """
            Creates a treedepth decomposition for the subtree rooted at parent
            Arguments:
                vertices (iterable):
                    Vertices that have yet to be assigned a level in the
                    decomposition.
                colorClasses (dict):
                    Dictionary mapping a color to a set of vertices that have
                    that color.
                parent (vertex, optional):
                    Parent of the subtrees for the remaining vertices.  Should
                    only be set to None when decomp is None.
                decomp (TDDecomposition, optional):
                    Treedepth decomposition being created from the vertices.
                    If None, the function will create a new TDDecomposition for
                    each component.
            """
            component_color_freqs = self.coloring.frequencies(vertices)
            if len(component_color_freqs) == 2:
                # pop some vertex to check
                some_vertex = vertices.pop()
                # add it back because we don't want to lose it
                vertices.add(some_vertex)
                # Check to see if this is the center
                if (component_color_freqs[self.coloring[some_vertex]] == 1):
                    # It is the center, so build tdDecomposition without making
                    # recursive calls
                    decomp.update_parent_child(some_vertex, parent)
                    vertices.remove(some_vertex)
                    decomp.update_parent_children(vertices, some_vertex)
                # Not the center
                else:
                    # Delete entry in dictionary for the color of that vertex,
                    # which leaves us with the color of the center
                    del component_color_freqs[self.coloring[some_vertex]]
                    # Get that vertex to add to the decomposition
                    vertex = (colorClasses[component_color_freqs.keys()[0]] &
                              vertices).pop()
                    # Build tdDecomposition without making recursive calls
                    decomp.update_parent_child(vertex, parent)
                    # Remove the vertex so that we can add the rest of the
                    # vertices as its children in the TDD
                    vertices.remove(vertex)
                    decomp.update_parent_children(vertices, vertex)

            else:
                # Find a center for this subtree
                for color, v_set in colorClasses.iteritems():
                    remainingInColor = vertices & v_set
                    # print "  Vertices " + str(remainingInColor) + \
                    #       " have color " + str(color)
                    # If the color is a center
                    if len(remainingInColor) == 1:
                        nextVertices = vertices - remainingInColor
                        v = remainingInColor.pop()
                        # Update parent/child relations
                        decomp.update_parent_child(v, parent)
                        for comp in self.G.get_components(nextVertices):
                            # Recursively build the decomposition in the
                            # subtrees
                            buildTDD(comp, colorClasses, decomp, v)
                        # stop searching
                        break
                    # If we are at the root of the decomposition, we should
                    # save it
            if parent is None:
                return decomp
        # For each component returned by walk_color_space
        for component in self.walk_color_space():
            # Make a new tree depth decomposition object for the component
            decomposition = TDDecomposition.fromSubgraph(self.G, component,
                                                         self.coloring)
            # Yield the tree depth decomposition built by buildTDD
            yield buildTDD(component, self.colorClasses, decomposition)
