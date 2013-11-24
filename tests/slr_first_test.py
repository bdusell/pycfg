'''Compute the first set for a grammar and print it in HTML to stdout.'''

from cfg.slr import *
from cfg.cfg import *

CFG = ContextFreeGrammar

G = CFG('''
E -> E+T | T
T -> T*F | F
F -> (E) | a
''')

T = FirstSetTable(augmented(G))

print T.html()

