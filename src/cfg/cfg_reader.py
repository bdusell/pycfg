'''A module for parsing context free grammar specifications using an extended
syntax. This extended syntax allows for symbols with labels longer than one
character. Nonterminal names are written between angle brackets (<...>), and
terminal names are written between double quotes ("...").

Example:
<Sentence> -> <Noun-phrase> <Verb-phrase> | <Sentence> <Prep-phrase>
<Noun-phrase> -> "noun"
<Noun-phrase> -> "det" "noun"
etc.
'''

import re
from cfg.core import Terminal, Nonterminal, ContextFreeGrammar, ProductionRule

class CFGReaderError(Exception):
    pass

class CFGReader(object):
    '''A parser for the "extended" grammar syntax.'''

    NONTERMINAL, TERMINAL, ARROW, PIPE, NEWLINE, WHITESPACE, ERROR, EOF = range(8)

    def parse(self, s):
        '''Read a grammar from a string in the extended syntax and return the
        grammar.'''
        self.productions = []
        self.tokenizer = iter(self.tokens(s))
        self.next_token()
        self.read_gram()
        if self.token != CFGReader.EOF:
            raise CFGReaderError('could not reach EOF')
        return ContextFreeGrammar([ProductionRule(left, right) for left, right_sides in self.productions for right in right_sides])

    def read_gram(self):
        while self.try_read(CFGReader.NEWLINE): pass
        if self.try_rule():
            while self.try_read(CFGReader.NEWLINE):
                while self.try_read(CFGReader.NEWLINE): pass
                if not self.try_rule(): break

    def read_rule(self):

        v = self.value
        self.read(CFGReader.NONTERMINAL)
        left_side = Nonterminal(v[1:-1])

        self.read(CFGReader.ARROW)

        self.right_sides = []
        self.read_sentence()
        while self.try_read(CFGReader.PIPE):
            self.read_sentence()

        self.productions.append((left_side, self.right_sides))

    def read_sentence(self):
        self.symbols = []
        while self.try_symbol(): pass
        self.right_sides.append(self.symbols)

    def try_symbol(self):
        v = self.value
        if self.try_read(CFGReader.NONTERMINAL):
            self.symbols.append(Nonterminal(v[1:-1]))
        elif self.try_read(CFGReader.TERMINAL):
            self.symbols.append(Terminal(v[1:-1]))
        else:
            return False
        return True

    def try_read(self, token):
        if self.token == token:
            self.next_token()
            return True
        return False

    def read(self, token):
        if not self.try_read(token):
            raise CFGReaderError('unexpected token %r' % self.value)

    def try_rule(self):
        if self.token == CFGReader.NONTERMINAL:
            self.read_rule()
            return True
        return False

    def tokens(self, s):
        tokenizer = re.compile(r'(\<[^>]*\>)|(\"[^"]*\")|(\-\>)|(\|)|(\n)|(\s+)|(.)', re.M)
        for token_tuple in tokenizer.findall(s):
            for i, v in enumerate(token_tuple):
                if v and i != self.WHITESPACE:
                    yield i, v
                    break
        yield CFGReader.EOF, None

    def next_token(self):
        result = (self.token, self.value) = next(self.tokenizer)
        return result

def parse_cfg(s):
    '''Parse a string into a ContextFreeGrammar, accepting either the extended
    or the standard syntax.'''
    try:
        return ContextFreeGrammar(s)
    except ValueError:
        try:
            return CFGReader().parse(s)
        except CFGReaderError:
            raise ValueError('unable to parse string into ContextFreeGrammar')

