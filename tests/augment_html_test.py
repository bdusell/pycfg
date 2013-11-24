'''Augment a grammar and print it as HTML to stdout.'''

import cfg.cfg, cfg.slr

CFG = cfg.cfg.ContextFreeGrammar

G = CFG('''
E -> E+T | T
T -> T*F | F
F -> (E) | a
''')

print cfg.slr.augmented(G).html()

