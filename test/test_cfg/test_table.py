from cfg.table import *
from read_grammar import *
from glob import glob
import unittest

def get_test_cases(folder):
    return map(read_test_case, sorted(glob('../test/test_cfg/' + folder + '/*')))

table_test_cases = get_test_cases('tables')
grammar_test_cases = get_test_cases('grammars')

class TestTable(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTable, self).__init__(*args, **kwargs)

    def test_normal_form(self):
        '''Show that the SLR table equivalency algorithm works correctly for
        several test cases.'''
        for test in table_test_cases:
            self.assertEqual(test.tablea.equivalent(test.tableb), test.result, str(test))

    def test_build_slr_table(self):
        '''Show that the SLR table is computed correctly for several test
        grammars, using the SLR table equivalency algorithm.'''
        for test in grammar_test_cases:
            if test.table is not None:
                expected_table = test.table
                actual_table = get_slr_table(test.grammar).to_normal_form()
                self.assertTrue(actual_table.equivalent(expected_table))

if __name__ == '__main__':
    unittest.main()

