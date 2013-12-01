'''Convert a grammar to CNF form and print it to stdout in HTML.'''

from cfg import cfg, cnf

CFG = cfg.ContextFreeGrammar
CNF = cnf.ChomskyNormalForm

G = CFG('''
S -> ASA | aB
A -> B | S
B -> b |
''')

print CNF(G).html()

