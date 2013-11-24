'''Make sure Terminal and Nonterminal objects are sorted correctly.'''

from cfg.cfg import *
from util.html import *

T = map(Terminal, 'ABCDEF')
N = map(Nonterminal, 'ABCDEF')

print ul(sorted(set(T + N)))

