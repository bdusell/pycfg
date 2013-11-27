'''Construct a simple automaton and print a diagram of it to stdout in dot
code.'''

import cfg.automaton

Automaton = cfg.automaton.Automaton

M = Automaton()

M.add_transition(0, 'a', 1)
M.add_transition(0, 'b', 2)
M.add_transition(1, 'b', 2)

print M.dot_str()

