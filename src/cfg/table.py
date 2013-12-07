'''Functions for building SLR parser tables.'''

import sys
from collections import deque
from cfg import ContextFreeGrammar as CFG, Marker

END_MARKER = Marker('$')

def first_sets(G):
    '''Compute the first sets for the variables in a grammar. Return a pair
    whose first element is a dictionary mapping variables to their first sets
    (as sets of Nonterminals) and whose second element is the set of nullable
    variables in the grammar.'''
    result = { A : set() for A in G.nonterminals }
    nullable = set()
    R = deque((p, 0) for p in G.productions)
    Rnext = deque()
    Q = []
    while True:
        m = False
        while R:
            p, i = R.popleft()
            A = p.left_side
            while True:
                if i < len(p.right_side):
                    X = p.right_side[i]
                    if X.is_terminal():
                        m = (X not in result[A]) or m
                        result[A].add(X)
                    else:
                        Q.append((X, A)) # X merges into A
                        if X in nullable:
                            i += 1
                            continue
                        else:
                            Rnext.append((p, i))
                else:
                    m = (A not in nullable) or m
                    nullable.add(A)
                break
        if not m: break
        R, Rnext = Rnext, R
    while True:
        m = False
        for A, B in Q: # A merges into B
            m = bool(result[A] - result[B]) or m
            result[B].update(result[A])
        if not m: break
    return result, nullable

def follow_sets(G, first, nullable):
    '''Compute the follow sets for the variables in a grammar. The first sets
    and nullable variables must be given. Returns a dictionary mapping
    variables to their follow sets (as sets of Nonterminals).'''
    result = { A : set() for A in G.nonterminals }
    result[G.start].add(END_MARKER)
    Q = []
    for p in G.productions:
        A = p.left_side
        n = True
        F = set()
        for X in reversed(p.right_side):
            if X.is_terminal():
                n = False
                F.clear(); F.add(X)
            else:
                result[X].update(F)
                if n:
                    Q.append((A, X)) # A merges into X
                if X not in nullable:
                    F.clear()
                    n = False
                F.update(first[X])
    m = True
    while m:
        m = False
        for A, B in Q: # A merges into B
            m = m or bool(result[A] - result[B])
            result[B].update(result[A])
    return result

class ParseTable(object):
    '''An SLR parse table class which allows for multi-valued entries (shift-
    reduce and reduce-reduce conflicts).'''

    def __init__(self, grammar):
        '''Initalize an empty parse table with respect to a certain grammar.'''
        self._REDUCE = {}
        self._GOTOSHIFT = {}
        self._grammar = grammar

    def add_reduction(self, state, symbol, r):
        '''Add a reduction entry to the cell indexed by state and symbol. r
        should be a production rule.'''
        if state in self._REDUCE: row = self._REDUCE[state]
        else: row = self._REDUCE[state] = {}
        if symbol in row: cell = row[symbol]
        else: cell = row[symbol] = []
        cell.append(r)

    def set_gotoshift(self, state, symbol, s):
        '''Add a goto (if symbol is a nonterminal) or shift (if symbol is a
        terminal) entry to the cell indexed by state and symbol. s should be
        an integer representing a parser state.'''
        if state in self._GOTOSHIFT: row = self._GOTOSHIFT[state]
        else: row = self._GOTOSHIFT[state] = {}
        row[symbol] = s

    def get_reductions(self, state, symbol):
        '''Get all of the reductions (as a list of production rules) at the
        cell indexed by state and symbol.'''
        return self._REDUCE.get(state, {}).get(symbol, [])

    def get_shifts(self, state, symbol):
        '''Get all of the shift instructions in the cell indexed by state and
        symbol as a list of parser state numbers. The list either contains one
        or no states. symbol should be a terminal.'''
        assert symbol.is_terminal()
        sh = self._GOTOSHIFT.get(state, {}).get(symbol, None)
        if sh is None: return []
        else: return [sh]

    ACCEPT_STATE = 1

    def has_accept(self, state, symbol):
        '''Tell whether the cell indexed by state and symbol has an accept
        action, where symbol should be a terminal.'''
        return state == ParseTable.ACCEPT_STATE and symbol == END_MARKER

    def get_goto(self, state, symbol):
        '''Get the goto state in the cell indexed by state and symbol, where
        symbol should be a nonterminal. Return None if there is no such goto
        state.'''
        assert symbol.is_nonterminal()
        return self._GOTOSHIFT.get(state, {}).get(symbol, None)

    def to_normal_form(self):
        '''Return this parse table as a ParseTableNormalForm object.'''
        result = ParseTableNormalForm()
        pindex = { p : i + 1 for i, p in enumerate(self._grammar.productions) }
        for q, row in self._REDUCE.iteritems():
            for a, cell in row.iteritems():
                for p in cell:
                    result.add_reduction(q, a, pindex[p])
        for q, row in self._GOTOSHIFT.iteritems():
            for X, t in row.iteritems():
                result.set_gotoshift(q, X, t)
        result.set_accept(self.ACCEPT_STATE, END_MARKER)
        return result

    def equivalent(self, other):
        '''Tell whether this parse table is equivalent to another one.'''
        return self.to_normal_form().equivalent(other.to_normal_form())

    def tabbed_str(self):
        '''See ParseTableNormalForm.tabbed_str.'''
        return self.to_normal_form().tabbed_str()

    def spaced_str(self):
        '''See ParseTableNormalForm.spaced_str.'''
        return self.to_normal_form().spaced_str()

    def __str__(self):
        return self.to_normal_form().__str__()

class ParseTableNormalForm(object):
    '''A normal form for multi-valued SLR parse tables which facilitates
    comparisons between different parse table representations.'''

    def __init__(self):
        '''Initialize an empty table.'''
        self._reductions = {} # { int : { Terminal : [ProductionRule] } }
        self._gotoshifts = {} # { int : { Symbol : int } }
        self._accepts = {} # { int : set(int) }
        self._terminals = set()
        self._nonterminals = set()

    @property
    def reductions(self):
        '''Get the reduce actions of the table as a dict in the form
        { int : Terminal : [int] }.'''
        return self._reductions

    @property
    def gotoshifts(self):
        '''Get the goto and shift actions of the table as a dict in the form
        { int : { Symbol : int } }.'''
        return self._gotoshifts

    @property
    def accepts(self):
        '''Get the accept actions of the table as a dict in the form
        { int : set(Terminal) }.'''
        return self._accepts

    def add_reduction(self, state, terminal, production):
        self.reductions.setdefault(state, {}).setdefault(terminal, []).append(production)
        self._add_symbol(terminal)

    def set_gotoshift(self, state, symbol, gotoshift_state):
        self.gotoshifts.setdefault(state, {})[symbol] = gotoshift_state
        self._add_symbol(symbol)

    def set_accept(self, state, terminal):
        self._accepts.setdefault(state, set()).add(terminal)
        self._add_symbol(terminal)

    def _add_symbol(self, X):
        if X.is_terminal() and X != END_MARKER:
            self._terminals.add(X)
        elif X.is_nonterminal():
            self._nonterminals.add(X)

    def equivalent(self, other):
        '''Tell whether this table and another are equivalent.'''

        def get_reductions(table, state):
            return dict(map(lambda pair: (pair[0], set(pair[1])), table.reductions.get(state, {}).items()))

        def get_gotoshifts(table, state, symbol):
            return table.gotoshifts.get(state, {}).get(symbol, None)

        def get_accepts(table, state):
            return table.accepts.get(state, set())

        if (self._terminals, self._nonterminals) != (other._terminals, other._nonterminals):
            return False
        Q = deque([(0, 0)])
        mapping = dict(Q)
        while Q:
            s, t = Q.popleft()
            if get_reductions(self, s) != get_reductions(other, t):
                return False
            for X in self._terminals | self._nonterminals:
                ss = get_gotoshifts(self, s, X)
                tt = get_gotoshifts(other, t, X)
                if ss is None and tt is None:
                    continue
                if (ss is None) != (tt is None):
                    return False
                if ss in mapping:
                    if mapping[ss] != tt:
                        return False
                else:
                    mapping[ss] = tt
                    Q.append((ss, tt))
        for s, t in mapping.iteritems():
            if get_accepts(self, s) != get_accepts(other, t):
                return False
        return True

    def tabbed_str(self):
        '''Return a string representation of the table where each cell is
        separated by tabs.'''
        header, rows = self._str_table()
        return '\t' + '\t'.join(header) + '\n' + '\n'.join(i + '\t' + '\t'.join(row) for i, row in rows)

    def spaced_str(self):
        '''Return a string representation of the table where the cells are
        evenly spaced apart.'''
        header, rows = self._str_table()
        colw = lambda x: max(max(map(len, x)) + 1, 8)
        colsp = [colw(s for s, r in rows)] + [colw([header[i]] + [r[i] for s, r in rows]) for i in range(len(header))]
        fmt = ['%-' + str(w) + 's' for w in colsp]
        return fmt[0] % '' + ''.join(f % X for f, X in zip(fmt[1:], header)) + '\n' + '\n'.join(fmt[0] % s + ''.join(f % c for f, c in zip(fmt[1:], r)) for s, r in rows)

    def __str__(self):
        return self.spaced_str()

    def _str_table(self):
        '''Return a pair containing the cells of the top heading of the
        table, and a list of pairs containing the left heading of each row and
        then the cells of the row itself.'''
        # Arrange table
        symbols = sorted(self._terminals) + [END_MARKER] + sorted(self._nonterminals)
        m = {}
        def newrow(): return { X : [] for X in symbols }
        # Add shifts and goto states
        for i, row in self.gotoshifts.items():
            mrow = m[i] = newrow()
            for X, j in row.items():
                m[i][X].append('sh%d' % j if X.is_terminal() else str(j))
        # Add reductions
        for i, row in self.reductions.items():
            if i not in m: mrow = m[i] = newrow()
            else: mrow = m[i]
            for A, P in row.items():
                mrow[A].extend('re%d' % p for p in P)
        # Add accept
        for i, row in self.accepts.items():
            if i not in m: mrow = m[i] = newrow()
            else: mrow = m[i]
            for a in row:
                mrow[a].append('acc')
        states = sorted(m.keys())
        return map(str, symbols), [(str(i), [','.join(map(str, m[i][X])) for X in symbols]) for i in states]

def build_slr_table(G, follow):
    '''Construct an SLR table for a grammar. Its follow sets must be provided.
    '''
    table = ParseTable(G)
    P = { A : [] for A in G.nonterminals }
    for p in G.productions: P[p.left_side].append(p)
    def CLOSE(s):
        while Q:
            p, i = Q.popleft()
            A = p.left_side
            if i < len(p.right_side):
                X = p.right_side[i]
                if X.is_nonterminal() and X not in d:
                    for r in P[X]:
                        Q.append((r, 0))
                if X not in d: dX = d[X] = set()
                else: dX = d[X]
                dX.add((p, i + 1))
            else:
                for a in follow[A]:
                    table.add_reduction(s, a, p)
    def PROCESS(s):
        d.clear()
        CLOSE(s)
        for X, IX in d.items():
            key = frozenset(IX)
            if key in I:
                j = I[key]
            else:
                j = len(I) + 2
                I[key] = j
                states.append((key, j))
            table.set_gotoshift(s, X, j)
    S = G.start
    states = deque()
    I = {}
    d = { S : set() }
    Q = deque((p, 0) for p in P[G.start])
    CLOSE(0)
    Q.extend(d[S])
    del d[S]
    table.set_gotoshift(0, S, 1)
    for X, IX in d.items():
        key = frozenset(IX)
        j = len(I) + 2
        I[key] = j
        states.append((key, j))
        table.set_gotoshift(0, X, j)
    PROCESS(1)
    while states:
        Is, s = states.popleft()
        Q.extend(Is)
        PROCESS(s)
    return table

def get_slr_table(G):
    '''Compute the SLR table for a grammar, computing first and follow sets as
    needed so they do not need to be provided.'''
    return build_slr_table(G, follow_sets(G, *first_sets(G)))

