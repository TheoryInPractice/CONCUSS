#!/usr/bin/python
#
# This file is part of CONCUSS, https://github.com/theoryinpractice/concuss/, and is
# Copyright (C) North Carolina State University, 2015. It is licensed under
# the three-clause BSD license; see LICENSE.
#



import sys
import collections
import datetime
from xml.sax.saxutils import quoteattr

from lib.graph.graph import Graph as Graph


class multidict(object):

    def __init__(self):
        self.d = collections.defaultdict(list)

    def __getitem__(self, key):
        if len(self.d[key]) == 1:
            return self.d[key][0]
        return self.d[key]

    def __setitem__(self, key, value):
        if value is None:
            self.d[key] = []
        else:
            self.d[key].append(value)

    def __iter__(self):
        return iter(self.d)

    def __contains__(self, key):
        return key in self.d

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.d)

    def __str__(self):
        res = "{"
        for key in self:
            if len(self.d[key]) == 1:
                res += "{0}: {1}, ".format(key, self.d[key][0])
            else:
                res += "{0}: {1}, ".format(key, self.d[key])
        if len(self) != 0:
            res = res[:-2]
        res += "}"
        return res


def write_gml_data(data):
    print 'graph'
    print '['
    print '  directed 0'
    for d in data['graph']['node']:
        print '  node'
        print '  ['
        for v in d:
            if v == 'ComponentID':
                continue
            if v == 'graphics':
                print '    graphics'
                print '    ['
                for vv in d[v]:
                    print '      {0} {1}'.format(vv, d[v][vv])
                print '    ]'
                continue
            print '    {0} {1}'.format(v, d[v])
        print '  ]'
    for e in data['graph']['edge']:
        print '  edge'
        print '  ['
        for v in e:
            print '    {0} {1}'.format(v, e[v])
        print '  ]'
    print ']'


def read_gml_data(filename):
    stream = []
    for l in open(filename):
        l = l.strip()
        if len(l) == 0:
            continue
        fields = l.split(" ")
        token = lambda: None  # Inline object
        token.name = None
        if len(fields) == 1:
            v = fields[0]
            if v == "[":
                token.type = "BLOCK_START"
            elif v == "]":
                token.type = "BLOCK_END"
            else:
                token.type = "BLOCK_NAME"
                token.name = v
        else:
            token.type = "FIELD"
            token.name = fields[0]
            token.value = "".join(fields[1:])
        stream.append(token)

    data = multidict()
    stack = [data]
    for token in stream:
        current = stack[-1]
        if token.type == "BLOCK_NAME":
            # Start new data block
            block = multidict()
            label = token.name
            current[label] = block
            stack.append(block)
        elif token.type == "BLOCK_START":
            pass
        elif token.type == "BLOCK_END":
            stack.pop()
        elif token.type == "FIELD":
            current[token.name] = token.value
    return data


def read_edgelist(filename):
    graph = Graph()
    for line in open(filename).readlines():
        line = line.strip()
        if line[0] == '#':
            continue
        source, target = line.split()
        s = int(source)
        t = int(target)

        graph.add_edge(s, t)

    return graph


def write_edgelist(graph, ostream, **kwargs):
    sep = '\t'
    if 'separator' in kwargs:
        sep = kwargs['separator']
    offset = 0
    if 'base' in kwargs:
        offset = int(kwargs['base'])

    formstr = "{0}"+sep+"{1}"
    if 'weighted' in kwargs and kwargs['weighted'] == True:
        formstr += sep+"1"
    formstr += "\n"
    for u, v in graph.edges():
        ostream.write(formstr.format(u+offset, v+offset))


def read_leda(filename):
    graph = Graph()

    numVertices = 10**10
    lines = open(filename)

    # Skip preable
    skip_lines(lines, 4)
    numVertices = int(next(lines))

    # We do not need vertex labels
    skip_lines(lines, numVertices)

    numEdges = int(next(lines))

    for line in lines:
        line = line.strip()
        if line == '' or line[0] == '#':
            continue
        s, t, r, l = line.split(' ')
        graph.add_edge(int(s)-1, int(t)-1)  # LEDA is 1-based.

    return graph


def write_leda(graph, ostream, **kwargs):
    ostream.write('LEDA.GRAPH\nstring\nstring\n-1\n')

    n = len(graph)
    m = sum(1 for _, _ in graph.edges())

    ostream.write(str(n)+'\n')
    indices = []
    for i, v in enumerate(graph):
        indices.extend([0 for x in range(len(indices), v + 1)])
        indices[v] = i
        ostream.write('|{}|\n')

    ostream.write(str(m)+'\n')
    for s, t in graph.edges():
        ostream.write(str(s+1)+' '+str(t+1)+' 0 |{}|\n')


def write_dgf(graph, ostream):
    n = len(graph)
    m = sum(1 for _, _ in graph.edges())

    ostream.write('p edge ' + str(n) + ' ' + str(m) + '\n')
    indices = []
    for i, v in enumerate(graph):
        indices.extend([0 for x in range(len(indices), v + 1)])
        indices[v] = i

    for s, t in graph.edges():
        ostream.write('e ' + str(s+1) + ' '+str(t+1) + '\n')


def skip_lines(fileit, num):
    skipped = 0
    while skipped < num:
        line = next(fileit).strip()
        if line != '' and line[0] != '#':
            skipped += 1


def read_gexf(filename):
    from BeautifulSoup import BeautifulSoup as Soup
    soup = Soup(open(filename).read())
    graph = Graph()

    for edge in soup.findAll("edge"):
        source = int(edge['source'])
        target = int(edge['target'])
        graph.add_edge(source, target)
    return graph


def read_graphml(filename):
    from BeautifulSoup import BeautifulSoup as Soup
    soup = Soup(open(filename).read())
    graph = Graph()

    for edge in soup.findAll("edge"):
        source = int(edge['source'])
        target = int(edge['target'])
        graph.add_edge(source, target)
    return graph


def read_gml(filename):
    graph = Graph()

    data = read_gml_data(filename)
    for n in data['graph']['node']:
        graph.add_node(int(n['id']))

    for e in data['graph']['edge']:
        graph.add_edge(int(e['source']), int(e['target']))

    return graph


def write_gml_attr(data, lvl, ostream):
    for attr in data:
        ostream.write('\t'*lvl)
        ostream.write(str(attr))
        ostream.write(' ')

        try:
            it = iter(data[attr])
        except TypeError:
            # Not iterable: plain data
            plain = True
        else:
            # Iterable: not plain EXCEPT if it is a string
            plain = type(data[attr]) is str

        if plain:
            ostream.write('{0}\n'.format(data[attr]))
        else:
            ostream.write('[\n')
            write_gml_attr(data[attr], lvl+1, ostream)
            ostream.write('\t'*lvl)
            ostream.write(']\n')


def write_gml(graph, ostream, nodedata=None, **kwargs):
    ostream.write('graph\n[\n')
    for v in graph:
        ostream.write('\tnode\n\t[\n')
        ostream.write('\t\tid {0}\n'.format(v))
        if nodedata is not None and v in nodedata:
            write_gml_attr(nodedata[v], 2, ostream)

        ostream.write('\t]\n')
    for s, t in graph.edges():
        ostream.write('\tedge\n\t[\n')
        ostream.write('\t\tsource {0}\n\t\ttarget {1}\n'.format(s, t))
        ostream.write('\t]\n')
    ostream.write(']')


# TODO: refactor this into a stream writer.
def write_gexf(graph, labels, vertexlabels):
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">'
    print '<meta lastmodifieddate="{0:%Y-%m-%d}">'.format(
        datetime.date.today())
    print '\t<creator>LuFGTI RWTH Aachen University</creator>'
    print '\t<description></description>'
    print '</meta>'
    print '<graph defaultedgetype="undirected">'

    print '\t<attributes class="node">'
    for i, l in enumerate(labels):
        print '\t\t<attribute id="{0}" title="{1}" type="string" />'.format(
            i, l)
    print '\t</attributes>'

    print '\t<nodes>'
    for v in graph:
        lab = vertexlabels[v]
        # Note: quoteattr already adds quotes around the string.
        print '\t\t<node id="{0}" label="{1}">'.format(v, v)
        for i, l in enumerate(lab):
            print '\t\t\t<attvalue for="{0}" value="{1}" />'.format(i, l)
        print '\t\t</node>'
    print '\t</nodes>'

    print '\t<edges>'
    for i, e in enumerate(graph.edges()):
        print '\t\t<edge id="{0}" source="{1}" target="{2}" />'.format(
            i, e[0], e[1])
    print '\t</edges>'

    print '</graph>'
    print '</gexf>'


def load_coloring(filename):
    from graph import Coloring as Coloring
    coloring = Coloring()
    for line in open(filename).readlines():
        line = line.strip()
        if ':' not in line:
            continue
        vertex, color = line.split(':')
        coloring[int(vertex)] = int(color)
    return coloring


def remove_loops(graph):
    for v in graph:
        if graph.adjacent(v, v):
            graph.remove_edge(v, v)


def get_parser(ext):
    if ext == ".gexf":
        return read_gexf
    elif ext == ".graphml":
        return read_graphml
    elif ext == ".gml":
        return read_gml
    elif ext == ".leda":
        return read_leda
    elif ext == ".txt":
        # print "Ending is .txt. Assuming SNAP raw edge list"
        return read_edgelist
    else:
        raise Exception('Unknown input file format: {0}'.format(ext))


def get_writer(ext):
    if ext == ".leda":
        return write_leda
    elif ext == ".gml":
        return write_gml
    elif ext == ".txt":
        return write_edgelist
    else:
        raise Exception('Unknown output file format: {0}'.format(ext))


def load_graph(filename):
    import os
    name, ext = os.path.splitext(filename)

    parser = get_parser(ext)

    return parser(filename)


def write_graph(graph, filename, **kwargs):
    import os
    name, ext = os.path.splitext(filename)

    writer = get_writer(ext)
    writer(graph, open(filename, 'w'), **kwargs)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Loads a graph from file. \
        only arugment for --convert, the graph will be written back into \
        said file. Both the input and the output format are determined by \
        the file ending. Supported inputs types are: \
            .leda .graphml .gml .txt (snap edge list). \
        Supported outputs types are: \
            .leda \
         ")
    parser.add_argument("graph", help="Filename of the input graph.", type=str)
    parser.add_argument("--convert", "-c", help="Output file.", type=str)
    args = parser.parse_args()

    filename = sys.argv[1]
    try:
        g = load_graph(sys.argv[1])
    except Exception as ex:
        print "Could not load graph."
        print ex
        sys.exit()
    print "Graph {0} has {1} vertices and {2} edge".format(
        filename, len(g), len(list(g.edges())))
    print "Graph hash: {0}".format(graph.graph_hash(g))

    if args.convert:
        print "Converting to {0}".format(args.convert)
        try:
            write_graph(g, args.convert)
        except Exception as ex:
            print "\nCould not convert."
            print ex
            sys.exit()
