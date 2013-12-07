from cfg.cfg_reader import *
from cfg.cfg import *
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

        GRA = reader.parse('''\
<Sentence> -> <Noun phrase> <Verb phrase> | <Sentence> <Prep phrase>
<Sentence> -> <Sentence> "and" <Sentence>
<Noun phrase> -> "noun" | "det" "noun" | <Noun phrase> <Prep phrase> | <Noun phrase> "and" <Noun phrase>
<Verb phrase> -> "verb" <Noun phrase> | "verb" <Sentence>
<Prep phrase> -> "prep" <Noun phrase>
''')

        self.assertEqual(GRA.productions, GRA_expected_rules)

        with self.assertRaises(Exception) as ar:
            reader.parse('foobar')

if __name__ == '__main__':
    unittest.main()

