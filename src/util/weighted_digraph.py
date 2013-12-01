'''A weighted directed graph class.'''

import pprint

class WeightedDigraph(object):

    def __init__(self):
        '''Initalize an empty graph.'''
        self.clear()

    def clear(self):
        '''Re-initialize to an empty graph.'''
        self._edges = {}

    def add_edge(self, source, dest, weight):
        '''Add an edge to the graph, inserting the vertices if necessary.'''

        if source not in self._edges: self._edges[source] = source_dict = {}
        else: source_dict = self._edges[source]

        source_dict[dest] = weight

    def get_edge(self, source, dest):
        '''Get the weight of the edge connecting source to dest, provided that
        it exists.'''
        return self._edges[source][dest]

    def has_edge(self, source, dest):
        '''Tell whether an edge exists which connects source to dest.'''
        return source in self._edges and dest in self._edges[source]

    def add_vertex(self, v):
        '''Add a vertex to the graph.'''
        if v not in self._edges: self._edges[v] = {}

    @property
    def edges(self):
        '''A list of triples (s, t, w) for each edge, where s is the source
        vertex, t is the destination vertex, and w is the weight of each edge
        in the graph.'''
        return [(source, dest, weight) for source, sdict in self._edges.items() \
                                       for dest, weight in sdict.items()]

    def __str__(self):
        return pprint.pformat(self._edges)

