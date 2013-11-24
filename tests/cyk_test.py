'''Run Example 4.8 from Aho & Ullman p. 315-316, printing the steps to stdout.
'''

from cfg import aho_ullman, cfg

CFG = cfg.ContextFreeGrammar

G = CFG('''
S -> AA | AS | b
A -> SA | AS | a
''')

w = map(cfg.Terminal, 'abaab')

T = aho_ullman.cocke_younger_kasami_algorithm(G, w)
print aho_ullman.parse_table_str(T)
parse = aho_ullman.left_parse_from_parse_table(G, w, T)
tree = aho_ullman.LeftParse(G, parse).tree()
print tree
