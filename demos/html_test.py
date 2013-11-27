'''Print various things as HTML to stdout.'''

from cfg.cfg import *

things_to_print = [
    Nonterminal('A'),
    Terminal('a'),
    Nonterminal('noun'),
    Nonterminal('Noun-phrase'),
    Terminal('and'),
    SubscriptedNonterminal('S', 0),
    Marker('$'),
    ProductionRule(Nonterminal('A'), [Nonterminal('A'), Terminal('a')]),
    ProductionRule(Nonterminal('A'), []),
    Nonterminal(''),
    Terminal('')
]

print '<br />\n'.join(map(lambda x: x.html(), things_to_print))

