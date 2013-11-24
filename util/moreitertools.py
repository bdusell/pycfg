'''Iterator and sequence tools.'''

import itertools

def alternations(sequences):
    '''Given a list of sequences, return every combination of the items in the
    lists.'''
    if sequences:
        for alt in alternations(sequences[1:]):
            for item in sequences[0]:
                yield [item] + alt
    else:
        yield []

def powerset(iterable):
    '''Return the power set of a list of items.'''
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, i) \
                                         for i in xrange(len(s)+1))

