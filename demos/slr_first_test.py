'''Compute the first set for a grammar and print it in HTML to stdout.'''

from cfg.slr import *
from cfg.cfg import *

CFG = ContextFreeGrammar

G = CFG('''
E -> E+T | T
T -> T*F | F
F -> (E) | a
''')

print '<h1><var>G<var>:</h1>'
print G.html()
print

T = FirstSetTable(augmented(G))

print '<h1><var>T</var>:</h1>'
print T.html()

