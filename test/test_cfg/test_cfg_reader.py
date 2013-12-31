from cfg.cfg_reader import *
from cfg.core import *
import unittest

class TestCfgReader(unittest.TestCase):

    def test_cfg_reader(self):

        reader = CFGReader()

        S, NP, VP, PP = map(Nonterminal, ['Sentence', 'Noun phrase', 'Verb phrase', 'Prep phrase'])
        and_, det, n, p, v = map(Terminal, ['and', 'det', 'noun', 'prep', 'verb'])

        GRA_expected_rules = map(lambda args: ProductionRule(*args), [
            (S, [NP, VP]),
            (S, [S, PP]),
            (S, [S, and_, S]),
            (NP, [n]),
            (NP, [det, n]),
            (NP, [NP, PP]),
            (NP, [NP, and_, NP]),
            (VP, [v, NP]),
            (VP, [v, S]),
            (PP, [p, NP])
        ])

        GRA_text = '''\
<Sentence> -> <Noun phrase> <Verb phrase> | <Sentence> <Prep phrase>
<Sentence> -> <Sentence> "and" <Sentence>
<Noun phrase> -> "noun" | "det" "noun" | <Noun phrase> <Prep phrase> | <Noun phrase> "and" <Noun phrase>
<Verb phrase> -> "verb" <Noun phrase> | "verb" <Sentence>
<Prep phrase> -> "prep" <Noun phrase>
'''
        GRA = reader.parse(GRA_text)

        self.assertEqual(GRA.productions, GRA_expected_rules)

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('foobar')

        with self.assertRaises(ValueError) as ar:
            reader.parse('')

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('<sentence> := <noun phrase> <verb phrase>')

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('<sentence> <noun phrase> <verb phrase>')

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('-> <noun phrase> <verb phrase>')

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('<sentence> <noun phrase> -> <verb phrase>')

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('<sentence> <noun phrase> <verb phrase> ->')

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('<sentence> -> <noun phrase> -> <verb phrase>')

        with self.assertRaises(CFGReaderError) as ar:
            reader.parse('<sentence> | <noun phrase> <verb phrase>')

        self.assertEqual(
            reader.parse('<Sentence> -> ').productions,
            [ProductionRule(S, [])])

        self.assertEqual(
            reader.parse('<Sentence> -> <Noun phrase> |').productions,
            [ProductionRule(S, [NP]), ProductionRule(S, [])])

        self.assertEqual(
            parse_cfg(GRA_text).productions,
            GRA.productions)

        normal_text = '''\
S -> S+S | S*S | x
'''
        self.assertEqual(
            parse_cfg(normal_text).productions,
            ContextFreeGrammar(normal_text).productions)

        with self.assertRaises(ValueError) as ar:
            parse_cfg('foobar')
        with self.assertRaises(ValueError) as ar:
            parse_cfg('a -> b')
        with self.assertRaises(ValueError) as ar:
            parse_cfg('"the" -> <det>')

if __name__ == '__main__':
    unittest.main()

