from cfg.classify import *
import unittest

class TestClassify(unittest.TestCase):

    def test_classify(self):

        G1 = ContextFreeGrammar('''\
A -> BC
B -> de
C -> f
''')

        G2 = ContextFreeGrammar('''\
A -> BC
B -> b
C ->
''')

        G3 = ContextFreeGrammar('''\
A -> B
B -> B
''')
        G4 = ContextFreeGrammar('''\
A -> B
B -> C
C -> D
D -> E
E -> F
F -> B
''')
        G5 = ContextFreeGrammar('''\
A -> B
B -> CBD
C ->
D ->
''')
        G6 = ContextFreeGrammar('''\
A -> B
B -> CDE
C -> FF
D -> FF
F -> B |
E -> DD
''')

        G7 = ContextFreeGrammar('''\
A -> C
B -> C
C -> c
''')

        G8 = ContextFreeGrammar('''\
A -> EC
B -> CE
E ->
C -> c
''')

        self.assertFalse(has_empty_rules(G1))
        self.assertTrue(has_empty_rules(G2))
        self.assertFalse(is_cyclic(G1))
        self.assertFalse(is_cyclic(G2))
        self.assertTrue(is_cyclic(G3))
        self.assertTrue(is_cyclic(C4))
        self.assertTrue(is_cyclic(G5))
        self.assertTrue(is_cyclic(G6))
        self.assertFalse(is_cyclic(G7))
        self.assertFalse(is_cyclic(G8))

