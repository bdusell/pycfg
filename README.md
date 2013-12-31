pycfg
=====

This repository contains a Python package, `cfg`, which implements
data structures and algorithms for carrying out sophisticated analysis and
parsing of arbitrary context-free grammars. The main vehicle used for CFG
parsing is the GLR (Generalized-LR) algorithm discovered by Masaru Tomita.
Several pedagogical parsing algorithms described by Alfred Aho and Jeffrey
Ullman are also included. A tool named `pycfg` provides a command-
line interface to CFG analysis algorithms.

Contents
--------

The file `pycfg` is a command-line utility for analyzing CFGs. It can:

* Convert grammars to Chomsky Normal Form
* Compute a grammar's first and follow sets
* Create a diagram of a grammar's DFA of LR(0) items used for LR parsing
* Compute a grammar's SLR(1) parse table
* Generate a report in HTML of the steps taken to build the parse table
* Make you a sandwich, as long as you have root privileges

Use the command

    ./pycfg

without arguments to see a full help message.

The `src/` directory contains the Python packages `cfg` and `util`. Included
in `cfg` are:

* A class structure for context free grammars, symbols, parse trees, etc.
* Tomita's GLR parsing algorithm, modified to handle empty production rules
  and cyclic grammars
* Algorithms for building first sets, follow sets, and multi-valued SLR parse
  tables
* Parsing algorithms described by Aho and Ullman and included for pedagogical
  purposes
* Other algorithms such as cycle and left-recursion detection

The `test/` directory contains unit tests for most components in the
library. Use

    ./run_tests

to run all of the test cases included here, which should all pass.

The `demos/` directory contains some standalone Python scripts demonstrating
the use of the library.

Demo
----

The demos/ directory has a number of driver programs demonstrating the use
of various parts of the library. For example, the command

    cd src; python ../demos/glr_demo.py ../demos/grammars/gra.txt

will bring up a prompt for input symbols to be parsed with respect to the
ambiguous grammar described in demos/grammars/gra.txt, and then generate
and display images of the resulting parse trees. In this case the input
alphabet consists of the characters 'n' for noun, 'd' for determiner, 'v'
for Vendetta... I mean verb, and 'p' for preposition. To run the example
on an ambiguous sentence with six valid parse trees, enter the following
characters at the prompt and then press Ctrl-C, as shown below:

    >> n
    >> v
    >> n
    >> a
    >> n
    >> v
    >> d
    >> n
    >> p
    >> d
    >> n
    >> <Ctrl-C>

This corresponds to the sentence "I saw Jane and Jack hit the man with a
telescope."

References
----------

* Aho, Alfred V., and Ullman, Jeffrey D. *The Theory of Parsing, Translation,
  and Compiling: Volume I: Parsing*. Englewood Cliffs, NJ: Prentice-Hall,
  Inc. 1972.
* Tomita, Masaru (Ed.). *Generalized LR Parsing*. Boston, MA: Kluwer Academic
  Publishers 1991.

