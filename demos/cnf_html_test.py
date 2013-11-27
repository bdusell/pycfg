'''Convert a grammar to CNF form and print it to stdout in HTML.'''

from cfg import cfg

CFG = cfg.ContextFreeGrammar
CNF = cfg.ChomskyNormalForm

G = CFG('''
S -> ASA | aB
A -> B | S
B -> b |
''')

print CNF(G).html()

