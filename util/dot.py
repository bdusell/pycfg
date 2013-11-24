'''Utilities for dealing with .dot format files.'''

def escape(s):
    return repr(s)[1:-1].replace('"', '\\"')
