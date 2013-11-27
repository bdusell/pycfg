'''Convert a grammar to CNF and print it to stdout.'''

from cfg import cfg

CFG = cfg.ContextFreeGrammar
CNF = cfg.ChomskyNormalForm

G = CFG('''
S -> ASA | aB
A -> B | S
B -> b |
''')

print CNF(G)
