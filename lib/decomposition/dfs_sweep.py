#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


import sys
from copy import copy

from decomp_generator import DecompGenerator
from lib.util.recordtype import *
from lib.graph.td_decomposition import TDDecomposition


class DFSSweep(DecompGenerator):

    # max: number of vertices in graph
    # current_depth: Number of colors we are looking at (0 indexed, so 0 is 1st
    #     color, -1 is no color)
    # colors_in_combi: set containing colors that we are currently processing
    # component_store: A stack of dictionaries for reverse component lookups
    # wscolorlist: A list of WCSColors (one for each color used to color our
    #     parent graph G
    # union_find: A stack of union find structures for fast merging of
    #     components

    # union find structure:
    # every vertex stores information in one mint64
    # every mint64 contains following bits:
    # ------------------------------------------
    # |                 parent index |  type   |
    # |           number of vertices |  type   |
    # ------------------------------------------
    # |      ... |  5 |  4 |  3 |  2 |  1 | 0  |
    # ------------------------------------------
    #
    # type can be
    #      00 = the vertex will be ignored (the color is not in the
    #           combination)
    #      01 = the vertex is a root in a connected component (stores number of
    #           vertices)
    #      10 = the vertex is a child (the parent-bits are used)

    WCSData = recordtype('WCSData', 'max current_depth colors_in_combi '
                         'component_store wscolorlist union_find')

    # number: Number of vertices of this color
    # nodes: A set of vertices that have this color
    WCSColor = recordtype('WCSColor', 'number nodes')

    UFS_TYPE_MASK = 0b11  # Mask for determining if vertex is root or child
    UFS_TYPE_ROOT = 0b01  # Constant for type root
    UFS_TYPE_CHILD = 0b10  # Constant for type child

    def __iter__(self):
        """
        Return an iterator based on size of color sets we are looking at

        :return: An iterator for decompositions
        """

        return self.induced_color_components()

    def walk_color_space(self):
        """
        A function that walks our color space using a
        recursive helper function.
        """

        # Make a WCSData recordtype to store information about
        # components
        data = self.WCSData(
            max=self.G.get_max_id(),
            current_depth=-1,
            colors_in_combi=set(),
            component_store=[],
            wscolorlist={},
            union_find=[]
        )

        # Make a new recordtype for each color in our graph
        for color in self.coloring.usedcols:
            data.wscolorlist[color] = self.WCSColor(
                number=0,
                nodes=set()
            )

        # Record which vertices belong to what
        # color. Also record their count
        for v in self.G:
            data.wscolorlist[self.coloring[v]].number += 1
            data.wscolorlist[self.coloring[v]].nodes.add(v)

        # Generate components by recursively walking through color space
        for component in self.recursive_walk(data,
                                             list(self.coloring.usedcols)):
            yield component

    def recursive_walk(self, data, colors, index_of_last=-1):
        """
        Method to help walk through color space

        :param data: The WCSData object
        :param colors: A list of all colors used for coloring G
        :param index_of_last (optional): Keeps track of index of last
                color added to combination

        """
        # Check to see if we are at p-1 colors, if so generate all combinations
        # with added pth color
        if len(data.colors_in_combi) == self.p - 1:
            for color in colors[index_of_last + 1:]:
                # Add color to stack
                self.add(data, color)
                # Generate components with added color and yield them

                # If the verbose flag is provided
                if self.verbose:
                    sys.stdout.write("\t"+str(data.colors_in_combi)+"\n")

                # Before yielding components with this color set, run all the
                # callbacks in our before_color_set list.
                for fn in self.before_color_set:
                    fn(data.colors_in_combi)

                # Yield components in order to generate TDDs
                for c in self.component_generator(data):
                    yield c

                # After yielding components with this color set, run all the
                # callbacks in our after_color_set list.
                for fn in self.after_color_set:
                    fn(data.colors_in_combi)
                # Pop color from stack since we don't need it
                self.remove(data, color)
        else:
            # We need a separate last index for the recursive call
            # which will be incremented for each color we add
            last_index = index_of_last
            # For every remaining color in the list add and process
            for color in colors[index_of_last + 1:]:
                last_index += 1
                # At this point we are not looking at sets that have
                # less than td_H elements
                self.add(data, color)
                if len(data.colors_in_combi) >= self.td_H:
                    # Generate components with added color and yield them

                    # If the verbose flag is provided
                    if self.verbose:
                        sys.stdout.write("\t"+str(data.colors_in_combi)+"\n")

                    # Before yielding components with this color set, run all
                    # the callbacks in our before_color_set list.
                    for fn in self.before_color_set:
                        fn(data.colors_in_combi)

                    # Yield the components to generate decompositions
                    for c in self.component_generator(data):
                        yield c

                    # After yielding components with this color set, run all
                    # the callbacks in our after_color_set list.
                    for fn in self.after_color_set:
                        fn(data.colors_in_combi)

                # Call this method again to add additional color to stack
                for component in self.recursive_walk(data, colors, last_index):
                    yield component

                # Pop the last color
                self.remove(data, color)

    def ufs_find(self, ufs, node):
        """
        Find operation for our union find structure

        Find the root of a vertex in our union find structure
        Implementation used from check_tree_depth.py

        :param ufs: The union-find structure
        :param node: The node whose root we are trying to find
        """

        # Save a copy of our node since we want to do path compression
        save = node
        depth = 0
        # traverse through the tree up until we find a root
        # while (ufs_isChild(ufs, node)):
        while (ufs[node] & self.UFS_TYPE_MASK) == self.UFS_TYPE_CHILD:
            node = (ufs[node] >> 2)  # ufs_getParent(ufs, node)
            depth += 1

        # If our original node was a child, make it point to
        # its farthest parent (root) for finding it faster the next time
        if ((ufs[save] & self.UFS_TYPE_MASK) == self.UFS_TYPE_CHILD and
                depth > 1):  # (ufs_isChild(ufs, save)):
            # ufs[save] = ufs_setParent(ufs, save, node)
            ufs[save] = self.UFS_TYPE_CHILD | (node << 2)

        # return our root
        return node

    def print_union_find(self, ufs):
        """
        A nice representation for our union find structure.
        Useful for debugging.

        :param ufs: The union find structure that we want to print

        """

        ufs_str = "["
        # For each entry
        for idx, entry in enumerate(ufs):
            # Ignore this entry
            if entry == 0:
                ufs_str += 'none'
            # This is a root, print -> vertex r - num vertices in component
            elif entry % 2 != 0:
                ufs_str += str(idx) + 'r - ' + str(entry >> 2)
            # This is a child, print -> vertex cof(child of) root
            else:
                ufs_str += str(idx) + ' cof ' + str(self.ufs_find(ufs, idx))
            # Add a comma after each entry
            ufs_str += ', '
        # Cut out extra ', ' at the end and add closing bracket
        print '\n' + ufs_str[0: len(ufs_str) - 2] + ']' + '\n'

    def remove(self, data, color):
        """
        Remove a color from the current combination

        :param data: The WCSData object
        :param color: The color we want to remove

        """

        # Drop one level
        data.component_store.pop()
        # We are done processing 'color', so remove it
        data.colors_in_combi.remove(color)
        # Drop one level in the union find
        data.union_find.pop()
        # Decrease current depth by 1
        data.current_depth -= 1

    def alt_component_generator(self, data):
        """
        An alternate implementation for generating components which is
        memory efficient

        :param data: WCSData
        :return: A generator for components

        """

        # Initialize an empty dictionary to store the components
        comps = []

        # Build the dictionary
        ufs = data.union_find[data.current_depth]
        for idx, elem in enumerate(ufs):
            # Ignore this element
            if elem == 0:
                continue
            # This is a root, so make new dictionary entry for this root
            elif elem % 2 != 0:                    
                # Flexible  comps[idx] = {idx}
                if idx >= len(comps):
                    comps.extend([{x} for x in range(len(comps), idx)])
                    comps.insert(idx,{idx})
            # This is a child, find its root, and add to appropriate set
            else:
                root = self.ufs_find(ufs, idx)
                # Flexible  comps[root] = {root}
                if root >= len(comps):
                    comps.extend([{x} for x in range(len(comps), root)])
                    comps.insert(root, {root})

                comps[root].add(idx)

        # Generate components while also pruning ones we don't need
        for item in comps:
            if not self.prune(item, self.multi_pat_min_p):
                yield item

    def component_generator(self, data):

        """
        Generator for components at current level

        :param data: The WCSData object
        :return A generator for components at current_depth in data

        """
        # Get the dictionary at the current depth
        comps_at_level = data.component_store[data.current_depth]
        # Iterate over its keys to get all components
        for component in comps_at_level.itervalues():
            # Prune component if it has less than p vertices
            if not self.prune(component, self.multi_pat_min_p):
                yield component

    def add(self, data, color):
        """
        Add one color to the color combination and find all new
        connected components using a union find data structure

        :param G: The parent graph
        :param data: The WCSData object
        :param color: The color to add

        """
        # Add the color to the combination
        data.colors_in_combi.add(color)
        # Increment current depth since we have added a color
        data.current_depth += 1
        # Find how many vertices we have
        n = data.max + 1
        # If we are at looking at the first color
        if data.current_depth == 0:
            # Make a ufs structure and initialize it with 0s
            ufs = [0] * n

            # Initialize a component store to store our components
            # Components are stored as sets in a dictionary
            comps = {}

            # For all the vertices of that color
            for v in data.wscolorlist[color].nodes:
                # Initialize the union find entry
                # Make each vertex a root
                ufs[v] = (1 << 2) | self.UFS_TYPE_ROOT
                # Since each vertex is a component by itself
                # Make a set containing only v and add it to the dictionary
                comps[v] = frozenset([v])

        # We are looking at at least two colors
        else:
            # Copy the previous dictionary of components
            comps = copy(data.component_store[data.current_depth - 1])
            # Copy the previous union find structure
            ufs = copy(data.union_find[data.current_depth - 1])
            # Initialize new colors in the UFS and comps dictionary
            for v in data.wscolorlist[color].nodes:
                ufs[v] = (1 << 2) | self.UFS_TYPE_ROOT
                comps[v] = frozenset([v])

            for v in data.wscolorlist[color].nodes:
                # For each newly added vertex, find its neighbors
                # and check to see if it already belongs to some component
                for u in self.G.neighbours(v):
                    if self.coloring[u] in data.colors_in_combi:
                        root1 = self.ufs_find(ufs, v)
                        root2 = self.ufs_find(ufs, u)
                        if root1 != root2:
                            # Get the UFS entries of these roots
                            ufs_root1 = ufs[root1]
                            ufs_root2 = ufs[root2]
                            # Find which root to append to and which root gets
                            # appended.  'a' is the one that 'd' will be
                            # appended to.
                            a, d = (root1, root2) if ((ufs_root1 >> 2) >
                                                      (ufs_root2 >> 2)) \
                                else (root2, root1)

                            # Increment the count of vertices in 'a'
                            total_count = (ufs_root1 >> 2) + (ufs_root2 >> 2)
                            ufs[a] = (total_count << 2) | self.UFS_TYPE_ROOT
                            # Set 'd' as a child of a
                            # union operation (set parent)
                            ufs[d] = self.UFS_TYPE_CHILD | (a << 2)

                            # Move all of "d's" elements to "a"
                            comps[a] |= comps[d]  
                            # Delete key since we don't need it anymore
                            del comps[d]

        # Append the new union find to our stack of union finds
        data.union_find.append(ufs)
        # Append the new component dictionary to our
        # stack of component dictionaries
        data.component_store.append(comps)

    def induced_color_components(self):

        def buildTDD(vertices, colorClasses, decomp, parent=None):
            """
            Creates a treedepth decomposition for the subtree rooted at parent
            Arguments:
                vertices (iterable):
                    Vertices that have yet to be assigned a level in the
                    decomposition
                colorClasses (dict):
                    Dictionary mapping a color to a set of vertices that have
                    that color
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
                    # it is the center, so build tdDecomposition without making
                    # recursive calls
                    decomp.update_parent_child(some_vertex, parent)
                    vertices.remove(some_vertex)
                    decomp.update_parent_children(vertices, some_vertex)
                # not the center
                else:
                    # delete entry in dictionary for the color of that vertex,
                    # which leaves us with the color of the center
                    del component_color_freqs[self.coloring[some_vertex]]
                    # get that vertex to add to the decomposition
                    vertex = (colorClasses[component_color_freqs.keys()[0]] &
                              vertices).pop()
                    decomp.update_parent_child(vertex, parent)
                    vertices.remove(vertex)
                    decomp.update_parent_children(vertices, vertex)

            else:
                # find a center for this subtree
                for color, v_set in colorClasses.iteritems():
                    remainingInColor = vertices & v_set
                    # if the color is a center
                    if len(remainingInColor) == 1:
                        nextVertices = vertices - remainingInColor
                        v = remainingInColor.pop()
                        # update parent/child relations
                        decomp.update_parent_child(v, parent)
                        for comp in decomp.get_components(nextVertices):
                            # recursively build the decomposition in the
                            # subtrees
                            buildTDD(comp, colorClasses, decomp, v)
                        # stop searching
                        break
                    # if we are at the root of the decomposition, we should
                    # save it
            if parent is None:
                return decomp
        # For each component yielded by walk_color_space
        for component in self.walk_color_space():
            # Computer color classes
            colorClasses = self.G.get_color_classes(component, self.coloring)
            # Make a new set since we don't want to alter the one in our
            # component store
            vertices = set(component)
            # Make a new TDDecomposition object
            decomposition = TDDecomposition.fromSubgraph(self.G, vertices,
                                                         self.coloring)
            # Yield the tree depth decomposition for this component
            yield buildTDD(vertices, colorClasses, decomposition)
