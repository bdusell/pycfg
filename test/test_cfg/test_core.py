from cfg.core import *
import unittest
from pprint import pprint

class TestCFG(unittest.TestCase):

    def test_nonterminal(self):

        A = Nonterminal('A')
        L = [1, 3.14, 'abcdef', None]

        self.assertIsInstance(A, Symbol,
            'Nonterminal is an instance of Symbol')
        self.assertEqual(A.name, 'A',
            'Get label of nonterminal')
        self.assertEqual(A, A,
            'Nonterminal instance is equal to itself')
        self.assertEqual(Nonterminal('X'), Nonterminal('X'),
            'Different nonterminal instances with same labels are equal to each other')
        self.assertNotEqual(Nonterminal('X'), Nonterminal('Y'),
            'Nonterminals with different labels are not equal')
        self.assertEqual(Nonterminal('Noun phrase'), Nonterminal('Noun phrase'),
            'Nonterminals with names longer than one character can be equal')
        self.assertIn(Nonterminal('X'), L + [Nonterminal('X')],
            'Nonterminals can be found in lists')
        self.assertIn(Nonterminal('X'), set(L + [Nonterminal('X')]),
            'Nonterminals can be hashed and found in sets')
        self.assertEqual(len(set(map(Nonterminal, 'AABBC'))), 3,
            'Nonterminals are deduplicated in sets')
        self.assertNotEqual(Nonterminal('A'), Terminal('A'),
            'Nonterminals are not equal to terminals with the same label')
        self.assertEqual(len(set(map(Nonterminal, 'XXYYZ') + map(Terminal, 'XXYYZ'))), 6,
            'Nonterminals and terminals with same names are distinct items in sets')

    def test_terminal(self):

        a = Terminal('a')
        L = [1, 3.14, 'abcdef', None]

        self.assertIsInstance(a, Symbol,
            'Terminal is an instance of Symbol')
        self.assertEqual(a.name, 'a',
            'Get label of terminal')
        self.assertEqual(a, a,
            'Terminal instance is equal to itself')
        self.assertEqual(Terminal('x'), Terminal('x'),
            'Different terminal instances with same labels are equal to each other')
        self.assertNotEqual(Terminal('x'), Terminal('y'),
            'Terminals with different labels are not equal')
        self.assertEqual(Terminal('the'), Terminal('the'),
            'Terminals with names longer than one character can be equal')
        self.assertIn(Terminal('x'), L + [Terminal('x')],
            'Terminals can be found in lists')
        self.assertIn(Terminal('x'), set(L + [Terminal('x')]),
            'Terminals can be hashed and found in sets')
        self.assertEqual(len(set(map(Terminal, 'AABBC'))), 3,
            'Terminals are deduplicated in sets')
        self.assertNotEqual(Terminal('a'), Nonterminal('a'),
            'Terminals are not equal to nonterminals with the same label')
        self.assertEqual(len(set(map(Terminal, 'xxyyz') + map(Nonterminal, 'xxyyz'))), 6,
            'Terminals and nonterminals with same names are distinct items in sets')

    def test_subscripted_nonterminal(self):

        self.assertIsInstance(SubscriptedNonterminal('S', 0), Nonterminal,
            'SubscriptedNonterminal is an instance of Nonterminal')
        self.assertNotEqual(SubscriptedNonterminal('S', 0), Nonterminal('S'),
            'Subscripted nonterminal is not equal to original')
        self.assertNotEqual(Nonterminal('S'), SubscriptedNonterminal('S', 0),
            'Nonterminal is not equal to subscripted nonterminal with same label')
        self.assertEqual(SubscriptedNonterminal('A', 5), SubscriptedNonterminal('A', 5),
            'Subscripted nonterminals with same label and subcript are equal')
        self.assertNotEqual(SubscriptedNonterminal('A', 1), SubscriptedNonterminal('A', 2),
            'Subscripted nonterminals with different subscripts are not equal')
        self.assertNotEqual(SubscriptedNonterminal('A', 1), SubscriptedNonterminal('B', 1),
            'Subscripted nonterminals with different labels are not equal')

        L = [10, 'abc', Nonterminal('S'), Terminal('S'), SubscriptedNonterminal('S', 0)]

        self.assertIn(SubscriptedNonterminal('S', 0), L,
            'Subscripted nonterminals can be found in lists')
        self.assertIn(SubscriptedNonterminal('S', 0), set(L),
            'Subscripted nonterminals can be hashed and found in lists')

        self.assertEqual(len(set(map(lambda x: SubscriptedNonterminal(x, 1), 'ABC' * 5))), 3,
            'Subscripted nonterminals are deduplicated in sets')

        M = map(lambda x: SubscriptedNonterminal('A', x), range(10) + range(20, 30))

        self.assertEqual(
            SubscriptedNonterminal('S', 1),
            SubscriptedNonterminal.next_unused('S', set(L + M)),
            'Get next unused subscripted nonterminal after S0')
        self.assertEqual(
            SubscriptedNonterminal('A', 10),
            SubscriptedNonterminal.next_unused('A', set(L + M)),
            'Get next unused subscripted nonterminal after A9')

    def test_primed_nonterminal(self):

        self.assertIsInstance(PrimedNonterminal('S', 1), Nonterminal,
            'PrimedNonterminal is an instance of Nonterminal')
        self.assertNotEqual(PrimedNonterminal('S', 5), Nonterminal('S'),
            'Primed nonterminal is not equal to original')
        self.assertNotEqual(Nonterminal('S'), PrimedNonterminal('S', 5),
            'Nonterminal is not equal to primed nonterminal with the same label')
        self.assertEqual(PrimedNonterminal('A', 3), PrimedNonterminal('A', 3),
            'Primed nonterminals with same label and number of marks are equal')
        self.assertNotEqual(PrimedNonterminal('A', 1), PrimedNonterminal('A', 2),
            'Primed nonterminals with different numbers of marks are not equal')
        self.assertNotEqual(PrimedNonterminal('A', 2), PrimedNonterminal('B', 2),
            'Primed nonterminals with different labels are not equal')
        self.assertNotEqual(PrimedNonterminal('A', 2), SubscriptedNonterminal('A', 2),
            'Primed nonterminal is not equal to subscripted nonterminal')
        self.assertNotEqual(SubscriptedNonterminal('A', 2), PrimedNonterminal('A', 2),
            'Subscripted nonterminal is not equal to primed nonterminal')

        L = [543, 'S', Nonterminal('S'), Terminal('S'),
             SubscriptedNonterminal('S', 1), PrimedNonterminal('S', 1)]

        self.assertIn(PrimedNonterminal('S', 1), L,
             'Primed nonterminals can be found in lists')
        self.assertIn(PrimedNonterminal('S', 1), set(L),
             'Primed nonterminals can be hashed and found in lists')

        self.assertEqual(len(set(L)), len(set(L)),
             'Subscripted nonterminals are distinct items in sets')

    def test_marker(self):

        self.assertIsInstance(Marker('$'), Terminal,
            'Marker is an instance of Terminal')
        self.assertEqual(Marker('$'), Marker('$'),
            'Marker is equal to itself')
        self.assertNotEqual(Marker('$'), Marker('#'),
            'Markers with different labels are not equal')
        self.assertNotEqual(Marker('$'), Terminal('$'),
            'Marker is not equal to terminal with same label')
        self.assertNotEqual(Terminal('$'), Marker('$'),
            'Terminal is not equal to marker with same label')
        self.assertNotEqual(Marker('$'), Nonterminal('$'),
            'Marker not equal to nonterminal')
        self.assertNotEqual(Nonterminal('$'), Marker('$'),
            'Nonterminal not equal to marker')

        L = [1, '$', Nonterminal('$'), Terminal('$'),
             SubscriptedNonterminal('$', 1), PrimedNonterminal('$', 1),
             Marker('$')]

        self.assertIn(Marker('$'), L,
            'Markers can be found in lists')
        self.assertIn(Marker('$'), set(L),
            'Markers can be hashed and found in lists')
        self.assertEqual(len(set(L)), len(L),
            'Markers are distinct items in lists')

    def test_production_rule(self):

        self.assertEqual(
            ProductionRule(Symbol('S'), [Symbol('S'), Terminal('+'), Symbol('T')]),
            ProductionRule(Symbol('S'), [Symbol('S'), Terminal('+'), Symbol('T')]),
            'Production rules with same left and right sides are equal')

        self.assertNotEqual(
            ProductionRule(Symbol('S'), [Symbol('S'), Terminal('+'), Symbol('T')]),
            ProductionRule(Symbol('S'), [Symbol('T')]),
            'Production rules with different right sides are not equal')

        self.assertNotEqual(
            ProductionRule(Symbol('S'), [Symbol('X')]),
            ProductionRule(Symbol('T'), [Symbol('X')]),
            'Prodcution rules with different left sides are not equal')

        p1 = ProductionRule(Symbol('S'), [Symbol('S'), Terminal('+'), Symbol('S')])
        p2 = ProductionRule(Symbol('S'), [Symbol('S'), Terminal('+'), Symbol('S')])
        p3 = ProductionRule(Symbol('S'), [Symbol('S'), Terminal('*'), Symbol('S')])
        p4 = ProductionRule(Symbol('T'), [Symbol('S'), Terminal('*'), Symbol('S')])

        self.assertEqual(len(set([p1, p2, p3, p4])), 3,
            'Production rules are hashable and deduplicated in sets')

    def test_parse_tree(self):

        t1 = ParseTree(Nonterminal('S'), [
            ParseTree(Nonterminal('S'), [ParseTree(Terminal('1'))]),
            ParseTree(Terminal('+')),
            ParseTree(Nonterminal('S'), [ParseTree(Terminal('2'))])
        ])

        t2 = ParseTree(Nonterminal('S'), [
            ParseTree(Nonterminal('S'), [ParseTree(Terminal('1'))]),
            ParseTree(Terminal('+')),
            ParseTree(Nonterminal('S'), [ParseTree(Terminal('2'))])
        ])

        t3 = ParseTree(Nonterminal('S'), [
            ParseTree(Nonterminal('S'), [ParseTree(Terminal('1'))]),
            ParseTree(Terminal('+')),
            ParseTree(Nonterminal('S'), [ParseTree(Terminal('3'))])
        ])

        self.assertEqual(t1, t2,
            'Parse trees are equal')
        self.assertNotEqual(t1, t2,
            'Parse trees are not equal')

        t4 = ParseTree(Nonterminal('S'), [
            t1, ParseTree(Terminal('+')), t3
        ])

        t5 = ParseTree(Nonterminal('S'), [
            t1, ParseTree(Terminal('+')), t3
        ])

        t6 = ParseTree(Nonterminal('S'), [
            t1, ParseTree(Terminal('+')), t2
        ])

        self.assertEqual(t4, t5,
            'Bigger parse trees are equal')
        self.assertNotEqual(t4, t6,
            'Bigger parse trees are not equal')
        self.assertNotEqual(t6, t1,
            'Big tree not equal to small tree')

        self.assertEqual(list(t1.iter_leaves()), map(Terminal, '1+2'),
            'Get all leaves from parse tree in order')
        self.assertEqual(list(t4.iter_leaves()), map(Terminal, '1+2+1+3'),
            'Get all leaves from parse tree in order')
        self.assertTrue(t1.all_leaves(lambda x: len(x.name) == 1),
            'Test predicate on all leaves')
        self.assertFalse(t1.all_leaves(lambda x: x.name == '1'),
            'Test predicate on all leaves')

    def test_context_free_grammar(self):

        nonterminals = map(Nonterminal, 'STF')
        terminals = map(Terminal, '*+()a')
        rules = [
            ProductionRule(Nonterminal('S'), [Nonterminal('S'), Terminal('+'), Nonterminal('T')]),
            ProductionRule(Nonterminal('S'), [Nonterminal('T')]),
            ProductionRule(Nonterminal('T'), [Nonterminal('T'), Terminal('*'), Nonterminal('F')]),
            ProductionRule(Nonterminal('T'), [Nonterminal('F')]),
            ProductionRule(Nonterminal('F'), [Terminal('('), Nonterminal('S'), Terminal(')')]),
            ProductionRule(Nonterminal('F'), [Terminal('a')])
        ]
        start = Nonterminal('S')

        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar(map(Nonterminal, 'ST'), terminals, rules, start)
            # 'Nonterminal appears in rules but not in declared nonterminals'
        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar(nonterminals, map(Terminal, '+()a'), rules, start)
            # 'Terminal appears in rules but not in declared terminals'
        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar(nonterminals, terminals, rules, Nonterminal('X'))
            # 'Start variable is not in declared nonterminals'
        with self.assertRaises(TypeError) as ar:
            ContextFreeGrammar(map(Terminal, 'STF'), terminals, rules, start)
            # 'Terminals given for nonterminals set'
        with self.assertRaises(TypeError) as ar:
            ContextFreeGrammar(terminals, map(Nonterminal, '*+()a'), rules, start)
            # 'Nonterminals given for terminals set'
        with self.assertRaises(TypeError) as ar:
            ContextFreeGrammar(terminals, nonterminals, rules, Terminal('a'))
            # 'Terminal given for start variable'
        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar(nonterminals, terminals, [], start)
            # 'No production rules given'

        G1 = ContextFreeGrammar(rules)
        self.assertEquals(G1.nonterminals, set(nonterminals),
            'Nonterminals found from rules')
        self.assertEquals(G1.terminals, set(terminals),
            'Terminals found from rules')
        self.assertEquals(G1.symbols, set(nonterminals + terminals),
            'Symbols consist of all nonterminals and terminals')
        self.assertEquals(G1.productions, rules[:],
            'Productions same as passed in')
        self.assertEquals(G1.start, start,
            'Start variable is left side of first rule')

        rules_dict = {
            Nonterminal('S') : [(Nonterminal('S'), Terminal('+'), Nonterminal('T')), (Nonterminal('T'),)],
            Nonterminal('T') : [(Nonterminal('T'), Terminal('*'), Nonterminal('F')), (Nonterminal('F'),)],
            Nonterminal('F') : [(Terminal('('), Nonterminal('S'), Terminal(')')), (Terminal('a'),)]
        }

        self.assertEquals(G1.production_dict(), rules_dict,
            'Get production list as a dict')
        self.assertEquals(
            G1.productions_with_left_side(Nonterminal('S')),
            rules[0:2],
            'Get rules with S on left side')

        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar([])
            # 'Empty set of rules'

        G2 = ContextFreeGrammar('''\
S -> S+T | T
T -> T*F | F
F -> (S) | a
''')
        self.assertEquals(G2.productions, rules,
            'Production rules interpreted correctly')
        self.assertEquals(G2.nonterminals, set(nonterminals),
            'Nonterminals collected correctly')
        self.assertEquals(G2.terminals, set(terminals),
            'Terminals collected correctly')
        self.assertEquals(G2.start, start,
            'Start variable chosen correctly')
        self.assertEquals(G2.symbols, set(nonterminals + terminals),
            'Symbols collected correctly')

        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar('')
            # 'Empty set of rules'

        G22 = ContextFreeGrammar('''\
S -> S+T
S -> T
T -> T*F
T -> F
F -> (S)
F -> a
''')
        self.assertEquals(G22.productions, rules,
            'Rules with same left side can be on different lines')

        G7 = ContextFreeGrammar('''\
A -> B -> C
B -> b
C -> c
''')
        self.assertEqual(G7.terminals, set(map(Terminal, ' ->bc')))
        self.assertEqual(G7.nonterminals, set(map(Nonterminal, 'ABC')))

        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar('foobar')
        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar('<noun phrase> -> <det> <noun>')
        with self.assertRaises(ValueError) as ar:
            ContextFreeGrammar('a -> b')

if __name__ == '__main__':
    unittest.main()

