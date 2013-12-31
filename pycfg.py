import sys, subprocess
from cfg import core, cfg_reader, slr, cnf

def print_usage():
    print '''\
Usage: pycfg ((-g|n|a|f|t -h|b) | (-m -b)) [input] [-o <output>]

    A context free grammar analyzer.

    input      The input file. If omitted, input is read from stdin. The
               input grammar may be in either the short or extended syntax.

               Short syntax:
                   A -> AB | Aa
                   B -> b
                   ...

               Extended syntax:
                   <sent> -> <noun-phr> <verb-phr>
                   <noun-phr> -> "the" <noun> | <noun>
                   ...

    -o output  The output file. If omitted, output is written to stdout.

    Flags:
    -h         Format the result in html.
    -b         Display the result in the browser.
    -c         Format the grammar and parse table for use in C++ code.

    Modes:
    -g -h|b    Simply display the grammar in the output format specified.
    -n -h|b    Convert the grammar to Chomsky normal form.
    -a -h|b    Compute the augmented grammar.
    -f -h|b    Compute the first and follow sets.
    -m -b      Compute the DFA of LR(0) items used for LR parsing.
    -t -h|b    Compute the SLR(1) parse table.
    -r -h|b    Generate a report showing the augmented grammar, first and
               follow sets, DFA, and parse table.

    --help     Display this help message.
'''

class UsageError(Exception):
    pass

def process_args(args):
    def error(msg): raise UsageError(msg)
    opts = {c : False for c in 'ohbgnafmtr'}
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
    output_formats = 'hb'
    operations = 'gnafmtr'
    checkopts(output_formats, 'output format')
    checkopts(operations, 'operation')
    if opts['m'] and not opts['b']: error('DFA requires browser output')
    def whichopt(s):
        for c in s:
            if opts[c]:
                return c
    execute(whichopt(output_formats), whichopt(operations), fin_name, fout_name)

def execute(output_format, operation, fin_name, fout_name):
    with sys.stdin if fin_name is None else open(fin_name, 'r') as fin:
        try:
            G = cfg_reader.parse_cfg(fin.read())
        except ValueError:
            raise UsageError('syntax error in input grammar')

        if operation == 'g':
            html = G.html()
        elif operation == 'n':
            html = cnf.ChomskyNormalForm(G).html()
        elif operation == 'a':
            html = slr.augmented(G).html()
        elif operation == 'f':
            html = first_follow_set_html(G)
        elif operation == 't':
            T = slr.ParsingTable(G)
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
    <title>pycfg</title>
  </head>
  <body>
%s
  </body>
</html>
''' % html)
    preferred_open(tmp)

def main():
    args = sys.argv[1:]
    if args and not '--help' in args:
        try:
            process_args(args)
        except UsageError, e:
            print 'Error:', e
            print_usage()
            sys.exit(1)
        except (IOError, ValueError), e:
            print 'Error:', e
            sys.exit(1)
        except KeyboardInterrupt:
            print
    else:
        print_usage()

if __name__ == '__main__':
    main()

