'''A set of pedagogical CFG parsing algorithms.

The algorithms in this module mainly come from:

    Aho, Alfred V., and Ullman, Jeffrey D. "The Theory of Parsing, Translation,
        and Compiling: Volume I: Parsing". Englewood Cliffs, NJ: Prentice-Hall,
        Inc. 1972.
'''

import sys
from pprint import pprint

import cfg, cnf
from util.reindexed_list import Seq

CFG = cfg.ContextFreeGrammar

class ParseError(ValueError):
    '''An exception indicating an unseccessful parse of an input string.'''
    pass

class Parse(object):
    '''The abstract base class for a particular parse or derivation of an input
    string with respect to a certain grammar. A parse is represented as a
    sequence of derivation rule numbers and a grammar. The original input string
    can be recovered by successive applications of these rules starting with the
    start variable according to a policy such as leftmost or rightmost.'''

    def __init__(self, G, parse):
        '''Initialize with a reference grammar and a list of production rule
        numbers specifying the derivation.'''
        self.grammar = G
        self.productions = number_productions(G)
        self.parse = parse

    def tree(self):
        '''Generate a parse tree from this derivation.'''
        raise NotImplementedError()

    def __str__(self):
        if len(self.productions) < 10:
            return ''.join([str(i) for i in self.parse])
        return str(self.parse)

    def __repr__(self):
        return '%s(%r, %r)' % \
               (self.__class__.__name__, self.grammar, self.parse)

class LeftParse(Parse):
    '''A left-most derivation.'''

    def tree(self):
        result, i = self._tree(0)
        assert result.value == self.grammar.start
        assert i == len(self.parse)
        return result

    def _tree(self, i):
        rule = self.productions[self.parse[i]]
        i += 1
        children = []
        for c in rule.right_side:
            if isinstance(c, cfg.Nonterminal):
                tree, i = self._tree(i)
                assert tree.value == c
                children.append(tree)
            else:
                children.append(cfg.ParseTree(c))
        return cfg.ParseTree(rule.left_side, children), i

class RightParse(Parse):
    '''A right-most derivation.'''

    def tree(self):
        result, i = self._tree(-1)
        assert result.value == self.grammar.start
        assert i == -len(self.parse) - 1
        return result

    def _tree(self, i):
        rule = self.productions[self.parse[i]]
        i -= 1
        children = []
        for c in reversed(rule.right_side):
            if isinstance(c, cfg.Nonterminal):
                tree, i = self._tree(i)
                assert tree.value == c
                children = [tree] + children
            else:
                children = [cfg.ParseTree(c)] + children
        return cfg.ParseTree(rule.left_side, children), i

def number_productions(G):
    '''Get the production rules of a grammar as a 1-indexed list.'''
    return Seq(G.productions)

def _check_args(G, w):
    if not isinstance(G, cfg.ContextFreeGrammar):
        raise TypeError('grammar is not an instance of ContextFreeGrammar')
    for ai in w:
        if not isinstance(ai, cfg.Terminal):
            raise TypeError('input symbol is not an instance of Terminal')
    terminals = G.terminals
    for ai in w:
        if ai not in terminals:
            raise ValueError('input terminal is not in the grammar\'s alphabet')

def topdown_state_str(s, i, alpha, beta):
    '''Return a string representing a parser configuration state in the topdown
    backtrack parse algorithm.'''
    if alpha:
        alpha_strs = []
        for a in alpha:
            if type(a) == tuple and len(a) == 2:
                A, ii = a
                alpha_strs.append(str(A) + str(ii))
            else:
                alpha_strs.append(str(a))
        alpha_str = ' '.join(alpha_strs)
    else:
        alpha_str = 'e'
    if beta:
        beta_str = ''.join([str(b) for b in beta])
    else:
        beta_str = 'e'
    return '(%s, %s, %s, %s)' % (s, i, alpha_str, beta_str)

def topdown_backtrack_parse(G, w, out=None):
    '''Top-down backtrack parsing (Aho & Ullman p. 289-291).
    Input: A non-left-recursive CFG G = (Nu, Sigma, P, S) and an input string
    w = a1 a2 ... an, n >= 0. We assume that the productions in P are numbered
    1, 2, ..., p.
    Output: One left parse for w if one exists. Raise a ParseError otherwise.
    '''
    _check_args(G, w)
    if G.left_recursive():
       raise ValueError('grammar is left-recursive')

    def write(s):
        if out is not None: out.write(s)

    N = set(G.nonterminals)
    Sigma = set(G.terminals)
    P = number_productions(G)
    S = G.start
    a = Seq(w)
    n = len(w)
    p = len(P)

    # (1)
    # For each nonterminal A in Nu, order the alternates for A. Let Ai be the
    # index for the ith alternate of A. For example, if
    # A -> alpha1 | alpha2 | ... | alphak are all the A-productions in P and we
    # have ordered the alternates as shown, then A1 is the index for alpha1,
    # A2 is the index for alpha2, and so forth.
    I = {}
    for A in N:
        I[A] = Seq([pp.right_side for pp in P if pp.left_side == A])

    # (2)
    # A 4-tuple (s, i, alpha, beta) will be used to denote a configuration of
    # the algorithm:
    #   (a) s denotes the state of the algorithm
    #   (b) i represents the location of the input pointer. We assume that the
    #       n + 1st "input symbol" is $, the right endmarker.
    #   (c) alpha represents the first pushdown list (L1).
    #   (d) beta represents the second pushdown list (L2).
    # The top of alpha will be on the right and the top of beta will be on the
    # left. L2 represents the "current" left-sentential form, the one which our
    # expansion of nonterminals has produced. Referring to our informal
    # description of top-down parsing in Section 4.1.1, the symbol on top of L2
    # is the symbol labeling the active node of the derivation tree being
    # generated. L1 represents the current history of the choices of alternates
    # made and the input symbol over which the input head has shifted. The
    # algorithm will be in one of three states q, b, or t; q denotes normal
    # operation, b denotes backtracking, and t is the terminating state.

    a.append(cfg.Marker('$'))
    q, b, t = 'qbt'

    # (3)
    # The initial configuration of the algorithm is (q, 1, e, S$)
    s = q
    i = 1
    alpha = []
    beta = [S, cfg.Marker('$')]

    # (4)
    # There are six types of steps. These steps will be described in terms of
    # their effect on the configuration of the algorithm. The heart of the
    # algorithm is to compute successive configurations defined by a "goes to"
    # relation, |-. The notation (s, i, alpha, beta) |- (s', i', alpha', beta')
    # means that if the current configuration is (s, i, alpha, beta), then we
    # are to go next into the configuration (s', i', alpha', beta'). Unless
    # otherwise stated, i can be any integer from 1 to n + 1, alpha a string in
    # (Sigma U I)*, where I is the set of indices for the alternates, and beta a
    # string in (Nu U Sigma)*. The six types of move are as follows:
    #   (a) Tree expansion
    #       (q, i, alpha, A beta) |- (q, i, alpha A1, gamma1 beta)
    #       where A -> gamma1 is a production in P and gamma1 is the first
    #       alternative for A. This step corresponds to an expansion of the
    #       partial derivation tree using the first alternate for the leftmost
    #       nonterminal in the tree.
    #   (b) Successful match of input symbols and derived symbol
    #       (q, i, alpha, a beta) |- (q, i + 1, alpha a, beta)
    #       provided ai = a, i <= n. If the ith input symbol matches the next
    #       terminal symbol derived, we move that terminal symbol from the top
    #       of L2 to the top of L1 and increment the input pointer.
    #   (c) Successful conclusion
    #       (q, n + 1, alpha, $) |- (t, n + 1, alpha, e)
    #       We have reached the end of the input and have found a left-
    #       sentential form which matches the input. We can recover the left
    #       parse from alpha by applying the following homomorphism h to alpha:
    #       h(a) = e for all a in Sigma; h(Ai) = p, where p is the production
    #       number associated with the production A -> gamma, and gamma is the
    #       ith alternate for A.
    #   (d) Unsuccessful match of input symbol and derived symbol
    #       (q, i, alpha, a beta) |- (b, i, alpha, a beta)
    #       We go into backtracking mode as soon as the left-sentential form
    #       being derived is not consistent with the input.
    #   (e) Backtracking on input
    #       (b, i, alpha a, beta) |- (b, i - 1, alpha, a beta)
    #       for all a in Sigma. In the backtracking mode we shift input symbols
    #       back from L1 to L2.
    #   (f) Try next alternate
    #       (b, i, alpha Aj, gammaj beta) |-
    #       (i) (q, i, alpha Aj+1, gammaj+1 beta) if gammaj+1 is the j + 1st
    #           alternate for A. (Note that gammaj is replaced by gammaj+1 on
    #           the top of L2.)
    #       (ii) No configuration, if i = 1, A = S, and there are only j
    #           alternates for S. (This condition indicates that we have
    #           exhausted all possible left-sentential forms consistent with the
    #           input w without having found a parse for w.)
    #       (iii) (b, i, alpha, A beta) otherwise.  (Here, the alternates for A
    #           are exhausted, and we backtrack by removing Aj from L1 and
    #           replacing gammaj by A on L2.

    def goes_to(_s, _i, _alpha, _beta):
        # Successful conclusion
        if _s == q and _i == n + 1 and len(_beta) == 1 and \
           _beta[0] == cfg.Marker('$'):
            return t, _i, _alpha, []
        # Tree expansion
        if _s == q and len(_beta) > 0 and isinstance(_beta[0], cfg.Nonterminal):
            return q, _i, _alpha + [(_beta[0], 1)], \
                   list(I[_beta[0]][1]) + beta[1:]
        # Testing match of input symbol
        if _s == q and len(_beta) > 0 and \
           isinstance(_beta[0], cfg.Terminal):
            # Successful match
            if _i <= n and _beta[0] == a[_i]:
                return q, _i + 1, _alpha + [_beta[0]], _beta[1:]
            # Unsuccessful match
            else:
                return b, _i, _alpha, _beta
        # Backtracking on input
        if _s == b and len(_alpha) > 0 and isinstance(_alpha[-1], cfg.Terminal):
            return b, _i - 1, _alpha[:-1], [_alpha[-1]] + _beta
        # Try next alternate
        if _s == b and len(_alpha) > 0:
            _Aj = _alpha[-1]
            if type(_Aj) == tuple and len(_Aj) == 2:
                _A, _j = _Aj
                _gammaj = I[_A][_j]
                if _beta[:len(_gammaj)] == list(_gammaj):
                # Form is verified
                    # Next alternate
                    if _j+1 <= len(I[_A]):
                        return q, _i, _alpha[:-1] + [(_A, _j+1)], \
                               list(I[_A][_j+1]) + _beta[len(_gammaj):]
                    # Parse failed
                    if _i == 1 and _A == S and len(I[S]) >= _j:
                        return
                    # Backtrack
                    return b, _i, _alpha[:-1], [_A] + _beta[len(_gammaj):]

    def h(ss):
        return [P.index(cfg.ProductionRule(c[0], I[c[0]][c[1]])) \
                for c in ss if not isinstance(c, cfg.Terminal)]

    # The execution of the program is as follows.

    # Step 1: Starting in the initial configuration, compute successive next
    # configurations C0 |- C1 |- ... |- Ci |- ... until no further configurations
    # can be computed.

    write(topdown_state_str(s, i, alpha, beta) + '\n')
    while True:
        next_config = goes_to(s, i, alpha, beta)
        if next_config is None:
            break
        s, i, alpha, beta = next_config
        write('|- ' + topdown_state_str(s, i, alpha, beta) + '\n')

    # Step 2: If the last computed configuration is (t, n + 1, gamma, e), emit
    # h(gamma) and halt. h(gamma) is the first found left parse. Otherwise, emit
    # the error signal.

    if s == t and i == n + 1 and len(beta) == 0:
        return h(alpha)
    else:
        raise ParseError('error')

def bottomup_state_str(s, i, alpha, beta):
    '''Return a string representing a parser configuration state in the bottom-
    up backtrack parse algorithm.'''
    if alpha:
        alpha_str = ''.join(str(a) for a in alpha)
    else:
        alpha_str = 'e'
    if beta:
        beta_str = ''.join(str(b) for b in beta)
    else:
        beta_str = 'e'
    return '(%s, %s, %s, %s)' % (s, i, alpha_str, beta_str)

def bottomup_backtrack_parse(G, w, out=None):
    '''Bottom-up backtrack parsing (Aho & Ullman p. 303-304).
    Input: CFG G = (Nu, Sigma, P, S) with no cycles or e-productions, whose
    productions are numbered 1 to p, and an input string w = a1 a2 ... an,
    n >= 1.
    Output: One right parse for w if one exists. The output "error" otherwise.
    '''
    _check_args(G, w)
    if G.has_empty_rules():
        raise ValueError('grammar has empty rules')
    if G.cyclic():
        raise ValueError('grammar is cyclic')

    N = set(G.nonterminals)
    Sigma = set(G.terminals)
    P = Seq(G.productions)
    S = G.start
    a = Seq(w)
    n = len(w)
    p = len(P)

    def write(s):
        if out is not None: out.write(s)

    # (1) Order the productions arbitrarily.

    # (2) We shall couch our algorithm in the 4-tuple configurations similar to
    # those used in Algorithm 4.1. In a configuration (s, i, alpha, beta)
    #   (a) s represents the state of the algorithm.
    #   (b) i represents the current location of the input pointer. We assume
    #       the n + 1st input symbol is $, the right endmarker.
    #   (c) alpha represents a pushdown list L1 (whose top is on the right).
    #   (d) beta represents a pushdown list L2 (whose top is on the left).
    # As before, the algorithm can be in one of three states q, b, or t. L1 will
    # hold a string of terminals and nonterminals that derives the portion of
    # input to the left of the input pointer. L2 will hold a history of the
    # shifts and reductions necessary to obtain the contents of L1 from the
    # input.

    q, b, t = 'qbt'

    # (3) The initial configuration of the algorithm is (q, 1, $, e)
    s, i, alpha, beta = q, 1, [cfg.Marker('$')], []

    write(bottomup_state_str(s, i, alpha, beta) + '\n')

    # (4) The algorithm itself is as follows. We begin by trying to apply step
    # 1.

    def endswith(ss, ww):
        nn = len(ww)
        if nn > len(ss):
            return False
        return tuple(ss)[-nn:] == tuple(ww)

    def firstsuffix(_alpha, start):
        for ii in xrange(start, p+1):
            if endswith(_alpha, P[ii].right_side):
                return ii

    shift = 's'
    
    # Step 1: Attempt to reduce
    #   (q, i, alpha beta, gamma) |- (q, i, alpha A, j gamma)
    # provided A -> beta is the jth production in P and beta is the first right
    # side in the linear ordering in (1) that is a suffix of alpha beta. The
    # production number is written on L2. If step 1 applies, return to step 1.
    # Otherwise go to step 2.

    while True: # Step 1
        rule_number = firstsuffix(alpha, 1)
        if s == q and rule_number is not None:
            rr = P[rule_number]
            nn = len(rr.right_side)
            alpha[-nn:] = [rr.left_side]
            beta = [rule_number] + beta
            write('|- ' + bottomup_state_str(s, i, alpha, beta) + '\n')
            continue

    # Step 2: Shift
    #   (q, i, alpha, gamma) |- (q, i + 1, alpha ai, s gamma)
    # provided i != n + 1. Go to step 1.
    # If i = n + 1, instead go to step 3.
    # If step 2 is successful, we write the ith input symbol on top of L1,
    # increment the input pointer, and write s on L2, to indicate that a shift
    # has been made.

        if s == q and i != n + 1:
            alpha.append(a[i])
            beta = [shift] + beta
            i += 1
            write('|- ' + bottomup_state_str(s, i, alpha, beta) + '\n')
            continue

    # Step 3: Accept
    #   (q, n + 1, $S, gamma) |- (t, n + 1, $S, gamma)
    # Emit h(gamma), where h is the homomorphism
    #   h(s) = e
    #   h(j) = j    for all production numbers
    # h(gamma) is a right parse of w in reverse. Then halt.
    # If step 3 is not applicable, go to step 4.

        if s == q and i == n + 1 and alpha == [cfg.Marker('$'), S]:
            s = t
            write('|- ' + bottomup_state_str(s, i, alpha, beta) + '\n')
            def h(ss):
                return [sss for sss in ss if isinstance(sss, int)]
            return h(beta)

    # Step 4: Enter backtracking mode
    #   (q, n + 1, alpha, gamma) |- (b, n + 1, alpha, gamma)
    # provided alpha != $S. Go to step 5.

        assert i == n + 1
        s = b
        write('|- ' + bottomup_state_str(s, i, alpha, beta) + '\n')

    # Step 5: Backtracking
    #   (a) (b, i, alpha A, j gamma) |- (q, i, alpha' B, k gamma)
    # if the jth production in P is A -> beta and the next production in the
    # ordering of (1) whose right side is a suffix of alpha beta is B -> beta',
    # numbered k. Note that alpha beta = alpha' beta'. Go to step 1. (Here we
    # have backtracked to the previous reduction, and we try the next
    # alternative reduction.)
    #   (b) (b, n + 1, alpha A, j gamma) |- (b, n + 1, alpha beta, gamma)
    # if the jth production in P is A -> beta and no other alternative
    # reductions of alpha beta remain. Go to step 5. (If no alternative
    # reductions exist, "undo" the reduction and continue backtracking when the
    # input pointer is at n + 1.)
    #   (c) (b, i, alpha A, j gamma) |- (q, i + 1, alpha beta a, s gamma)
    # if i != n + 1, the jth production in P is A -> beta, and no other
    # alternative reductions of alpha beta remain. Here a = ai is shifted onto
    # L1, and an s is entered on L2. Go to step 1.
    #   Here we have backtracked to the previous reduction. No alternative
    # reductions exist, so we try a shift instead.
    #   (d) (b, i, alpha a, s gamma) |- (b, i - 1, alpha, gamma)
    # if the top entry on L2 is the shift symbol. (Here all alternatives at
    # position i have been exhausted, and the shift action must be undone. The
    # input pointer moves left, the terminal symbol ai is removed from L1 and
    # the symbol s is removed from L2.)

        while True:
            if s == b and len(alpha) > 0 and \
               isinstance(alpha[-1], cfg.Nonterminal) and \
               len(beta) > 0 and isinstance(beta[0], int):
                A = alpha[-1]
                j = beta[0]
                if P[j].left_side == A:
                    tempalpha = alpha[:-1] + list(P[j].right_side)
                    k = firstsuffix(tempalpha, j + 1)
                    if k is not None: # Condition (a)
                        rr = P[k]
                        s = q
                        alpha = tempalpha[:-len(rr.right_side)] + [rr.left_side]
                        beta[0] = k
                        write('|- ' + \
                              bottomup_state_str(s, i, alpha, beta) + '\n')
                        break # to step 1
                    elif i == n + 1: # Condition (b)
                        alpha = tempalpha
                        del beta[0]
                        write('|- ' + \
                              bottomup_state_str(s, i, alpha, beta) + '\n')
                        continue # to step 5
                    else: # Condition (c)
                        s = q
                        alpha = tempalpha + [a[i]]
                        i += 1
                        beta[0] = shift
                        write('|- ' + \
                              bottomup_state_str(s, i, alpha, beta) + '\n')
                        break # to step 1
            elif s == b and len(alpha) > 0 and \
                 isinstance(alpha[-1], cfg.Terminal) and \
                 len(beta) > 0 and beta[0] == shift: # Condition (d)
                i -= 1
                alpha.pop()
                del beta[0]
                write('|- ' + bottomup_state_str(s, i, alpha, beta) + '\n')
                continue # to step 5
            raise ParseError('error')
        continue

def ParseTable(n):
    '''Generate an empty parser table for the CYK algorithm.'''
    return [[set() for j in xrange(n - i)] for i in xrange(n)]

def _parse_table_cells_str(cell_strs):
    cell_width = max(map(lambda row: max(map(len, row)), cell_strs))
    n = len(cell_strs)
    index_width = len(str(n))
    width = max(cell_width, index_width)
    format_str = '%-' + str(width) + 's'
    format_cell = lambda c: format_str % c
    sep = '|'
    return '\n'.join(
        [sep.join(
            map(format_cell, \
                [j + 1] + [cell_strs[i][j] for i in xrange(n - j)]
            )
        )
        for j in reversed(xrange(n))] +
        [(' '*len(sep)).join(map(format_cell, [''] + range(1,n+1)))]
    )

def _get_cell_strs(T):
    return [[', '.join(map(str, c)) for c in row] for row in T]

def parse_table_str(T):
    '''Return a printable string displaying a CYK parse table.'''
    return _parse_table_cells_str(_get_cell_strs(T))

def parse_table_iterators_str(T, coords):
    '''Return a printable string displaying a CYK parse table with certain
    cells marked, i.e. to mark iterators.'''
    cell_strs = _get_cell_strs(T)
    for i, j in coords:
        i -= 1
        j -= 1
        if i >= 0 and j >= 0:
            cell_strs[i][j] = '[%s]' % cell_strs[i][j]
    return _parse_table_cells_str(cell_strs)

def _cyk_check_args(G, w, check):
    _check_args(G, w)
    if G.has_empty_rules():
        raise ValueError('grammar has empty rules')
    if check:
        if not cnf.is_cnf(G):
            raise ValueError('grammar is not in Chomsky normal form')

def cocke_younger_kasami_algorithm(G, w, out=None, check=True):
    '''Cocke-Younger-Kasami parsing algorithm. (Aho & Ullman p. 315)
    Input: A Chomsky normal form CFG G = (Nu, Sigma, P, S) with no e-production
    and an input string w = a1 a2 ... an in Sigma+.
    Output: The parse table T for w such that tij contains A if and only if
    A =>+ ai ai+1 ... ai+j-1.'''

    _cyk_check_args(G, w, check)

    Nu = set(G.nonterminals)
    Sigma = set(G.terminals)
    P = Seq(G.productions)
    S = G.start
    a = Seq(w)
    n = len(a)

    T = ParseTable(n)
    t = Seq(map(Seq, T))

    def write(s):
        if out is not None: out.write(s)

    write(parse_table_str(T) + '\n\n')

    # (1) Set ti1 = {A | A -> ai is in P} for each i. After this step, if ti1
    # contains A, then clearly A =>+ ai.
    # To compute ti1 for all i merely requires that we set i = 1, then
    # repeatedly set ti1 to {A | A -> ai is in P}, test if i = n, and if not,
    # increment i by 1.
    for i in xrange(1, n+1):
        t[i][1] |= set([pp.left_side for pp in P if pp.right_side[0] == a[i]])
        write(parse_table_str(T) + '\n\n')

    # (2) Assume that tij' has been computed for all i, 1 <= i <= n, and all j',
    # 1 <= j' < j. Set
    #   tij = {A | for some k, 1 <= k < j, A -> BC is in P,
    #              B is in tik, and C is in ti+k,j-k}.
    # (3) Repeat step (2) until tij is known for all 1 <= i <= n, and 1 <= j <=
    # n - 1 + 1.

    # We must perform the following steps to compute tij:
    #   (1) Set j = 1.
    #   (2) Test if j = n. If not, increment j by 1 and perform line(j), a
    #       procedure to be defined below.
    #   (3) Repeat step (2) until j = n.

    # The procedure line(j) computes all entries tij such that 1 <= i < n - j +
    # 1. It embodies the procedure outlined above to compute tij. It is defined
    # as follows (we assume that all tij initially have the value emptyset):
    #   (1) Let i = 1 and j' = n - j + 1.
    #   (2) Let k = 1.
    #   (3) Let k' = i + k and j'' = j - k.
    #   (4) Examine tik and tk'j''. Let
    #           tij = tij U {A | A -> BC is in P, B in tik, and C in tk'j''}.
    #   (5) Increment k by 1.
    #   (6) If k = j, go to step (7). Otherwise, go to step (3).
    #   (7) If i = j', halt. Otherwise do step (8).
    #   (8) Increment i by 1 and go to step (2).

    def line(j):
        jj = n - j + 1
        for i in xrange(1, jj + 1):
            for k in xrange(1, j + 1):
                kk = i + k
                jjj = j - k
                if jjj < 1:
                    continue
                t[i][j] |= set([pp.left_side for pp in P \
                                if len(pp.right_side) == 2 and \
                                jjj >= 1 and \
                                pp.right_side[0] in t[i][k] and \
                                pp.right_side[1] in t[kk][jjj]])
                write(
                    parse_table_iterators_str(
                        T, [(i, j), (i, k), (kk, jjj)]
                    ) + '\n\n'
                )

    for _j in xrange(1, n+1):
        line(_j)

    return t

def left_parse_from_parse_table(G, w, T, check=True):
    '''Left parse from parse table. (Aho & Ullman p. 318-319)
    Input: A Chomsky normal form CFG G = (Nu, Sigma, P, S) in which the
    productions of P are numbered from 1 to p, an input string w = a1 a2 ... an,
    and the parse table T for w constructed by the CYK algorithm.
    Output: A left parse for w or the signal "error."'''

    _cyk_check_args(G, w, check)

    Nu = G.nonterminals
    Sigma = G.terminals
    P = Seq(G.productions)
    S = G.start
    a = Seq(w)
    n = len(a)
    t = T

    # We shall describe a recursive routine gen(i, j, A) to generate a left
    # parse corresponding to the derivation A =>+lm ai ai+1 ... ai+j-1. The
    # routine gen(i, j, A) is defined as follows:
    #   (1) If j = 1 and the mth production in P is A -> ai, then emit the
    #       production number m.
    #   (2) If j > 1, k is the smallest integer, 1 <= k < j, such that for some
    #       B in tik and C in ti+k,j-k, A -> BC is a production in P, say the
    #       mth. (There may be several choices for A -> BC here. We can
    #       arbitrarily choose the one with the smallest m.) Then emit the
    #       production number m and execute gen(i, k, B), followed by
    #       gen(i + k, j - k, C).

    def gen(i, j, A):
        if j == 1:
            p = cfg.ProductionRule(A, [a[i]])
            if p in P:
                return [P.index(p)]
            else:
                raise ParseError('error')
        elif j > 1:
            m = None
            stop = False
            for k in xrange(1, j):
                for B in t[i][k]:
                    for C in t[i+k][j-k]:
                        p = cfg.ProductionRule(A, [B, C])
                        if p in P:
                            m = P.index(p)
                            stop = True
                            break
                    if stop:
                        break
                if stop:
                    break
            if m is None:
                raise ParseError('error')
            return [m] + gen(i, k, B) + gen(i + k, j - k, C)
        return []

    # The algorithm, then, is to execute gen(1, n, S), provided that S is in
    # t1n. If S is not in t1n, emit the message "error."

    # We should mention that this algorithm can be made to run faster if, when
    # we construct the parse table and add a new entry, we place pointers to
    # those entries which cause the new entry to appear.

    return gen(1, n, S)

class Item(object):
    '''An "item" for a CFG rule.'''

    def __init__(self, production, k, i):
        assert isinstance(production, cfg.ProductionRule)
        self.production = production
        self.k = k
        self.i = i

    def __str__(self):
        strs = map(str, self.production.right_side)
        if any(map(lambda x: len(x) > 1, strs)):
            sep = ' '
        else:
            sep = ''
        strs.insert(self.k, '.')
        return '[%s -> %s, %s]' % (self.production.left_side, sep.join(strs),
                                   self.i)

    def __repr__(self):
        return 'Item(%r, %r, %r)' % (self.production, self.k, self.i)

    def __eq__(self, y):
        return isinstance(y, Item) and self.production == y.production and \
               self.k == y.k and self.i == y.i

    @property
    def m(self):
        return len(self.production.right_side)

    def after_dot(self):
        if self.k < self.m:
            return self.production.right_side[self.k]
        else:
            return None

def parse_list_str(I, j):
    '''Return a printable string displaying a parse list of Earley's algorithm.
    '''
    return '\n'.join(['I%s' % j] + map(str, I[j]))

def earley_parse(G, w, out=None):
    '''Earley's parsing algorithm. (Aho & Ullman p. 321)
    Input: CFG G = (Nu, Sigma, P, S) and an input string w = a1 a2 ... an in
    Sigma*.
    Output: The parse lists I0, I1, ..., In.'''

    _check_args(G, w)
    
    Nu = G.nonterminals
    Sigma = G.terminals
    P = Seq(G.productions)
    S = G.start
    a = Seq(w)
    n = len(a)

    def write(s):
        if out is not None: out.write(s)

    I = [[] for ii in xrange(n+1)]

    # First, we construct I0 as follows:

    # (1) If S -> alpha is a production in P, add [S -> .alpha, 0] to I0.
    for p in P:
        if p.left_side == S:
            I[0].append(Item(p, 0, 0))

    # Now perform steps (2) and (3) until no new items can be added to I0.
    added = True
    while added:
        added = False

        write(parse_list_str(I, 0) + '\n\n')
        
    # (2) If [B -> gamma., 0] is on I0, add [A -> alpha B . beta, 0] for all
    # [A -> alpha . B beta, 0] on I0. (Note that gamma can be e. This is the
    # way rule (2) becomes applicable initially.)
        new_items = []
        for item in I[0]:
            if item.m == item.k and item.i == 0:
                for other_item in I[0]:
                    if other_item.after_dot() == item.left_side and \
                       other_item.i == 0:
                        new_item = Item(other_item.production,
                                        other_item.k + 1,
                                        0)
                        if new_item not in I[0] and new_item not in new_items:
                            new_items.append(new_item)
                            added = True
        I[0].extend(new_items)

    # (3) Suppose that [A -> alpha . B beta, 0] is an item in I0. Add to I0, for
    # all productions in P of the form B -> gamma, the item [B -> . gamma, 0]
    # (provided this item is not already in I0).

        new_items = []
        for item in I[0]:
            B = item.after_dot()
            if B is not None and B.is_nonterminal():
                for production in P:
                    if production.left_side == B:
                        new_item = Item(production, 0, 0)
                        if new_item not in I[0] and new_item not in new_items:
                            new_items.append(new_item)
                            added = True
        I[0].extend(new_items)

    # We now construct Ij, having constructed I0, I1, ..., Ij-1.
    for j in xrange(1, n+1):

    # (4) For each [B -> alpha . a beta, i] in Ij-1 such that a = aj, add
    # [B -> alpha a . beta, i] to Ij.
        for item in I[j-1]:
            if item.after_dot() == a[j]:
                new_item = Item(item.production, item.k+1, item.i)
                if new_item not in I[j]:
                    I[j].append(new_item)

    # Now perform steps (5) and (6) until no new items can be added.

        added = True
        while added:
            added = False

            write(parse_list_str(I, j) + '\n\n')

    # (5) Let [A -> gamma ., i] be an item in Ij. Examine Ii for items of the
    # form [B -> alpha . A beta, k]. For each one found, we add
    # [B -> alpha A . beta, k] to Ij.

            new_items = []
            for item in I[j]:
                if item.m == item.k:
                    A = item.production.left_side
                    for other_item in I[item.i]:
                        if other_item.after_dot() == A:
                            new_item = Item(other_item.production,
                                            other_item.k+1,
                                            other_item.i)
                            if new_item not in I[j] and \
                               new_item not in new_items:
                                new_items.append(new_item)
                                added = True
            I[j].extend(new_items)

    # (6) Let [A -> alpha . B beta, i] be an item in Ij. For all B -> gamma in
    # P, we add [B -> . gamma, j] to Ij.

            new_items = []
            for item in I[j]:
                B = item.after_dot()
                if B is not None and B.is_nonterminal():
                    for production in P:
                        if production.left_side == B:
                            new_item = Item(production, 0, j)
                            if new_item not in I[j] and \
                               new_item not in new_items:
                                new_items.append(new_item)
                                added = True
            I[j].extend(new_items)

    # Note that consideration of an item with a terminal to the right of the dot
    # yields no new items in steps (2), (3), (5), and (6).

    # The algorithm, then, is to construct Ij for 0 <= j <= n.

    return I

def right_parse_from_parse_lists(G, w, I, out=None):
    '''Construction of a right parse from the parse lists. (Aho & Ullman p. 328)
    Input: A cycle-free CFG G = (Nu, Sigma, P, S) with the productions in P
    numbered from 1 to p, an input string w = a1 ... an, and the parse lists
    I0, I1, ..., In for w.
    Output: pi, a right parse for w, or an "error" message.'''

    _check_args(G, w)
    if G.cyclic():
        raise ValueError('grammar is cyclic')

    Nu = G.nonterminals
    Sigma = G.terminals
    P = Seq(G.productions)
    S = G.start
    a = Seq(w)
    n = len(a)

    def write(s):
        if out is not None: out.write(s)

    # If no item of the form [S -> alpha ., 0] is on In, then w is not in L(G),
    # so emit "error" and halt. Otherwise, initialize the parse pi to e and
    # execute the routine R([S -> alpha ., 0], n) where the routine R is defined
    # as follows:

    # Routine R([A -> beta ., i], j):
    def R(item, j):
        write('R(%s, %s)' % (item, j))
        assert item.m == item.k
        A = item.production.left_side
        beta = item.production.right_side
        i = item.i
    #   (1) Let pi be h followed by the previous value of pi, where h is the
    #       number of production A -> beta. (We assume that pi is a global
    #       variable.)
        h = P.index(item.production)
        pi.insert(0, h)
    #   (2) If beta = X1 X2 ... Xm, set k = m and l = j.
        X = Seq(beta)
        m = len(X)
        k = m
        l = j
    #   (3) (a) If Xk is in Sigma, subtract 1 from both k and l.
    #       (b) If Xk is in Nu, find an item [Xk -> gamma ., r] in Il for some
    #           r such that [A -> X1 X2 ... Xk-1 . Xk ... Xm, i] is in Ir. Then
    #           execute R([Xk -> gamma ., r], l). Subtract 1 from k and set
    #           l = r.
        while True:
            if X[k] in Sigma:
                k -= 1
                l -= 1
            elif X[k] in Nu:
                for other_item in I[l]:
                    if other_item.production.left_side == X[k] and \
                       other_item.m == other_item.k:
                        gamma = other_item.production.right_side
                        r = other_item.i
                        check_item = Item(cfg.ProductionRule(A, beta), k-1, i)
                        if check_item in I[r]:
                            R(other_item, l)
                            k -= 1
                            l = r
                            break
    #   (4) Repeat step (3) until k = 0. Halt.
            if k == 0:
                break

    for _item in I[n]:
        if _item.production.left_side == S and _item.k == _item.m and \
           _item.i == 0:
            pi = []
            R(_item, n)
            return pi
    raise ParseError('error')
