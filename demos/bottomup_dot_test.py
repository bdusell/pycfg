'''Run the bottom-up backtrack parsing algorithm from Aho & Ullman on a sample
input and print a diagram of the parse tree in dot code to stdout.'''

from cfg import aho_ullman, core

CFG = core.ContextFreeGrammar

G = CFG('''
E -> E+T
E -> T
T -> T*F
T -> F
F -> a
''')

w = map(core.Terminal, 'a*a')

class NullOutput:
    def write(self, x):
        pass

null_output = NullOutput()

try:
    parse = aho_ullman.bottomup_backtrack_parse(G, w, null_output)
    tree = aho_ullman.RightParse(G, parse[::-1]).tree()
    assert list(tree.iter_leaves()) == w
    print tree.dot_str()
except aho_ullman.ParseError, e:
    print e

