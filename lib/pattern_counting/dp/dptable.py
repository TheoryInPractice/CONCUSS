#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/,
# and is Copyright (C) North Carolina State University, 2015. It is licensed
# under the three-clause BSD license; see LICENSE.
#


from collections import defaultdict


class DPTable(object):
    """
    Dynamic programming table for computing graph isomorphisms.
    See http://arxiv.org/pdf/1406.2587v4.pdf for the algorithm
    and explanations of the table and pattern operations
    """
    def __init__(self, G):
        """
        Create an empty table

        Arguments
                G:  TDDecomposition object
        """
        self.table = defaultdict(lambda: defaultdict(int))
        self.G = G

    def computeLeaf(self, v, pattern1, mem_motif=None):
        """
        Compute table entry for a given leaf and k-pattern

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        patternSum = 0
        # Localize variables and functions for faster lookups
        self_isIsomorphism = self.isIsomorphism
        # Iterate through all patterns that become pattern1 when they forget
        # the depth of v.
        for pattern2 in pattern1.inverseForget(self.G.depth(v), mem_motif):
            patternSum += self_isIsomorphism(v, pattern2, mem_motif)
        # Update appropriate table entry
        self.table[(v,)][pattern1] = patternSum

    def computeInnerVertex(self, v, pattern1, mem_motif=None):
        """
        Compute table entry for a given single non-leaf and k-pattern

        Arguments:
                v:  leaf Vertex
                pattern1:  kPattern
        """
        patternSum = 0
        # Localize variables and functions for faster lookups
        g_ch = self.G.children
        tup = tuple
        self_table = self.table
        # Iterate through all patterns that become pattern1 when they forget
        # the depth of v.
        for pattern2 in pattern1.inverseForget(self.G.depth(v), mem_motif):
            patternSum += self_table[tup(g_ch(v))][pattern2]
        # update appropriate table entry
        self_table[(v,)][pattern1] = patternSum

    def computeInnerVertexSet(self, v_list, pattern1, mem_motif=None):
        """
        Compute table entry for a given set of vertices and k-pattern

        Arguments:
                v_list:  ordered iterable of Vertex
                pattern1:  kPattern
        """
        patternSum = 0
        # Split last vertex from the rest
        v_last = v_list[-1:]
        v_front = v_list[:-1]
        # Localize variables and functions for faster lookups
        self_table = self.table
        # Iterate through all pattern pairs whose join yields pattern1
        for pattern2, pattern3 in pattern1.inverseJoin(mem_motif):
            patternSum += (self_table[v_front][pattern2] *
                           self_table[v_last][pattern3])
        # Update appropriate table entry
        self_table[v_list][pattern1] = patternSum

    def computeInnerVertexSetCleanup(self, leftChildren, mem_motif=None):
        pass

    def lookup(self, v, pattern):
        # if not isinstance(v, tuple):
        #       v_tup = (v,)
        # else:
        #       v_tup = tuple(v)
        return self.table[v][pattern]

    def safeLookup(self, v, pattern):
        """
        Lookup table entry with error handling
        Arguments:
                v:  Vertex or iterable of Vertex
                pattern:  kPattern
        """
        if not isinstance(v, tuple):
            v_tup = (v,)
        else:
            v_tup = tuple(v)
        print "Vertices: ", [str(u) for u in v_tup]
        print "Table"
        for k, c in self.table[v_tup].iteritems():
            print k, c
        try:
            print "Trying"
            t = self.table[v_tup][pattern]
        except KeyError as e:
            print "----------------------------------------------------"
            print [str(u) for u in v_tup]
            print pattern
            print "Table"
            for k, c in self.table[v_tup].iteritems():
                print k, c
            print "----------------------------------------------------"
            raise
        return t

    def __str__(self):
        """Give a string representation of the table"""
        outputString = ""
        for v_tup in sorted(self.table.keys()):
            outputString += "Vertex set: " + \
                            str([str(v) for v in v_tup]) + "\n"
            for pattern, count in sorted(self.table[v_tup].iteritems()):
                if count > 0:
                    outputString += "\t" + str(count) + " at pattern "
                    outputString += str(pattern) + "\n"
        return outputString

    def isIsomorphism(self, v, pattern, mem_motif=None):
        """
        Determine whether the root path is an isomorphism to the boundary of
        the k-pattern

        Arguments:
                v:  vertex
                pattern:  kPattern
        Return value:
                True if the path from the root to v is isomorphic to the
                boundary of the k-pattern
        """
        # Throw away patterns that cannot have isomorphisms
        if (pattern.vertices != pattern.boundaryVertices or
                pattern.numVertices() > self.G.depth(v)+1):
            return False
        if pattern.numVertices() <= 1:
            return True
        P_v = self.G.rootPath(v)

        # Create mapping of vertices of H to vertices of G
        HtoGMap = defaultdict(lambda: None)
        for u, idx in pattern.boundaryIter(pattern):
            try:
                HtoGMap[u] = P_v[idx]
            except IndexError:
                return False
                print pattern.vertices
                print P_v
                raise

        # Create mapping of vertices of G to vertices of H
        # NOTE: not used, so commented out
        # GtoHMap = dict(reversed(i) for i in HtoGMap.iteritems())

        # Ensure the neighborhoods of a vertex and its image are the same
        HinG = frozenset(HtoGMap.itervalues())
        for u in pattern.boundaryVertexIter():
            # Image of u in G
            u_prime = HtoGMap[u]
            # Images in G of the neighbors of u
            N_prime = set()
            for x in pattern.graph.adj[u]:
                N_prime.add(HtoGMap[x])
            N_prime.discard(None)
            if N_prime ^ (self.G.adj[u_prime] & HinG):
                return False
        return True

        # print [(str(v), str(u)) for v, u in HtoGMap.iteritems()]
        # for u1, u2 in itertools.combinations([v for v,
        #                                      i in pattern.boundaryIter()],
        #                                      2):
        #       neighborsInH = u1 in pattern.graph.adj[u2]
        #       neighborsInG = HtoGMap[u1] in self.adj[HtoGMap[u2]]
        #       if not neighborsInH == neighborsInG:
        #               return False
        # return True
