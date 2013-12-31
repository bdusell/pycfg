'''Additional CFG algorithms.'''

from util.digraph import Digraph
from table import first_sets

def has_empty_rules(grammar):
    '''Return whether a grammar has e-productions.'''
    for rule in grammar.productions:
        if not rule.right_side:
            return True
    return False

def is_left_recursive(grammar):
    '''Return whether a grammar is left-recursive.'''
    firsts, nullable = first_sets(grammar)
    G = Digraph()
    for rule in grammar.productions:
        for Xi in rule.right_side:
            if Xi.is_nonterminal():
                G.add_edge(rule.left_side, Xi)
                if Xi not in nullable:
                    break
            else:
                break
    return G.cyclic()

def is_cyclic(grammar):
    '''Return whether a grammar has a cycle.'''
    firsts, nullable = first_sets(grammar)
    G = Digraph()
    for rule in grammar.productions:
        for i, Xi in enumerate(rule.right_side):
            if Xi.is_nonterminal():
                if all(
                    map(
                        lambda x: x in nullable,
                        rule.right_side[:i-1] + rule.right_side[i+1:])):
                    G.add_edge(rule.left_side, Xi)
            else:
                break
    return G.cyclic()

