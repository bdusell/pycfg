'''Algorithms for converting grammars to Chomsky Normal Form.'''

from cfg.core import ContextFreeGrammar, Terminal, Nonterminal, \
                     ProductionRule, SubscriptedNonterminal
from util.moreitertools import powerset

def is_cnf_rule(r, start):
    '''Return whether a production rule is in CNF. Must indicate the grammar's
    start variable.'''
    rs = r.right_side
    return (len(rs) == 1 and rs[0].is_terminal()) or \
           (len(rs) == 2 and all(map(lambda x: x.is_nonterminal() and \
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

