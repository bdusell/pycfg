'''Compute the first and follow sets of a grammar and print them to stdout.'''

import copy
from cfg.cfg import *
from cfg.slr import *

CFG = ContextFreeGrammar

G = CFG('''
A -> ADx | BC
B -> AC | BB |
C -> y |
D -> z
E -> xC
''')

print '<h1>Grammar G</h1>'
print G.html()

FIRST = FirstSetTable(G)
print '<h1>First Sets</h1>'
print FIRST.html()

M = Automaton(G)
FOLLOW = FollowSetTable(FIRST, M)
print '<h1>Follow Sets</h1>'
print FOLLOW.html()

