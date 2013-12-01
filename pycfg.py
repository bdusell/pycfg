import sys, subprocess
from cfg import cfg, cfg_reader, slr

def print_usage():
    print '''\
Usage: pycfg [-e] ((-g|n|a|f -h|b) | (-m -b) | (-t -h|b|c)) [input] [-o <output>]

    A context free grammar analyzer.

    input      The input file. If omitted, input is read from stdin.
    -o output  The output file. If omitted, output is written to stdout.

    -e         Read the input grammar using the extended syntax.
    -h         Format the result in html.
    -b         Display the result in the browser.
    -c         Format the grammar and parse table for use in C++ code.

    -g -h|b    Simply display the grammar in the output format specified.
    -n -h|b    Convert the grammar to Chomsky normal form.
    -a -h|b    Compute the augmented grammar.
    -f -h|b    Compute the first and follow sets.
    -m -b      Compute the DFA of LR(0) items used for LR parsing.
    -t -h|b|c  Compute the SLR(1) parse table.
    -r -h|b    Generate a report showing the augmented grammar, first and
               follow sets, DFA, and parse table.

    --help     Display this help message.
'''

class UsageError(Exception):
    pass

def process_args(args):
    def error(msg): raise UsageError(msg)
    opts = {c : False for c in 'oehbcgnafmtr'}
    fin_name, fout_name = None, None
    for arg in args:
       if opts['o'] and fout_name is None:
           fout_name = arg
       elif arg.startswith('-'):
           for flag in arg[1:]:
               if flag in opts:
                   if opts[flag]:
                       error("flag '-%s' given more than once" % flag)
                   else:
                       opts[flag] = True
               else:
                   error("flag '-%s' not recognized" % flag)
       elif fin_name is None:
           fin_name = arg
       else:
           error("unrecognized argument '%s'" % arg)
    if opts['o'] and fout_name is None:
        error('-o flag missing file name')
    if opts['b'] and fout_name is not None:
        error('cannot have output file in browser mode')
    def checkopts(s, name):
        count = sum(opts[c] for c in s)
        if count < 1: error('missing %s' % name)
        elif count > 1: error('conflicting %ss' % name)
    output_formats = 'hbc'
    operations = 'gnafmtr'
    checkopts(output_formats, 'output format')
    checkopts(operations, 'operation')
    if opts['m'] and not opts['b']: error('DFA requires browser output')
    elif opts['c'] and not opts['t']: error('only the parsing table can be output as C++ code')
    def whichopt(s):
        for c in s:
            if opts[c]:
                return c
    execute(whichopt(output_formats), whichopt(operations), opts['e'], fin_name, fout_name)

def execute(output_format, operation, extended_syntax, fin_name, fout_name):
    with sys.stdin if fin_name is None else open(fin_name, 'r') as fin:
        read = cfg_reader.CFGReader().parse if extended_syntax else cfg.ContextFreeGrammar
        try:
            G = read(fin.read())
        except AssertionError:
            raise UsageError('syntax error in input grammar (try using -e)')

        if operation == 'g':
            html = G.html()
        elif operation == 'n':
            html = cfg.ChomskyNormalForm(G).html()
        elif operation == 'a':
            html = slr.augmented(G).html()
        elif operation == 'f':
            html = first_follow_set_html(G)
        elif operation == 't':
            T = slr.ParsingTable(G)
            if output_format == 'c':
                cpp = table_cpp(T)
            else:
                html = T.html()
        elif operation == 'r':
            html = report_html(G)

        if output_format == 'b':
            if operation == 'm':
                browser_automaton(G)
            else:
                browser_html(html)
        else:
            with sys.stdout if fout_name is None else open(fout_name, 'w') as fout:
                fout.write(html if output_format == 'h' else cpp)

def first_follow_set_html(G):
    M = slr.Automaton(G)
    G = M.augmented_grammar()
    FIRST = slr.FirstSetTable(G)
    FOLLOW = slr.FollowSetTable(FIRST, M)
    return '''\
<h1>First Sets</h1>
%s
<h1>Follow Sets</h1>
%s''' % (FIRST.html(), FOLLOW.html())

def report_html(G):
    T = slr.ParsingTable(G)
    return '''\
<h1>Original Grammar</h1>
%s
<h1>Augmented Grammar</h1>
%s
<h1>First Sets</h1>
%s
<h1>Follow Sets</h1>
%s
<h1>Parsing Table</h1>
%s''' % (T.original_grammar().html(),
         T.augmented_grammar().html(),
         T.first_sets().html(),
         T.follow_sets().html(),
         T.html())

def tempfile(suffix):
    p = subprocess.Popen(['tempfile', '-s', suffix], stdout=subprocess.PIPE)
    tempfile_name = p.stdout.read().strip()
    p.wait()
    return tempfile_name

def preferred_open(filename):
    subprocess.call(['xdg-open', filename])

def browser_automaton(G):
    png = tempfile('.png')
    dot = subprocess.Popen(['dot', '-Tpng'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    dot.stdin.write(slr.Automaton(G).dot_html())
    dot.stdin.close()
    with open(png, 'w') as fout:
        fout.write(dot.stdout.read())
    dot.wait()
    preferred_open(png)

def browser_html(html):
    tmp = tempfile('.html')
    with open(tmp, 'w') as fout:
        fout.write('''\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="Content-language" content="en" />
    <title>cfg</title>
  </head>
  <body>
%s
  </body>
</html>
''' % html)
    preferred_open(tmp)

def table_cpp(T):
    G = T.augmented_grammar()
    NONTERMINALS = list(G.nonterminals)
    TERMINALS = list(G.terminals)
    SYMBOLS = NONTERMINALS + TERMINALS
    END_ID = 'end'
    RULES = G.productions

    make_symbol_id = lambda s: '_' + ''.join(c if c.isalpha() else str(ord(c)) for c in str(s))
    symbol_ids = {X : make_symbol_id(X) for X in SYMBOLS}
    symbol_id = lambda s: symbol_ids[s] if s in symbol_ids else END_ID

    make_symbol_string = lambda s: '"%s"' % s.name.replace('"', '\\"')
    symbol_strings = {X : make_symbol_string(X) for X in SYMBOLS}
    symbol_string = lambda s: symbol_strings[s]

    make_rule = lambda p: 'rule(%s, %s)' % \
                          (symbol_id(p.left_side),
                           'sent()' + ''.join(' << ' + symbol_id(X) for X in p.right_side))
    make_rule_ref = lambda i: 'const rule &re%d = G.get_rule(%d);' % (i, i)

    def make_rule_entry(q, X, e):
        a = e[0]
        Xid = symbol_id(X)
        if a == slr.ParsingTable.SHIFT:
            return 'T.add_shift(%s, %s, %s);' % (q, Xid, e[1])
        elif a == slr.ParsingTable.REDUCE:
            return 'T.add_reduction(%s, %s, %s);' % (q, Xid, 're%d' % e[1])
        elif a == slr.ParsingTable.ACCEPT:
            return 'T.add_accept(%s, %s);' % (q, Xid)

    make_goto_entry = lambda q, X, e: 'T.set_goto(%s, %s, %s);' % (q, symbol_id(X), e)

    rule_entries = '\n\t'.join([make_rule_entry(q, X, e) for q, row in enumerate(T._action) \
                                                         for X, cell in row.iteritems() \
                                                         for e in cell] +
                               [make_goto_entry(q, X, e) for q, row in enumerate(T._goto) \
                                                         for X, e in row.iteritems() \
                                                         if X.is_nonterminal()])

    return '''\
#include <iostream>
#include <string>
#include "SymbolReader.h"
#include "GrammarPrinter.h"
#include "ContainerWrapper.h"
#include "tomita.h"
using namespace std;
int main(int argc, char **argv) {
	enum { %(SYMBOL_ENUMS)s };
	GrammarPrinter printer(ContainerWrapper<string>() %(SYMBOL_STRINGS)s);
	ContextFreeGrammar G(%(NUM_VARIABLES)d, %(NUM_SYMBOLS)d);
	typedef ContextFreeGrammar::rule_type rule;
	typedef ContextFreeGrammar::symbol_type symbol;
	typedef ContainerWrapper<symbol> sent;
	G %(RULES)s;
	symbol end = G.end_marker();
	ParseTable T;
	%(RULE_REFS)s
	%(TABLE_ENTRIES)s
	SymbolReader::map_type dict;
	%(DICT_ENTRIES)s
	printer.print(cout, G);
	SymbolReader reader(cin, dict, end);
	tomita_algorithm(T, reader, printer);
	return 0;
}
''' % {
        'SYMBOL_ENUMS'   : ', '.join(map(symbol_id, SYMBOLS)),
        'SYMBOL_STRINGS' : ' '.join('<< %s' % symbol_string(s) for s in SYMBOLS),
        'NUM_VARIABLES'  : len(NONTERMINALS),
        'NUM_SYMBOLS'    : len(SYMBOLS),
        'RULES'          : '\n\t  '.join('<< ' + make_rule(p) for p in RULES),
        'RULE_REFS'      : '\n\t'.join(make_rule_ref(i) for i in range(1, len(RULES))),
        'TABLE_ENTRIES'  : rule_entries,
        'DICT_ENTRIES'   : '\n\t'.join('dict[%s] = %s;' % (symbol_string(s), symbol_id(s)) for s in TERMINALS)
    }

def main():
    args = sys.argv[1:]
    if args and not '--help' in args:
        try:
            process_args(args)
        except UsageError, e:
            print 'Error:', e
            print_usage()
        except (IOError, cfg_reader.CFGReaderError), e:
            print 'Error:', e
        except KeyboardInterrupt:
            print
    else:
        print_usage()

main()

