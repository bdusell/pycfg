import re
from slr import *
from cfg import *

class CFGReaderError(Exception):
    pass

class CFGReader(object):
    '''A parser for the "extended" grammar syntax.

Example:
<S> -> <NP> <VP> | <S> <PP> | <S> "and" <S>
<NP> -> "n"
<NP> -> "det" "n"
    '''

    NONTERMINAL, TERMINAL, ARROW, PIPE, NEWLINE, ERROR, EOF = range(7)

    # Read a grammar from a string in the extended syntax and return the
    # grammar.
    def parse(self, s):
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
            raise CFGReaderError('expected different token, got %s' % self.value)

    def try_rule(self):
        if self.token == CFGReader.NONTERMINAL:
            self.read_rule()
            return True
        return False

    def tokens(self, s):
        tokenizer = re.compile(r'(\<[^>]*\>)|(\"[^"]*\")|(\-\>)|(\|)|(\n)', re.M)
        for token_tuple in tokenizer.findall(s):
            for i, v in enumerate(token_tuple):
                if v:
                    yield i, v
                    break
        yield CFGReader.EOF, None

    def next_token(self):
        result = (self.token, self.value) = next(self.tokenizer)
        return result


