'''A weighted directed graph class.'''

import pprint

class WeightedDigraph(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self._edges = {}

    def add_edge(self, source, dest, weight):

        if source not in self._edges: self._edges[source] = source_dict = {}
        else: source_dict = self._edges[source]

        source_dict[dest] = weight

    def get_edge(self, source, dest):
        return self._edges[source][dest]

    def has_edge(self, source, dest):
        return source in self._edges and dest in self._edges[source]

    def add_vertex(self, v):
        if v not in self._edges: self._edges[v] = {}

    @property
    def edges(self):
        return [(source, dest, weight) for source, sdict in self._edges.items() \
                                       for dest, weight in sdict.items()]

    def __str__(self):
        return pprint.pformat(self._edges)

