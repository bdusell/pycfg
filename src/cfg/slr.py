'''SLR parsing techniques for CFGs.'''

from collections import deque
import pprint
import copy
import cgi

import util.html

import cfg
import automaton
from cfg import ContextFreeGrammar as CFG

END_MARKER = cfg.Marker('$')

class Item(object):
    '''An LR(0) item.'''

    def __init__(self, production, dot_pos):
        if not isinstance(production, cfg.ProductionRule):
            raise TypeError('production is not an instance of ProductionRule')
        if not (0 <= dot_pos <= len(production.right_side)):
            raise ValueError('dot position not within bounds')
        self.production = production
        self.dot_pos = dot_pos

    def after_dot(self):
        if self.dot_pos < len(self.production.right_side):
            return self.production.right_side[self.dot_pos]
        else:
            return None

    def complete(self):
        return self.dot_pos == len(self.production.right_side)

    def dot_advanced(self):
        return Item(self.production, self.dot_pos + 1)

    def __str__(self):
        strs = map(str, self.production.right_side)
        if any(map(lambda x: len(x) > 1, strs)):
            sep = ' '
        else:
            sep = ''
        strs.insert(self.dot_pos, '.')
        return '%s -> %s' % (self.production.left_side, sep.join(strs))

    def __eq__(self, other):
        return isinstance(other, Item) and \
               self.dot_pos == other.dot_pos and \
               self.production == other.production

    def __hash__(self):
        return hash((self.production, self.dot_pos))

    def _html(self, tohtml, middot):
        strs = map(lambda x: tohtml(x), self.production.right_side)
        strs.insert(self.dot_pos, middot)
        return '%s &rarr; %s' % (tohtml(self.production.left_side), ''.join(strs))

    def html(self):
        return self._html(lambda x: x.html(), '&middot;')

    def dot_html(self):
        return self._html(lambda x: x.dot_html(), '&#xb7;')

def is_augmented(grammar):
    '''Check if a grammar's start symbol appears at most once on the left side
    of a production rule and never appears on the right side.'''
    assert isinstance(grammar, cfg.ContextFreeGrammar)
    return len(filter(lambda x: x.left_side == grammar.start, grammar.productions)) <= 1 \
           and not any(filter(lambda x: grammar.start in x.right_side, grammar.productions))

def augmented(grammar):
    '''Augment a grammar with a new start symbol, if necessary.'''
    if is_augmented(grammar):
        return grammar
    else:
        S0 = cfg.PrimedNonterminal.next_unused(grammar.start.name, grammar.nonterminals)
        N = [S0] + list(grammar.nonterminals)
        T = grammar.terminals
        P = [cfg.ProductionRule(S0, [grammar.start])] + grammar.productions
        return cfg.ContextFreeGrammar(N, T, P, S0)

def closure(item, grammar):
    '''Compute the closure of a single item.'''
    assert isinstance(item, Item)
    assert isinstance(grammar, cfg.ContextFreeGrammar)
    result = [item]
    seen = set()
    i = 0
    while i < len(result):
        source_item = result[i]
        A = source_item.after_dot()
        if isinstance(A, cfg.Nonterminal) and A not in seen:
            result.extend(
                filter(lambda x: x not in result,
                       map(lambda x: Item(x, 0), grammar.productions_with_left_side(A))))
            seen.add(A)
        i += 1
    return result

def is_kernel_item(item, grammar):
    '''Tell if an item is a kernel item.'''
    return isinstance(item, Item) and \
           (item.dot_pos > 0 or item.production.left_side == grammar.start)

class Closure(object):
    '''A closure of a set of items.'''

    def __init__(self, kernel_items, grammar):
        '''Construct with a set of kernel items and the grammar to which they
        belong.'''
        for ki in kernel_items:
            assert is_kernel_item(ki, grammar)
        self.kernel_items = kernel_items
        self.grammar = grammar

    def closure_nonterminals(self):
        '''Return the nonterminals on which the closure has transitions to non-
        empty closures.'''

        result = []

        # Get the nonterminals to the right of a dot in the kernel items.
        for item in self.kernel_items:
            X = item.after_dot()
            if isinstance(X, cfg.Nonterminal) and X not in result:
                result.append(X)

        # For every nonterminal found, include any nonterminals which appear
        # at the beginning of rules with those nonterminals on the left side.
        i = 0
        while i < len(result):
            for p in self.grammar.productions_with_left_side(result[i]):
                if len(p.right_side) > 0:
                    X = p.right_side[0]
                    if isinstance(X, cfg.Nonterminal) and X not in result:
                        result.append(X)
            i += 1

        return result

    def closure_items(self):
        '''Enumerate all of the non-kernel or closure items.'''
        return [Item(p, 0) for A in self.closure_nonterminals() for p in self.grammar.productions_with_left_side(A)]

    def items(self):
        '''Enumerate all of the items, kernel and non-kernel.'''
        return self.kernel_items + self.closure_items()

    def goto_kernel_items(self, X):
        '''Enumerate the kernel items to which the closure transitions on a
        certain symbol.'''
        return [item.dot_advanced() for item in self.items() if item.after_dot() == X]

    def goto(self, X):
        '''Return the closure to which this closure transitions on a certain
        symbol.'''
        return Closure(self.goto_kernel_items(X), self.grammar)

    def goto_symbols(self):
        '''Enumerate the symbols on which this closure has transitions to non-
        empty closures.'''
        seen = []
        for item in self.items():
            X = item.after_dot()
            if X is not None and X not in seen:
                seen.append(X)
        return seen

    def transitions(self):
        '''Enumerate all of the transitions leading out of this closure to non-
        empty closures in the form of pairs (X, Ii), where X is a grammar
        symbol and Ii is the closure to which the transition leads.'''
        return [(X, self.goto(X)) for X in self.goto_symbols()]

    def __nonzero__(self):
        '''The closure evaluates to True if and only if it is non-empty.'''
        return bool(self.kernel_items)

    def __eq__(self, other):
        return isinstance(other, Closure) and \
               set(self.kernel_items) == set(other.kernel_items)

    def __str__(self):
        return '\n'.join(map(str, self.items()))

    def html(self):
        lines = ['<tr><td>%s</td></tr>' % i.html() for i in self.items()]
        return '''\
<table>
  %s
</table>
''' % '\n  '.join(lines)

class Automaton(automaton.Automaton):
    '''An SLR automaton.'''

    def __init__(self, grammar):

        assert isinstance(grammar, cfg.ContextFreeGrammar)
        super(automaton.Automaton, self).__init__()

        # Construct initial closure item
        self._grammar = Gp = augmented(grammar)
        [p0] = Gp.productions_with_left_side(Gp.start)

        initial_closure = Closure([Item(p0, 0)], Gp)

        # Add initial state
        self._states = [initial_closure]
        self.add_state(0)

        # Add other states in DFS order
        i = 0
        while i < len(self._states):
            for X, I in self._states[i].transitions():
                index = self._get_state_index(I)
                if index is None:
                    index = len(self._states)
                    self._states.append(I)
                self.add_transition(i, X, index)
            i += 1

    def _get_state_index(self, closure):
        try:
            return self._states.index(closure)
        except ValueError:
            return None

    def augmented_grammar(self):
        return self._grammar

    def num_states(self):
        return len(self._states)

    def closure_states(self):
        return enumerate(self._states)

    def get_state(self, i):
        return self._states[i]

    def state_dot_label(self, s):
        return str(self._states[s])

    def state_dot_html_label(self, s):
        return '''\
<table>
  <tr><td><b>%s</b></td></tr>
  %s
</table>
''' % (s, '\n  '.join(['<tr><td>%s</td></tr>' % item.dot_html() for item in self._states[s].items()]))

    def dot_str(self):
        return super(Automaton, self).dot_str(shape='box')

    def dot_html(self):
        return super(Automaton, self).dot_html(shape='none')

class FirstSetTable(object):
    '''The first set table used for the SLR automaton construction algorithm.
    '''

    def __init__(self, grammar):
        self.grammar = grammar
        self._compute()

    def terminals(self, A):
        return self.table[A][0]

    def nullable(self, A):
        return self.table[A][1]

    def string_first(self, s):
        result = set()
        for X in s:
            if X in self.table:
                terminals, empty = self.table[X]
                result |= terminals
                if not empty:
                    return result, False
            else:
                result.add(X)
                return result, False
        return result, True

    def _compute(self):
        self.table = {A : [set(), False] for A in self.grammar.nonterminals}
        pass_number = 1
        changed = True
        rules = list(self.grammar.productions)
        while changed:
            old_table = copy.deepcopy(self.table)
            changed = False
            next_rules = []
            for p in rules:
                A = p.left_side
                for i, Xi in enumerate(p.right_side):
                    if Xi in self.grammar.nonterminals:
                        self.table[A][0] |= self.table[Xi][0]
                        if not self.table[Xi][1]:
                            next_rules.append(cfg.ProductionRule(A, p.right_side[i:]))
                            break
                    else:
                        self.table[A][0].add(Xi)
                        break
                else:
                    self.table[A][1] = True
            if old_table != self.table:
                changed = True
            rules = next_rules
            pass_number += 1

    def html(self):
        return '''\
<table>
  %s
</table>
''' % '\n  '.join(['<tr><th>%s</th><td>%s</td></tr>' % \
                   (X.html(), util.html.html_set(sorted(T) + ([cfg.Epsilon()] if e else []))) \
                   for X, (T, e) in sorted(self.table.items())])

class FollowSetTable(object):
    '''The follow set table used for the SLR automaton construction and table
    construction algorithms.'''

    def __init__(self, first_sets, automaton):
        self.first_sets = first_sets
        self.automaton = automaton
        self.grammar = automaton.augmented_grammar()
        self._compute()

    def terminals(self, A):
        return self.table[A]

    def _compute(self):
        self.table = {A : set() for A in self.grammar.nonterminals}
        self.table[self.grammar.start].add(END_MARKER)
        changed = True
        while changed:
            changed = False
            old_table = copy.deepcopy(self.table)
            for p in self.grammar.productions:
                A = p.left_side
                for i, B in enumerate(p.right_side):
                    if isinstance(B, cfg.Nonterminal):
                        Bfirst, Bempty = self.first_sets.string_first(p.right_side[i+1:])
                        self.table[B] |= Bfirst
                        if Bempty:
                            self.table[B] |= self.table[A]
            if old_table != self.table:
                changed = True

    def html(self):
        return '''\
<table>
  %s
</table>
''' % '\n  '.join(['<tr><th>%s</th><td>%s</td></tr>' % \
                   (A.html(), util.html.html_set(sorted(T))) \
                   for A, T in sorted(self.table.items())])

class ParsingTable(object):
    '''An SLR parsing table which allows multi-valued entries instead of
    treating shift-reduce and reduce-reduce conflicts as errors.'''

    SHIFT = 'shift'
    REDUCE = 'reduce'
    ACCEPT = 'accept'

    def __init__(self, *args):
        if len(args) == 1:
            self._init_grammar(*args)
        elif len(args) == 2:
            self._init_table(*args)
        else:
            raise TypeError('ParsingTable takes 1 or 2 arguments')

    def _init_grammar(self, grammar):

        self._grammar = grammar
        self._automaton = M = Automaton(grammar)

        self._compute_follow_sets()

        # ACTION table
        # State i is constructed from Ii. The parsing actions for state i are
        # determined as follows:
        # - If [A -> alpha . a beta] is in Ii and GOTO(Ii, a) = Ij, then set
        #   ACTION[i, a] to "shift j." Here a must be a terminal.
        # - If [A -> alpha .] is in Ii, then set ACTION[i, a] to
        #   "reduce A -> alpha" for all a in FOLLOW(A); here A may not be S'.
        # - If [S' -> S .] is in Ii, then set ACTION[i, $] to "accept."

        # GOTO table
        # If GOTO(Ii, A) = Ij, then GOTO[i, A] = j.

        self._action = [{} for i in range(M.num_states())]
        self._goto = [{} for i in range(M.num_states())]

        # Take care of the GOTO table and all of the shift actions.        
        for i, X, j in M.transitions:
            if isinstance(X, cfg.Terminal):
                self._add_action(i, X, (ParsingTable.SHIFT, j))
            else:
                self._goto[i][X] = j

        for i, Ii in M.closure_states():
            for item in Ii.items():
                if item.complete():
                    A = item.production.left_side
                    if A == M.augmented_grammar().start:
                        # Add accept action
                        self._add_action(i, END_MARKER, (ParsingTable.ACCEPT,))
                    else:
                        # Add reduce actions
                        for a in self.follow(A):
                            self._add_action(i, a, (ParsingTable.REDUCE, M.augmented_grammar().productions.index(item.production)))

    def _init_table(self, action, goto):
        assert len(action) == len(goto)
        self._action = [{a : list(actions) for a, actions in row.iteritems()} for row in action]
        self._goto = [{A : state for A, state in row.iteritems()} for row in goto]
        self._grammar = None
        self._terminals = list(set([a for row in self._action for a, actions in row.iteritems()]))
        self._nonterminals = list(set([A for row in self._goto for A, state in row.iteritems()]))

    def action(self, i, a):
        '''The ACTION function takes as arguments a state i and a terminal a
        (or $, the input endmarker). The value of ACTION[i, a] can have one of
        four forms:
        1. Shift j, where j is a state. The action taken by the parser
           effectively shifts input a to the stack, but uses state j to
           represent a.
        2. Reduce A -> beta. The action of the parser effectively reduces beta
           on the top of the stack to head A.
        3. Accept. The parser accepts the input and finishes parsing.
        4. Error. The parser discovers an error in its input and takes some
           corrective action.'''
        return self._action[i].get(a, [])

    def goto(self, i, A):
        '''We extend the GOTO function, defined on sets of items, to states:
        if GOTO[Ii, A] = Ij, then GOTO also maps a state i and a nonterminal A
        to state j.'''
        return self._goto[i].get(A, None)

    def follow(self, A):
        '''To compute FOLLOW(A) for all nonterminals A, apply the following
        rules until nothing can be added to any FOLLOW set.
        - Place $ in FOLLOW(S), where S is the start symbol.
        - If there is a production A -> alpha B beta, then everything in
          FIRST(beta) except epsilon is in FOLLOW(B).
        - If there is a production A -> alpha B, or a production
          A -> alpha B beta, where FIRST(beta) contains epsilon, then
          everything in FOLLOW(A) is in FOLLOW(B).'''
        return self._follow_sets.terminals(A)

    def original_grammar(self):
        '''Return the original grammar which was given.'''
        return self._grammar

    def augmented_grammar(self):
        '''Return the augmented grammar to which the production rule numbers
        correspond, if a grammar was given.'''
        return self._automaton.augmented_grammar()

    def first_sets(self):
        '''Return the first set table.'''
        return self._first_sets

    def follow_sets(self):
        '''Return the follow set table.'''
        return self._follow_sets

    def _compute_first_sets(self, G):
        self._first_sets = FirstSetTable(G)

    def _compute_follow_sets(self):
        M = self._automaton
        G = M.augmented_grammar()
        self._compute_first_sets(G)
        self._follow_sets = FollowSetTable(self._first_sets, M)

    def _add_to_follow_set(self, A, terminals):
        if A not in self._follow_sets: self._follow_sets[A] = terminals
        else: self._follow_sets[A] |= terminals

    def _add_action(self, i, X, action):
        row = self._action[i]
        if X not in row: row[X] = []
        row[X].append(action)

    def _action_set_html(self, i, a):
        actions = self.action(i, a)
        if actions:
            #return '<table>%s</table>' % \
            #       (''.join(['<tr><td>%s</td></tr>' % (self._action_html(action),) for action in self.action(i, a)]))
            return ','.join(self._action_html(action) for action in self.action(i, a))
        return ''

    def _action_html(self, action):
        if action[0] == ParsingTable.SHIFT: return 'sh%d' % action[1]
        elif action[0] == ParsingTable.REDUCE: return 're%s' % action[1]
        elif action[0] == ParsingTable.ACCEPT: return 'acc'

    def _goto_html(self, i, A):
        goto = self.goto(i, A)
        return goto if goto is not None else ''

    def terminals(self):
        if self._grammar is None:
            return self._terminals
        return sorted(self._grammar.terminals) + [END_MARKER]

    def nonterminals(self):
        if self._grammar is None:
            return self._nonterminals
        return sorted(self._grammar.nonterminals)

    def _closure_states(self):
        if self._grammar is None:
            return [(i, None) for i in range(len(self._action))]
        return self._automaton.closure_states()

    def __str__(self):
        return 'ACTION =\n%s\nGOTO =\n%s' % tuple(map(pprint.pformat, (self._action, self._goto)))

    def html(self):
        return '''\
<table>
  <tr><th rowspan="2">STATE</th><th colspan="%d">ACTION</th><th colspan="%d">GOTO</th></tr>
  <tr>%s</tr>
  %s
</table>
''' % (len(self.terminals()), len(self.nonterminals()),
       ''.join(['<th>%s</th>' % X.html() for X in self.terminals() + self.nonterminals()]),
       '\n  '.join(['<tr><th>%d</th>%s</tr>' % \
           (i, ''.join(['<td>%s</td>' % s for s in \
               [self._action_set_html(i, a) for a in self.terminals()] + \
               [self._goto_html(i, A) for A in self.nonterminals()]])) \
           for i, Ii in self._closure_states()]))

