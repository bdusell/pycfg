'''Make sure Terminal and Nonterminal objects are sorted correctly.'''

from cfg.core import *
from util.html import *

T = map(Terminal, 'ABCDEF')
N = map(Nonterminal, 'ABCDEF')

print ul(sorted(set(T + N)))

