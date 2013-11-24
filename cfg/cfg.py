'''A Context Free Grammar class along with peripheral classes and algorithms.
'''

import itertools
import cgi

from util.digraph import Digraph
from util.tree import Tree
from util.mixin import Comparable, Keyed, Subscripted, Primed
from util.moreitertools import powerset

class Symbol(Keyed, Comparable):
    '''A base class for symbols which appear in a grammar. Terminal and
    Nonterminal classes derive from this.'''

    def __init__(self, identifier):
        '''Initialize the symbol with a string used to distinguish it.'''
        assert isinstance(identifier, str)
        self._identifier = identifier

    @property
    def name(self):
        '''Return the symbol's name or identifier.'''
        return self._identifier

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._identifier)

    def __eq__(self, y):
        '''Symbols must be of the same class and have the same identifier to be
        considered equal.'''
        return isinstance(y, self.__class__) and \
               self._identifier == y._identifier

    def __key__(self):
        return (self.sort_num(), self.name)

    def sort_num(self):
        return 0

    def html(self):
        '''Return a suitable representation of the object in html.'''
        return '<i>%s</i>' % cgi.escape(self.name)

    def dot_html(self):
        return self.html()

class Nonterminal(Symbol):
    '''A class for nonterminal symbols, or variables, in a grammar.'''

    def __str__(self):
        '''The nonterminal's name appears in angle brackets unless it is a
        single capital letter.'''
        if len(self.name) != 1 or not self.name.isupper():
            return '<%s>' % self.name
        return self.name

    def is_nonterminal(self):
        return True

    def is_terminal(self):
        return False

    def sort_num(self):
        return -1

    def html(self):
        return self._html_interp()

    def html_insert(self, html):
        return self._html_interp(insert=html)

    def html_after(self, html):
        return self._html_interp(after=html)

    def dot_html(self):
        return self._html_interp(dot=True)

    def _html_interp(self, insert = '', after = '', dot = False):
        if len(self.name) != 1:
            return '&lang;%s&rang;%s%s' % (cgi.escape(self.name), insert, after)
        tag = 'i' if dot else 'var'
        return '<%s>%s%s</%s>%s' % (tag, cgi.escape(self.name), insert, tag, after)

def _next_unused(original, taken, start, type_):
    while True:
        result = type_(original, start)
        if result in taken: start += 1
        else: break
    return result

class SubscriptedNonterminal(Subscripted, Nonterminal):
    '''A nonterminal with a subscript.'''

    def __init__(self, name, subscript):
        Subscripted.__init__(self, subscript)
        Nonterminal.__init__(self, name)

    def __repr__(self):
        return 'SubscriptedNonterminal(%r, %r)' % (self.name, self.subscript)

    def html(self):
        return self.html_after('<sub>%s</sub>' % cgi.escape(str(self.subscript)))

    @staticmethod
    def next_unused(name, nonterminals):
        return _next_unused(name, nonterminals, 1, SubscriptedNonterminal)

class PrimedNonterminal(Primed, Nonterminal):

    def __init__(self, name, num_primes):
        Primed.__init__(self, num_primes)
        Nonterminal.__init__(self, name)

    def __repr__(self):
        return 'PrimedNonterminal(%r, %r)' % (self.name, self.num_primes)

    def html(self):
        if self.num_primes == 2:
            primestr = '&Prime;' # double prime
        elif self.num_primes == 3:
            primestr = '&#x2034;' # triple prime
        elif self.num_primes == 4:
            primtstr = '&#x2057;' # quadruple prime
        else:
            primestr = '&prime;' * self.num_primes
        return self.html_insert(primestr)

    def dot_html(self):
        return self._html_interp(insert = '&#x27;' * self.num_primes, dot=True)

    @staticmethod
    def next_unused(name, nonterminals):
        return _next_unused(name, nonterminals, 1, PrimedNonterminal)

class Terminal(Symbol):
    '''A class for terminal symbols in a grammar.'''

    def __str__(self):
        '''The terminal's identifier appears in double quotes unless it is a
        single lowercase letter.s'''
        if len(self.name) != 1 or self.name.isupper():
            return '"%s"' % self.name
        return self.name

    def is_nonterminal(self):
        return False

    def is_terminal(self):
        return True

    def html(self):
        return '<code>%s</code>' % cgi.escape(self.name)

    def dot_html(self):
        return '<b>%s</b>' % cgi.escape(self.name)

    def sort_num(self):
        return 1

class Marker(Terminal):
    '''A class for special marker symbols e.g. at the bottom of stacks, the ends
    of input tapes, etc. Traditionally represented as $, but may be initialized
    with any identifier. It is equal to no terminal symbol.'''

    def html(self):
        if len(self.name) == 1:
            return cgi.escape(self.name)
        return Nonterminal.html(self)

    def sort_num(self):
        return 3

class Epsilon(Terminal):

    def __init__(self):
        super(Epsilon, self).__init__('')

    def html(self):
        return '<i>&epsilon;</i>'

    def sort_num(self):
        return 2

class ProductionRule(object):
    '''A class for production rules in a context-free grammar. The left side
    must consist of a single variable, and the right side must be a string of
    terminals or nonterminals.'''

    def __init__(self, left_side, right_side):
        '''Initialize the rule with a variable for the left side and a sequence
        of symbols for the right side.'''
        assert isinstance(left_side, Symbol)
        for s in right_side:
            assert isinstance(s, Symbol)
        self.left_side = left_side
        self.right_side = tuple(right_side)

    def __str__(self):
        '''Represented with arrow notation. The symbols on the right side are
        separated by spaces unless all of their string representations are a
        aingle character long.'''
        if all(map(lambda x: len(str(x)) == 1, self.right_side)):
            sep = ''
        else:
            sep = ' '
        return '%s -> %s' % (self.left_side, sep.join([str(s) for s in \
                                                      self.right_side]))

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, repr(self.left_side), \
                               repr(self.right_side))

    def __eq__(self, o):
        '''Tests if the left and right side are equal.'''
        return isinstance(o, ProductionRule) and \
               self.left_side == o.left_side and \
               self.right_side == o.right_side

    def __hash__(self):
        return hash((self.left_side, self.right_side))

    def _html(self, tohtml):
        if self.right_side:
            if any(filter(lambda X: isinstance(X, Terminal) and len(X.name) != 1, self.right_side)):
                sep = ' '
            else:
                sep = ''
            right = sep.join([tohtml(X) for X in self.right_side])
        else:
            right = '<i>&epsilon;</i>'
        return '%s &rarr; %s' % (tohtml(self.left_side), right)

    def html(self):
        return self._html(lambda x: x.html())

    def dot_html(self):
        return self._html(lambda x: x.dot_html())

class ParseTree(Tree(Symbol)):
    '''A class for parse trees or syntax trees.'''
    pass

class ContextFreeGrammar(object):

    def __init__(self, *args):
        '''Initialize a context-free grammar in one of three ways:
        1. ContextFreeGrammar(string)
            The CFG is built from a string listing its production rules which
            follows a familiar syntax that allows test CFGs to be specified
            quickly and easily. The names of all symbols are one letter long,
            and all capital letters are treated as variables. Each line of the
            string is of the form
                A -> X1 | X2 | ... | Xn
            where A is a variable and the Xi are sentential forms. The CFG's
            terminal and nonterminal symbols are inferred from the productions
            given. The left side of the first rule is made the start variable.
        2. ContextFreeGrammar(list)
            The CFG is built from a list of production rule objects. The
            nonterminals, terminals, and start variable are all inferred from
            this listing.
        3. ContextFreeGrammar(Nu, Sigma, P, S)
            The CFG's nonterminals (Nu), terminals (Sigma), production rules
            (P), and start variable (S) are explicitly given.'''
        if len(args) == 1:
            if isinstance(args[0], str):
                self._init_string(*args)
            else:
                self._check_productions(*args)
                self._init_productions(*args)
        elif len(args) == 4:
            self._check_tuple(*args)
            self._init_tuple(*args)
        else:
            raise TypeError('ContextFreeGrammar takes 1 or 4 arguments')

    @property
    def nonterminals(self):
        '''Return a set of the nonterminal symbols which appear in the grammar.
        '''
        return self._get_symbols_of_type(Nonterminal) | \
               set(p.left_side for p in self._productions) | \
               self._extra_nonterminals
    
    @property
    def terminals(self):
        '''Return a set of the terminal symbols which appear in the grammar.'''
        return self._get_symbols_of_type(Terminal) | \
               self._extra_terminals

    @property
    def productions(self):
        '''Return a list of the productions of the grammar in order.'''
        return self._productions

    @property
    def start(self):
        '''Return the grammar's start variable.'''
        return self._start

    @property
    def symbols(self):
        '''Return a list of the grammar's nonterminals and terminals.'''
        return list(self.nonterminals) + list(self.terminals)

    def _get_symbols_of_type(self, T):
        return set(s for p in self._productions for s in p.right_side \
                   if isinstance(s, T))

    def _init_string(self, string):
        lines = filter(None, string.split('\n'))
        split_sides = [[w.strip() for w in line.split('->')] for line in lines]
        for left, right in split_sides:
            assert len(left) == 1 and left.isupper()
        self._extra_nonterminals = set()
        self._extra_terminals = set()
        self._productions = []
        for left, right in split_sides:
            left_side = Nonterminal(left)
            for symbol_string in right.split('|'):
                right_side = []
                for c in symbol_string.strip():
                    if c.isupper():
                        right_side.append(Nonterminal(c))
                    else:
                        right_side.append(Terminal(c))
                self._productions.append(ProductionRule(left_side, right_side))
        self._start = self._productions[0].left_side

    def _check_productions(self, productions):
        assert productions
        for p in productions:
            assert isinstance(p, ProductionRule)

    def _init_productions(self, productions):
        self._extra_nonterminals = set()
        self._extra_terminals = set()
        self._productions = list(productions)
        self._start = productions[0].left_side

    def _check_tuple(self, nonterminals, terminals, productions, start):
        # Check nonterminals
        for n in nonterminals:
            assert isinstance(n, Nonterminal)
        # Check terminals
        for t in terminals:
            assert isinstance(t, Terminal)
        # Check production rules
        for p in productions:
            assert isinstance(p, ProductionRule)
            assert p.left_side in nonterminals
            for s in p.right_side:
                assert s in terminals or s in nonterminals
        # Check start symbol
        assert isinstance(start, Nonterminal)
        assert start in nonterminals

    def _init_tuple(self, nonterminals, terminals, productions, start):
        # Assign members
        self._productions = list(productions)
        self._extra_nonterminals = set(nonterminals) - \
                                   self._get_symbols_of_type(Nonterminal)
        self._extra_terminals = set(terminals) - \
                                self._get_symbols_of_type(Terminal)
        self._start = start

    def __str__(self):
        return '\n'.join(str(p) for p in self.productions)

    def __repr__(self):
        return "%s('''\n%s\n''')" % (self.__class__.__name__, self)

    def _html(self, tohtml):
        rows = ['<tr><td>%s</td></tr>' % tohtml(p) for p in self.productions]
        return '''\
<table>
  %s
</table>
''' % '\n  '.join(rows)

    def html(self):
        return self._html(lambda x: x.html())

    def dot_html(self):
        return self._html(lambda x: x.dot_html())

    def production_dict(self):
        '''Return a mapping of variables to the sentences they produce, in
        order.'''
        result = {n : [] for n in self.nonterminals}
        for p in self.productions:
            result[p.left_side].append(p.right_side)
        return result

    def productions_with_left_side(self, left_side):
        '''Return all production rules in the grammar with a certain
        symbol on the left side.'''
        return filter(lambda x: x.left_side == left_side, self.productions)

    def left_recursive(self):
        '''Return whether a grammar is left-recursive. FIXME: Does not detect
        hidden left recursion.'''
        return self._detect_cycle(lambda right_side: len(right_side) >= 1)

    def has_empty_rules(self):
        '''Return whether a grammar has e-productions.'''
        for rule in self.productions:
            if not rule.right_side:
                return True
        return False

    def cyclic(self):
        '''Return whether a grammar has a cycle. FIXME: Does not detect hidden
        cycles.'''
        return self._detect_cycle(lambda right_side: len(right_side) == 1)

    def _detect_cycle(self, condition):
        G = Digraph()
        for rule in self.productions:
            if condition(rule.right_side) and \
               isinstance(rule.right_side[0], Nonterminal):
                G.add_edge(rule.left_side, rule.right_side[0])
        return G.cyclic()

def is_cnf_rule(r, start):
    '''Return whether a production rule is in CNF. Must indicate the grammar's
    start variable.'''
    rs = r.right_side
    return (len(rs) == 1 and isinstance(rs[0], Terminal)) or \
           (len(rs) == 2 and all(map(lambda x: isinstance(x, Nonterminal) and \
                                     x != start, rs))) or \
           (r.left_side == start and not rs)

def is_cnf(G):
    '''Return whether a grammar is in CNF.'''
    return all(map(lambda x: is_cnf_rule(x, G.start), G.productions))

def _first_rule_that(productions, pred):
    for i, p in enumerate(productions):
        if pred(p):
            return i

def _first_empty_rule(productions, start):
    return _first_rule_that(productions, \
                            lambda x: not x.right_side and \
                            not x.left_side == start)

def _first_unit_rule(productions):
    return _first_rule_that(productions, \
                            lambda x: len(x.right_side) == 1 \
                            and isinstance(x.right_side[0], Nonterminal))

def substitutions(sentence, production):
    '''Returns all of the distinct ways of applying a derivation rule to a
    sentence, including no change at all.'''
    indices = [i for i, s in enumerate(sentence) if s == production.left_side]
    result = []
    for subset in powerset(indices):
        substitution = []
        for i, symbol in enumerate(sentence):
            if i in subset:
                substitution.extend(production.right_side)
            else:
                substitution.append(symbol)
        if substitution not in result:
            result.append(substitution)
    return result

def chain(p, used_variables):
    '''Given a production rule p, return a list of equivalent rules such that
    the right side of each rule is no more than two symbols long.'''
    rs = p.right_side
    if len(rs) <= 2:
        return [p]
    first = rs[0]
    second_name = ''.join([str(s) for s in rs[1:]])
    second = SubscriptedNonterminal.next_unused(second_name, used_variables)
    first_new_rule = ProductionRule(p.left_side, (first, second))
    second_new_rule = ProductionRule(second, rs[1:])
    return [first_new_rule] + \
           chain(second_new_rule, used_variables | set([second]))

def get_variables(productions):
    '''Return a set of all the variables which appear in a list of productions.
    '''
    result = set()
    for p in productions:
        result.add(p.left_side)
        for s in p.right_side:
            if isinstance(s, Nonterminal):
                result.add(s)
    return result

def replace_terminals(p, proxy_rules):
    '''Replace all the terminal symbols in a production rule with equivalent
    variables, given a mapping from terminals to proxy production rules. Return
    a pair containing the fixed rule and a list of the terminals replaced.'''
    rs = p.right_side
    if len(rs) < 2 or p in proxy_rules.itervalues():
        return p, []
    new_rs = []
    replaced = []
    for s in rs:
        if isinstance(s, Terminal):
            new_rs.append(proxy_rules[s].left_side)
            replaced.append(s)
        else:
            new_rs.append(s)
    return ProductionRule(p.left_side, new_rs), replaced

def ChomskyNormalForm(G):
    '''Given a CFG G, return an equivalent CFG in Chomsky normal form.'''
            
    productions = list(G.productions)
    
    # Add a new start variable S0 and add the rule S0 -> S
    S0 = SubscriptedNonterminal(G.start.name, 0)
    productions[:0] = [ProductionRule(S0, [G.start])]

    # Remove e rules
    removed_rules = []
    while True:
        i = _first_empty_rule(productions, S0)
        if i is None:
            break
        pe = productions[i]
        removed_rules.append(pe)
        del productions[i]
        new_rules = [ProductionRule(rule.left_side, sentence) \
                     for rule in productions[1:] \
                     for sentence in substitutions(rule.right_side, pe)]
        productions[1:] = [r for r in new_rules if r not in removed_rules]

    # Remove unit rules
    removed_rules = []
    while True:
        i = _first_unit_rule(productions)
        if i is None:
            break
        pu = productions[i]
        removed_rules.append(pu)
        new_rules = [ProductionRule(pu.left_side, p.right_side) \
                     for p in productions if p.left_side == pu.right_side[0]]
        productions[i:i+1] = [r for r in new_rules if r not in productions \
                              and r not in removed_rules]

    # Chain right sides of rules
    i = 0
    while i < len(productions):
        new_rules = chain(productions[i], get_variables(productions))
        productions[i:i+1] = new_rules
        i += len(new_rules)

    # Replace terminal symbols with proxy variables
    terminals = G.terminals
    variables = get_variables(productions)
    proxy_rules = \
        {t : ProductionRule(
                SubscriptedNonterminal.next_unused(t.name.upper(), variables),
                [t]
             ) for t in terminals}
    added = {t : False for t in terminals}
    i = 0
    while i < len(productions):
        new_rule, replaced = replace_terminals(productions[i], proxy_rules)
        productions[i] = new_rule
        for t in replaced:
            if not added[t]:
                productions.append(proxy_rules[t])
                added[t] = True
        i += len(new_rules)

    return ContextFreeGrammar(productions)
