'''Compute the SLR parsing table for a grammar read from stdin in extended
sytax, printing the original grammar, augmented grammar, first sets, follow
sets, and table to stdout in HTML.'''

import sys
from cfg.cfg_reader import *
from cfg.slr import *

try:
    G = parse_cfg(sys.stdin.read())
except ValueError, e:
    print e
    sys.exit(1)

T = ParsingTable(G)

print '<h1>Original Grammar</h1>'
print T._grammar.html()
print '<h1>Augmented Grammar</h1>'
print T._automaton.augmented_grammar().html()
print '<h1>First Sets</h1>'
print T._first_sets.html()
print '<h1>Follow Sets</h1>'
print T._follow_sets.html()
print '<h1>Parsing Table</h1>'
print T.html()

