import sys
from cfg.cfg import *
from cfg.glr import *
from subprocutils import show_dot

def terminal_input_iterator():
    try:
        while True:
            yield Terminal(raw_input('INSERT NEXT SYMBOL HERE >> '))
    except (EOFError, KeyboardInterrupt):
        print
        return

def main():
    rc = 0
    if len(sys.argv) != 2:
        print '%s <grammar file>' % sys.argv[0]
        sys.exit(1)
    try:
        with open(sys.argv[1]) as fin:
            grammar = ContextFreeGrammar(fin.read())
        try:
            for t in parse(grammar, terminal_input_iterator()):
                show_dot(t.dot_str())
        except InputNotRecognized, e:
            sys.stderr.write('%s\n' % e)
            rc = 1
    except IOError, e:
        print 'Error:', e
        rc = 1
    sys.exit(rc)

main()

