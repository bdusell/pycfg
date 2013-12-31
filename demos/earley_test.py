'''Run Example 4.10 from Aho & Ullman p. 321-322, printing the steps to stdout.
'''

from cfg import aho_ullman, core

CFG = core.ContextFreeGrammar

G = CFG('''
E -> T+E
E -> T
T -> F*T
T -> F
F -> (E)
F -> a
''')

w = map(core.Terminal, '(a+a)*a')

print 'G:'
print G
print
print 'w =', ''.join(map(str, w))
print

I = aho_ullman.earley_parse(G, w, out=None)
for j in xrange(len(I)):
    print aho_ullman.parse_list_str(I, j)
    print

parse = aho_ullman.right_parse_from_parse_lists(G, w, I)
print aho_ullman.RightParse(G, parse).tree()
