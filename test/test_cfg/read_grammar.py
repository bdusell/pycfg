'''Read grammar specifications for test cases.'''

import re
import sys
from pprint import pprint
from cfg.cfg import ContextFreeGrammar, Terminal, Nonterminal, Marker
from cfg.table import END_MARKER, ParseTableNormalForm

class GrammarTestCase(object):
    '''Contains a CFG and optionally a parse table.'''

    def __init__(self, sections, filename):
        self._sections = sections
        self.filename = filename

    def __getattr__(self, name):
        return self._sections.get(name)

    def __str__(self):
        return self.filename + '\n' + '\n'.join(self._section_strs())

    def _section_strs(self):
        for k, v in self._sections.iteritems():
            yield '''\
==%s==
%s
''' % (k.upper(), v)

label_re = re.compile('^\s*==\s*(.*?)\s*==\s*$')
comment_re = re.compile('^([^#]*)')
shift_re = re.compile('^sh(\d+)$')
reduce_re = re.compile('^re(\d+)$')

def read_test_case(finname):
    '''Read a grammar test case from a file.'''
    label = 'grammar'
    sections = {}
    with open(finname, 'r') as fin:
        for line in filter(None, map(lambda s: comment_re.match(s).group(1).strip(), fin)):
            m = label_re.match(line)
            if m:
                label = m.group(1).lower()
            else:
                sections.setdefault(label, []).append(line)
    def retype(s, t):
        if s in sections:
            sections[s] = t(sections[s])
    retype('grammar', read_grammar)
    def retype_table(lines):
        return read_table(lines, sections['grammar'])
    retype('table', retype_table)
    retype('tablea', retype_table)
    retype('tableb', retype_table)
    retype('result', read_bool)
    return GrammarTestCase(sections, finname)

def read_grammar(lines):
    return ContextFreeGrammar('\n'.join(lines))

def read_table(lines, grammar):
    terminals = grammar.terminals
    nonterminals = grammar.nonterminals
    T = ParseTableNormalForm()
    for line in lines:
        left, right = line.split('=')
        q, X = left.split(',')
        q = int(q)
        is_terminal = False
        if Terminal(X) in terminals:
            is_terminal = True
            X = Terminal(X)
        elif Marker(X) == END_MARKER:
            is_terminal = True
            X = END_MARKER
        if is_terminal:
            actions = right.split(',')
            for a in actions:
                m = shift_re.match(a)
                if m:
                    T.set_gotoshift(q, X, int(m.group(1)))
                else:
                    m = reduce_re.match(a)
                    if m:
                        T.add_reduction(q, X, int(m.group(1)))
                    elif a == 'acc':
                        T.set_accept(q, X)
                    else:
                        raise ValueError('cell value %r not recognized' % a)
        elif Nonterminal(X) in nonterminals:
            T.set_gotoshift(q, Nonterminal(X), int(right))
        else:
            raise ValueError('a symbol in the table is not in the grammar at %s,%s' % (q, X))
    return T

def read_bool(lines):
    s = '\n'.join(lines).strip().lower()
    if s == 'true': return True
    elif s == 'false': return False
    else: return bool(int(s))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: read_grammar.py <file>\n')
        sys.exit(1)
    print read_test_case(sys.argv[1])

