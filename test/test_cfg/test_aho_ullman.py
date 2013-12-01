from cfg.aho_ullman import *
from cfg.cfg import *
import unittest

CFG = ContextFreeGrammar

class PseudoStream(object):

    def __init__(self):
        self._strs = []

    def write(self, s):
        self._strs.append(s)

    def clear(self):
        del self._strs[:]

    def __str__(self):
        return ''.join(self._strs)

class TestAhoUllman(unittest.TestCase):

    def _test_inputs(self, func):
        with self.assertRaises(TypeError) as ar:
            func('A -> x', map(Terminal, 'x'))
        with self.assertRaises(TypeError) as ar:
            func(CFG('A -> x'), 'x')
        with self.assertRaises(ValueError) as ar:
            func(CFG('A -> x'), map(Terminal, 'y'))

    def _test_expr_input_strings(self, func, G):
        self._test_input_strings(func, G,
            'a a*a a+a*a a*a+a a+a+a'.split(),
            [''] + '+ * aa a+a+ a+a*'.split()
        )

    def _test_input_strings(self, func, G, positive, negative):
        for w in positive:
            self.assertIsNot(func(G, map(Terminal, w)), None,
                'Succeeds on input %r' % w)
        for w in negative:
            with self.assertRaises(ParseError) as ar:
                func(G, map(Terminal, w))

    def test_topdown_backtrack_parse(self):

        self._test_inputs(topdown_backtrack_parse)
        with self.assertRaises(ValueError) as ar:
            topdown_backtrack_parse(CFG('A -> Aa | a'), map(Terminal, 'aaa'))

        # Example 4.1 from Aho & Ullman p. 292-293
        G = CFG('''
E -> T+E
E -> T
T -> F*T
T -> F
F -> a
''')
        w = map(Terminal, 'a+a')
        expected_parse = [1, 4, 5, 2, 4, 5]
        expected_tree = ParseTree(Nonterminal('E'), [
            ParseTree(Nonterminal('T'), [
                ParseTree(Nonterminal('F'), [
                    ParseTree(Terminal('a'))
                ])
            ]),
            ParseTree(Terminal('+')),
            ParseTree(Nonterminal('E'), [
                ParseTree(Nonterminal('T'), [
                    ParseTree(Nonterminal('F'), [
                        ParseTree(Terminal('a'))
                    ])
                ])
            ])
        ])
        expected_output = '''\
(q, 1, e, E$)
|- (q, 1, E1, T+E$)
|- (q, 1, E1 T1, F*T+E$)
|- (q, 1, E1 T1 F1, a*T+E$)
|- (q, 2, E1 T1 F1 a, *T+E$)
|- (b, 2, E1 T1 F1 a, *T+E$)
|- (b, 1, E1 T1 F1, a*T+E$)
|- (b, 1, E1 T1, F*T+E$)
|- (q, 1, E1 T2, F+E$)
|- (q, 1, E1 T2 F1, a+E$)
|- (q, 2, E1 T2 F1 a, +E$)
|- (q, 3, E1 T2 F1 a +, E$)
|- (q, 3, E1 T2 F1 a + E1, T+E$)
|- (q, 3, E1 T2 F1 a + E1 T1, F*T+E$)
|- (q, 3, E1 T2 F1 a + E1 T1 F1, a*T+E$)
|- (q, 4, E1 T2 F1 a + E1 T1 F1 a, *T+E$)
|- (b, 4, E1 T2 F1 a + E1 T1 F1 a, *T+E$)
|- (b, 3, E1 T2 F1 a + E1 T1 F1, a*T+E$)
|- (b, 3, E1 T2 F1 a + E1 T1, F*T+E$)
|- (q, 3, E1 T2 F1 a + E1 T2, F+E$)
|- (q, 3, E1 T2 F1 a + E1 T2 F1, a+E$)
|- (q, 4, E1 T2 F1 a + E1 T2 F1 a, +E$)
|- (b, 4, E1 T2 F1 a + E1 T2 F1 a, +E$)
|- (b, 3, E1 T2 F1 a + E1 T2 F1, a+E$)
|- (b, 3, E1 T2 F1 a + E1 T2, F+E$)
|- (b, 3, E1 T2 F1 a + E1, T+E$)
|- (q, 3, E1 T2 F1 a + E2, T$)
|- (q, 3, E1 T2 F1 a + E2 T1, F*T$)
|- (q, 3, E1 T2 F1 a + E2 T1 F1, a*T$)
|- (q, 4, E1 T2 F1 a + E2 T1 F1 a, *T$)
|- (b, 4, E1 T2 F1 a + E2 T1 F1 a, *T$)
|- (b, 3, E1 T2 F1 a + E2 T1 F1, a*T$)
|- (b, 3, E1 T2 F1 a + E2 T1, F*T$)
|- (q, 3, E1 T2 F1 a + E2 T2, F$)
|- (q, 3, E1 T2 F1 a + E2 T2 F1, a$)
|- (q, 4, E1 T2 F1 a + E2 T2 F1 a, $)
|- (t, 4, E1 T2 F1 a + E2 T2 F1 a, e)
'''
        out = PseudoStream()

        result = topdown_backtrack_parse(G, w, out)

        self.assertEqual(result, expected_parse,
            'Production number list is correct')
        self.assertEqual(LeftParse(G, result).tree(), expected_tree,
            'Parse tree is correct')
        self.assertEqual(str(out), expected_output,
            'State transition output is correct')

        self._test_expr_input_strings(bottomup_backtrack_parse, G)

    def test_bottomup_backtrack_parse(self):

        self._test_inputs(bottomup_backtrack_parse)
        with self.assertRaises(ValueError) as ar:
            bottomup_backtrack_parse(CFG('A -> '), map(Terminal, ''))
        with self.assertRaises(ValueError) as ar:
            bottomup_backtrack_parse(CFG('A -> B | a\nB -> A'), map(Terminal, 'a'))

        # Example 4.4 from Aho & Ullman p. 304-305
        G = CFG('''
E -> E+T
E -> T
T -> T*F
T -> F
F -> a
''')
        w = map(Terminal, 'a*a')
        expected_parse = [2, 3, 5, 4, 5]
        expected_tree = ParseTree(Nonterminal('E'), [
            ParseTree(Nonterminal('T'), [
                ParseTree(Nonterminal('T'), [
                    ParseTree(Nonterminal('F'), [
                        ParseTree(Terminal('a'))
                    ])
                ]),
                ParseTree(Terminal('*')),
                ParseTree(Nonterminal('F'), [
                    ParseTree(Terminal('a'))
                ])
            ])
        ])
        expected_output = '''\
(q, 1, $, e)
|- (q, 2, $a, s)
|- (q, 2, $F, 5s)
|- (q, 2, $T, 45s)
|- (q, 2, $E, 245s)
|- (q, 3, $E*, s245s)
|- (q, 4, $E*a, ss245s)
|- (q, 4, $E*F, 5ss245s)
|- (q, 4, $E*T, 45ss245s)
|- (q, 4, $E*E, 245ss245s)
|- (b, 4, $E*E, 245ss245s)
|- (b, 4, $E*T, 45ss245s)
|- (b, 4, $E*F, 5ss245s)
|- (b, 4, $E*a, ss245s)
|- (b, 3, $E*, s245s)
|- (b, 2, $E, 245s)
|- (q, 3, $T*, s45s)
|- (q, 4, $T*a, ss45s)
|- (q, 4, $T*F, 5ss45s)
|- (q, 4, $T, 35ss45s)
|- (q, 4, $E, 235ss45s)
|- (t, 4, $E, 235ss45s)
'''
        out = PseudoStream()

        result = bottomup_backtrack_parse(G, w, out)

        self.assertEqual(result, expected_parse,
            'Production number list is a right parse in reverse')
        result_tree = RightParse(G, list(reversed(result))).tree()
        self.assertEqual(result_tree, expected_tree,
            'Parse tree is correct')
        self.assertEqual(str(out), expected_output,
            'State transition output is correct')

        self._test_expr_input_strings(bottomup_backtrack_parse, G)

    def test_cyk(self):

        self._test_inputs(cocke_younger_kasami_algorithm)
        with self.assertRaises(ValueError) as ar:
            cocke_younger_kasami_algorithm(CFG('S -> AB\nA -> a\nB -> b\nA -> ABA'), map(Terminal, 'ab'))
        with self.assertRaises(ValueError) as ar:
            cocke_younger_kasami_algorithm(CFG('S -> a | '), map(Terminal, ''))
        with self.assertRaises(ValueError) as ar:
            cocke_younger_kasami_algorithm(CFG('S -> AA | AS | b\nA -> a'), map(Terminal, 'ab'))

        # Example 4.8 from Aho & Ullman p. 315-316
        G = CFG('''
S -> AA | AS | b
A -> SA | AS | a
''')
        w = map(cfg.Terminal, 'abaab')
        expected_table = \
            [[set([Nonterminal('A')]),
              set([Nonterminal('A'), Nonterminal('S')]),
              set([Nonterminal('A'), Nonterminal('S')]),
              set([Nonterminal('A'), Nonterminal('S')]),
              set([Nonterminal('A'), Nonterminal('S')])],
             [set([Nonterminal('S')]),
              set([Nonterminal('A')]),
              set([Nonterminal('S')]),
              set([Nonterminal('A'), Nonterminal('S')])],
             [set([Nonterminal('A')]),
              set([Nonterminal('S')]),
              set([Nonterminal('A'), Nonterminal('S')])],
             [set([Nonterminal('A')]), set([Nonterminal('A'), Nonterminal('S')])],
             [set([Nonterminal('S')])]]
        expected_parse = [2, 6, 2, 4, 3, 6, 2, 6, 3]
        # S(A(a)S(A(S(b)A(a))S(A(a)S(b))))
        S, A, a, b = map(Nonterminal, 'SA') + map(Terminal, 'ab')
        expected_tree = ParseTree(S, [
            ParseTree(A, [
                ParseTree(a)
            ]),
            ParseTree(S, [
                ParseTree(A, [
                    ParseTree(S, [
                        ParseTree(b)
                    ]),
                    ParseTree(A, [
                        ParseTree(a)
                    ])
                ]),
                ParseTree(S, [
                    ParseTree(A, [
                        ParseTree(a)
                    ]),
                    ParseTree(S, [
                        ParseTree(b)
                    ])
                ])
            ])
        ])
        out = PseudoStream()

        T = cocke_younger_kasami_algorithm(G, w, out=out, check=False)
        self.assertEqual(map(list, T), expected_table,
            'CYK parse table is correct')

        result_parse = left_parse_from_parse_table(G, w, T, check=False)
        self.assertEqual(result_parse, expected_parse,
            'Parse derived from parse table is correct')

        result_tree = LeftParse(G, result_parse).tree()
        self.assertEqual(result_tree, expected_tree,
            'Parse tree is correct')

        def parse(G, w):
            T = cocke_younger_kasami_algorithm(G, w, check=False)
            return left_parse_from_parse_table(G, w, T, check=False)

        self._test_input_strings(parse, G,
            'b aa ab baa'.split(),
            'a ba'.split())

    def test_earley_parse(self):

        self._test_inputs(earley_parse)

        # Example 4.10 from Aho & Ullman p. 321-322
        G = CFG('''
E -> T+E
E -> T
T -> F*T
T -> F
F -> (E)
F -> a
''')
        w = map(cfg.Terminal, '(a+a)*a')
        expected_lists = \
[[Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 0, 0),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'),)), 0, 0),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 0, 0),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 0, 0),
  Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 0, 0),
  Item(ProductionRule(Nonterminal('F'), (Terminal('a'),)), 0, 0)],
 [Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 1, 0),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 0, 1),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'),)), 0, 1),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 0, 1),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 0, 1),
  Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 0, 1),
  Item(ProductionRule(Nonterminal('F'), (Terminal('a'),)), 0, 1)],
 [Item(ProductionRule(Nonterminal('F'), (Terminal('a'),)), 1, 1),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 1, 1),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 1, 1),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 1, 1),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'),)), 1, 1),
  Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 2, 0)],
 [Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 2, 1),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 0, 3),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'),)), 0, 3),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 0, 3),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 0, 3),
  Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 0, 3),
  Item(ProductionRule(Nonterminal('F'), (Terminal('a'),)), 0, 3)],
 [Item(ProductionRule(Nonterminal('F'), (Terminal('a'),)), 1, 3),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 1, 3),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 1, 3),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 1, 3),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'),)), 1, 3),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 3, 1),
  Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 2, 0)],
 [Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 3, 0),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 1, 0),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 1, 0),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 1, 0),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'),)), 1, 0)],
 [Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 2, 0),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 0, 6),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 0, 6),
  Item(ProductionRule(Nonterminal('F'), (Terminal('('), Nonterminal('E'), Terminal(')'))), 0, 6),
  Item(ProductionRule(Nonterminal('F'), (Terminal('a'),)), 0, 6)],
 [Item(ProductionRule(Nonterminal('F'), (Terminal('a'),)), 1, 6),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 1, 6),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'),)), 1, 6),
  Item(ProductionRule(Nonterminal('T'), (Nonterminal('F'), Terminal('*'), Nonterminal('T'))), 3, 0),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'), Terminal('+'), Nonterminal('E'))), 1, 0),
  Item(ProductionRule(Nonterminal('E'), (Nonterminal('T'),)), 1, 0)]]
        expected_parse = [6, 4, 6, 4, 2, 1, 5, 6, 4, 3, 2]
        E, T, F, a, plus, mul, left, right = map(Nonterminal, 'ETF') + map(Terminal, 'a+*()')
        expected_tree = ParseTree(E, [
            ParseTree(T, [
                ParseTree(F, [
                    ParseTree(left),
                    ParseTree(E, [
                        ParseTree(T, [
                            ParseTree(F, [
                                ParseTree(a)
                            ])
                        ]),
                        ParseTree(plus),
                        ParseTree(E, [
                            ParseTree(T, [
                                ParseTree(F, [
                                    ParseTree(a)
                                ])
                            ])
                        ])
                    ]),
                    ParseTree(right)
                ]),
                ParseTree(mul),
                ParseTree(T, [
                    ParseTree(F, [
                        ParseTree(a)
                    ])
                ])
            ])
        ])
        out = PseudoStream()

        I = earley_parse(G, w, out=out)

        self.assertEqual(I, expected_lists,
            'Parse lists are correct')

        result_parse = right_parse_from_parse_lists(G, w, I)
        self.assertEqual(result_parse, expected_parse,
            'Parse constructed from parse lists is correct')

        result_tree = RightParse(G, result_parse).tree()
        self.assertEqual(result_tree, expected_tree,
            'Parse tree is correct')

        def parse(G, w):
            I = earley_parse(G, w)
            return right_parse_from_parse_lists(G, w, I)

        self._test_expr_input_strings(parse, G)
        self._test_input_strings(parse, G,
            '(a) a*(a+a) a+(a*a) (((((a)))))'.split(),
            '() (a)) a+() (((((a)))) (((((a))))))'.split())

if __name__ == '__main__':
    unittest.main()

