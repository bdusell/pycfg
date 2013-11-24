'''Run Example 4.4 from Aho & Ullman p. 304-305, printing each step and the
resulting parse tree to stdout.'''

from cfg import aho_ullman, cfg

CFG = cfg.ContextFreeGrammar

G = CFG('''
E -> E+T
E -> T
T -> T*F
T -> F
F -> a
''')

w = [cfg.Terminal(a) for a in 'a*a']

try:
    parse = aho_ullman.bottomup_backtrack_parse(G, w)
    tree = aho_ullman.RightParse(G, parse[::-1]).tree()
    assert list(tree.iter_leaves()) == w
    print tree
except aho_ullman.ParseError, e:
    print e
