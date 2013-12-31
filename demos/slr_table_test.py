'''Compute the SLR parsing table for an example grammar, printing the original
grammar, augmented grammar, first sets, follow sets, and parsing table in HTML
to stdout.'''

from cfg.slr import *
from cfg.core import *

CFG = ContextFreeGrammar

G = CFG('''
E -> E+T | T
T -> T*F | F
F -> (E) | a
''')

T = ParsingTable(G)

html = True

if html:
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
else:
    print T._automaton.dot_html()
