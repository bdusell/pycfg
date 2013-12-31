'''Convert a grammar to CNF form and print it to stdout in HTML.'''

from cfg import core, cnf

CFG = core.ContextFreeGrammar
CNF = cnf.ChomskyNormalForm

G = CFG('''
S -> ASA | aB
A -> B | S
B -> b |
''')

print '<h1><var>G</var>:</h1>'
print G.html()
print
print '<h1><var>G&prime;</var>:</h1>'
print CNF(G).html()

