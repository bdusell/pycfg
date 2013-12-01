from cfg.automaton import *
from cfg.cfg import *
import unittest

class TestAutomaton(unittest.TestCase):

    def test_automaton(self):

        A, B = map(Nonterminal, 'AB')
        M = Automaton()
        M.add_transition(1, A, 2)
        self.assertTrue(M.has_transition(1, A))
        self.assertFalse(M.has_transition(2, A))
        self.assertFalse(M.has_transition(1, B))
        self.assertFalse(M.has_transition(10, B))
        self.assertEqual(M.next_state(1, A), 2)
        self.assertEqual(list(M.transitions), [(1, A, 2)])
        self.assertEqual(set(M.states), set([1, 2]))
        M.add_state(3)
        self.assertEqual(set(M.states), set([1, 2, 3]))

if __name__ == '__main__':
    unittest.main()

