'''A Context Free Grammar class along with peripheral classes and algorithms.
'''

import itertools
import cgi

from util.digraph import Digraph
from util.tree import Tree
from util.mixin import Comparable, Keyed, Subscripted, Primed

class Symbol(Comparable, Keyed):
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

    def is_nonterminal(self):
        '''Tell whether this is a nonterminal symbol.'''
        raise NotImplementedError()

    def is_terminal(self):
        '''Tell whether this is a terminal symbol.'''
        raise NotImplementedError()

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self._identifier)

    def __eq__(self, y):
        '''Symbols must be of the same class and have the same identifier to be
        considered equal.'''
        return self.__class__ == y.__class__ and \
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
    '''A nonterminal with some number of "prime" marks.'''

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
        return '<code>%s</code>' % (cgi.escape(self.name)) if self.name else '&ldquo;&rdquo;'

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
            (P), and start variable (S) are explicitly given and checked for
            correctness.'''
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
        return self.nonterminals | self.terminals

    def _get_symbols_of_type(self, T):
        return set(s for p in self._productions for s in p.right_side \
                   if isinstance(s, T))

    def _init_string(self, string):
        lines = filter(None, string.split('\n'))
        split_sides = [[w.strip() for w in line.split('->', 1)] for line in lines]
        for left, right in split_sides:
            if not (len(left) == 1 and left.isupper()):
                raise ValueError('"%s" is not valid on the left side of a production rule')
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
        if not self._productions:
            raise ValueError('not production rules were given')
        self._start = self._productions[0].left_side

    def _check_productions(self, productions):
        if not productions:
            raise ValueError('no production rules were given')
        for p in productions:
            if not isinstance(p, ProductionRule):
                raise TypeError('production rules must be instances of ProductionRule')

    def _init_productions(self, productions):
        self._extra_nonterminals = set()
        self._extra_terminals = set()
        self._productions = list(productions)
        self._start = productions[0].left_side

    def _check_tuple(self, nonterminals, terminals, productions, start):
        # Check nonterminals
        for n in nonterminals:
            if not isinstance(n, Nonterminal):
                raise TypeError('%r is not an instance of Nonterminal' % n)
        # Check terminals
        for t in terminals:
            if not isinstance(t, Terminal):
                raise TypeError('%r is not an instance of Terminal' % t)
        # Check production rules
        if not productions:
            raise ValueError('no production rules were given')
        for p in productions:
            if not isinstance(p, ProductionRule):
                raise TypeError('%r is not an instance of ProductionRule' % p)
            if not (p.left_side in nonterminals):
                raise ValueError('%r is on the left side of a production rule but is not a nonterminal in the grammar' % p.left_side)
            for s in p.right_side:
                if not (s in terminals or s in nonterminals):
                    raise ValueError('%r is on the right side of a production rule but is not a symbol in the grammar' % s)
        # Check start symbol
        if not isinstance(start, Nonterminal):
            raise TypeError('start variable %r is not an instance of Nonterminal' % start)
        if not (start in nonterminals):
            raise ValueError('start variable %r is not a nonterminal in the grammar' % start)

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

