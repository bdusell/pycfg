'''Compute the SLR DFA of LR(0) items for the expression grammar and print a
diagram of it in dot code to stdout.'''

from cfg.slr import *
from cfg.cfg import *

CFG = ContextFreeGrammar

G = CFG('''
E -> E+T | T
T -> T*F | F
F -> (E) | a
''')

print Automaton(G).dot_html()

