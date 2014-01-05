'''A directed graph class.'''

class Digraph:
    '''A directed graph class.'''

    # Fundamental methods
    def __init__(self, vertices=None, edges=None):
        '''Initialize the graph with a container of vertices and/or a container
        of edges, where edges are tuples containing a start node and end node.
        '''
        
        # Edges are stored as a dictionary mapping vertices to sets of vertices
        # they connect to.
        self._edges = {}

        # Add vertices, then edges
        if vertices != None: self.add_vertices_from(vertices)
        if edges != None: self.add_edges_from(edges)
    
    def clear(self):
        '''Remove all vertices and edges from the graph.'''
        self._edges = {}
    
    # Addition methods
    def add_edge(self, s, t):
        '''Add an edge to the graph. Implicitly add vertices not already in the
        graph.'''
        self.add_vertex(s)
        self.add_vertex(t)
        self._edges[s].add(t)
    
    def add_edges_from(self, container):
        '''Add edges to the graph from a container of 2-tuples, where edges are
        specified with a start vertex and end vertex. Implicitly add new
        vertices.'''

        # Assert that all edges are 2-tuples
        for e in container:
            assert len(e) == 2

        # Add edges
        for e in container:
            self.add_edge(*e)
    
    def add_vertex(self, vertex):
        '''Add a new vertex to the graph or do nothing if it is already
        present.'''
        if vertex not in self._edges:
            self._edges[vertex] = set()

    def add_vertices_from(self, container):
        '''Add vertices from a container to the graph.'''
        for v in container:
            self.add_vertex(v)

    # Removal methods
    def remove_edge(self, s, t):
        '''Remove the pre-existing edge from vertex s to t from the graph.'''
        assert self.has_edge(s, t)
        self._edges[s].remove(t)
    
    def remove_edges_from(self, container):
        '''Remove all edges specified in a container from the graph, where edges
        are 2-tuples of vertices.'''
        for e in container:
            assert len(e) == 2
        for s, t in container:
            self.remove_edge(s, t)

    def remove_vertex(self, vertex):
        '''Remove a pre-existing vertex from the graph and all of its edges.'''
        assert self.has_vertex(vertex)
        del self._edges[vertex]
        for dest_set in self._edges.iteritems():
            if vertex in dest_set:
                dest_set.remove(vertex)

    def remove_vertices_from(self, vertices):
        '''Remove all vertices from the graph specified in a container and all
        of their edges.'''
        for v in vertices:
            assert self.has_vertex(v)
        for v in vertices:
            self.remove_vertex(v)

    def successors(self, vertex):
        '''Return a list of the vertices a vertex has outgoing edges to.'''
        assert self.has_vertex(vertex)
        return list(self._edges[vertex])

    def predecessors(self, vertex):
        '''Return a list of the vertices a vertex has incoming edges from.'''
        assert self.has_vertex(vertex)
        return [s for (s, dest_set) in self._edges.iteritems() if vertex in dest_set]

    def edges(self):
        '''Return the edges in the graph as a set of 2-tuples, where each
        tuple consists of the start vertex and the end vertex.'''
        return set((s, t) for (s, dest) in self._edges.iteritems() for t in dest)

    def has_edge(self, s, t):
        '''Return a boolean value indicating whether the graph connects vertex
        s to t.'''
        return s in self._edges and t in self._edges[s]

    def has_vertex(self, vertex):
        '''Return a boolean value indicating whether the graph contains a
        certain vertex.'''
        return vertex in self._edges

    def vertices(self):
        '''Return a list of the vertices in the graph.'''
        return self._edges.keys()

    def cyclic(self):
        '''Return whether the graph contains a cycle.'''
        return is_cyclic_multi(self._edges.iterkeys(), lambda x: self._edges[x])

    def __str__(self):
        return 'vertices = %s\nedges = %s' % (self.vertices, self.edges)

_VISITING, _VISITED = range(2)

def is_cyclic(root, successor_func):
    '''Determine whether a graph is cyclic. The graph is defined by a starting
    node and a successor function which generates the child nodes of a node in
    the graph. The nodes must be hashable.'''
    visited = { root : _VISITING }
    def visit(node):
        for child in successor_func(node):
            if child in visited:
                if visited[child] == _VISITING:
                    return True
            else:
                visited[child] = _VISITING
                if visit(child):
                    return True
                visited[child] = _VISITED
        return False
    return visit(root)

def is_cyclic_multi(roots, successor_func):
    '''Determine whether a graph is cyclic, given some subset of its nodes
    which determine the starting points of the graph traversal.'''
    visited = {}
    def visit(nodes):
        for node in nodes:
            if node in visited:
                if visited[node] == _VISITING:
                    return True
            else:
                visited[node] = _VISITING
                if visit(successor_func(node)):
                    return True
                visited[node] = _VISITED
        return False
    return visit(roots)

