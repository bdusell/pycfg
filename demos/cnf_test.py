'''Convert a grammar to CNF and print it to stdout.'''

from cfg import cfg, cnf

CFG = cfg.ContextFreeGrammar
CNF = cnf.ChomskyNormalForm

G = CFG('''
S -> ASA | aB
A -> B | S
B -> b |
''')

print 'G:'
print G
print
print 'G\':'
print CNF(G)
