'''Run the first set construction algorithm on an example grammar and print the
steps to stdout in HTML.'''

import copy
from cfg.core import *
from util.html import *

CFG = ContextFreeGrammar

G = CFG('''
A -> ADx | BC
B -> AC | BB |
C -> y |
D -> z
E -> xC
''')

print '<h1>Grammar G</h1>'
print G.html()

class FirstSetTable(object):

    def __init__(self, grammar):
        self.grammar = grammar

    def compute1(self):
        self.table = {X : [set(), set(), False] for X in grammar.symbols}
        self.initial_pass()
        while self.make_pass():
            print '<h1>Pass</h1>'
            print self.html()

    def initial_pass(self):
        print '<h1>Initial Pass</h1>'
        for p in self.grammar.productions:
            A = p.left_side
            if p.right_side:
                X1 = p.right_side[0]
                self.table[A][0 if isinstance(X1, Nonterminal) else 1].add(X1)
            else:
                self.table[A][2] = True
        print self.html()

    def make_pass(self):
        changed = False
        for A in self.grammar.nonterminals:
            newN = set()
            newT = set()
            newe = False
            for B in self.table[A][0]:
                newN |= self.table[B][0] - self.table[A][0]
                newT |= self.table[B][1] - self.table[A][1]
                newe = newe or ((not self.table[A][2]) and self.table[B][2])
            if newN or newT or newe: changed = True
            self.table[A][0] |= newN
            self.table[A][1] |= newT
            self.table[A][2] = self.table[A][2] or newe
        return changed

    def compute2(self):
        self.table = {A : [set(), set(), False] for A in self.grammar.nonterminals}
        pass_number = 1
        changed = True
        rules = list(self.grammar.productions)
        while changed:
            old_table = copy.deepcopy(self.table)
            print '<h2>Pass #%s</h2>' % pass_number
            print '<table><tr><th>Table</th><th>Rules</th></tr><tr><td>'
            print self.html()
            print '</td><td>'
            print CFG(rules).html()
            print '</td></tr></table>'
            changed = False
            next_rules = []
            for p in rules:
                A = p.left_side
                for i, Xi in enumerate(p.right_side):
                    if Xi in self.grammar.nonterminals:
                        self.table[A][1] |= self.table[Xi][1]
                        if not self.table[Xi][2]:
                            next_rules.append(ProductionRule(A, p.right_side[i:]))
                            break
                    else:
                        self.table[A][1].add(Xi)
                        break
                else:
                    self.table[A][2] = True
            if old_table != self.table:
                changed = True
            rules = next_rules
            pass_number += 1

    def html(self):
        return '''\
<table>
  %s
</table>
''' % '\n  '.join(['<tr><th>%s</th><td>%s</td></tr>' % (X.html(), html_set(sorted(N) + sorted(T) + ([Epsilon()] if e else []))) for X, (N, T, e) in sorted(self.table.items())])

T = FirstSetTable(G)
T.compute2()

