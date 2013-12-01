'''A module which models finite state machines/automata.'''

from util.weighted_digraph import WeightedDigraph
import util.dot

class Automaton(WeightedDigraph):
    '''An automaton where each state can have at most one transition per symbol
    leading out of a state. The fact that there may be no transition on a
    symbol leading out of a state makes this technically not a DFA.'''

    def add_transition(self, source, symbol, dest):
        '''Add a transition to the automaton. The source and destination states
        are added to the automaton if they do not already exist. If a
        transition on the given symbol already exists at the source state, it
        is overwritten.'''
        self.add_edge(source, symbol, dest)

    def has_transition(self, source, symbol):
        '''Test whether a state has an outgoing transition on a given symbol.
        '''
        return self.has_edge(source, symbol)

    def next_state(self, source, symbol):
        '''Get the state to which a state has a transition on the given symbol.
        '''
        return self.get_edge(source, symbol)

    def add_state(self, s):
        '''Add a state to the automaton.'''
        self.add_vertex(s)

    @property
    def states(self):
        '''A set containing all of the states in the automaton.'''
        result = set(self._edges.keys())
        for qi, a, qj in self.transitions:
            result.add(qi)
            result.add(qj)
        return result

    @property
    def transitions(self):
        '''A list of triples (s, X, t), where s is the source state, t is the
        destination state, and X is the transition symbol of each transition in
        the automaton.'''
        return self.edges

    def _dot_str(self, tostring, shape):
        lines = ['q%s [label=%s]' % (id(q), tostring(q)) for q in self.states]
        lines += ['q%s -> q%s [label="%s"]' % (id(qi), id(qj), util.dot.escape(str(a))) for qi, a, qj in self.transitions]
        return '''\
digraph {
	node [shape=%s];
	%s
}
''' % (shape, ';\n\t'.join(lines))

    def dot_str(self, shape='circle'):
        return self._dot_str(lambda s: '"%s"' % util.dot.escape(self.state_dot_label(s)), shape)

    def dot_html(self, shape='circle'):
        return self._dot_str(lambda s: '<%s>' % self.state_dot_html_label(s), shape)

    def state_dot_label(self, s):
        return str(s)

    def state_dot_html_label(self, s):
        return str(s)

