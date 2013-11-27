'''Run Example 4.1 from Aho & Ullman p. 292-293i, printing the steps to stdout.
'''

from cfg import aho_ullman, cfg

CFG = cfg.ContextFreeGrammar

G = CFG('''
E -> T+E
E -> T
T -> F*T
T -> F
F -> a
''')

w = [cfg.Terminal(a) for a in 'a+a']

try:
    parse = aho_ullman.topdown_backtrack_parse(G, w)
    print aho_ullman.LeftParse(G, parse).tree()
except aho_ullman.ParseError, e:
    print e
