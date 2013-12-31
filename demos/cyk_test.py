'''Run Example 4.8 from Aho & Ullman p. 315-316, printing the steps to stdout.
'''

from cfg import aho_ullman, core
import sys

CFG = core.ContextFreeGrammar

G = CFG('''
S -> AA | AS | b
A -> SA | AS | a
''')

w = map(core.Terminal, 'abaab')

print 'G:'
print G
print
print 'w =', ''.join(map(str, w))
print

T = aho_ullman.cocke_younger_kasami_algorithm(G, w, out=sys.stdout, check=False)
print 'T:'
print aho_ullman.parse_table_str(T)
print
parse = aho_ullman.left_parse_from_parse_table(G, w, T, check=False)
tree = aho_ullman.LeftParse(G, parse).tree()

print 'Parse tree:', tree

