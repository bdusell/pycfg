from cfg.slr import *
from cfg.cfg import *
import unittest
from test_table import grammar_test_cases

class TestSLR(unittest.TestCase):

    def test_item(self):
        S, T, plus = map(Nonterminal, 'ST') + map(Terminal, '+')
        p = ProductionRule(S, [S, plus, T])
        p2 = ProductionRule(S, [T])
        with self.assertRaises(TypeError) as ar:
            Item('S -> S+T', 0)
        with self.assertRaises(ValueError) as ar:
            Item(p, 5)
        with self.assertRaises(ValueError) as ar:
            Item(p, -2)
        self.assertEqual(Item(p, 0), Item(p, 0))
        self.assertNotEqual(Item(p, 0), Item(p, 1))
        self.assertNotEqual(Item(p, 0), Item(p2, 0))
        self.assertEqual(Item(p, 0).after_dot(), S)
        self.assertEqual(Item(p, 1).after_dot(), plus)
        self.assertEqual(Item(p, 2).after_dot(), T)
        self.assertEqual(Item(p, 3).after_dot(), None)
        self.assertFalse(Item(p, 1).complete())
        self.assertTrue(Item(p, 3).complete())
        self.assertEqual(Item(p, 2).dot_advanced(), Item(p, 3))
        self.assertEqual(len(set([Item(p, 0), Item(p, 1), Item(p, 0)])), 2)
        self.assertEqual(len(set([Item(p, 0), Item(p2, 0), Item(p, 2)])), 3)

    def test_table(self):
        for test in filter(lambda x: x.table is not None, grammar_test_cases):
            actual_table = ParsingTable(test.grammar).to_normal_form()
            self.assertTrue(actual_table.equivalent(test.table))

if __name__ == '__main__':
    unittest.main()

