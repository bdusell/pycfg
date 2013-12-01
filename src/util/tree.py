'''A generic tree class.'''

from util.dot import escape

def Tree(node_type):
    '''A parameterized tree class which asserts that its nodes carry values
    that are instances of a particular type.'''
    
    class TreeClass(object):
        
        def __init__(self, value, subtrees=None):
            assert isinstance(value, node_type)
            if subtrees is None: subtrees = []
            for t in subtrees:
                assert isinstance(t, self.__class__)
            self.value = value
            self.subtrees = tuple(subtrees)

        def __str__(self):
            if self.subtrees:
                children = '(' + ''.join(str(s) for s in self.subtrees) + ')'
            else:
                children = ''
            return str(self.value) + children

        def __repr__(self):
            return '%s(%r, %r)' % (self.__class__.__name__, self.value, self.subtrees)

        def __eq__(self, y):
            return isinstance(y, self.__class__) and \
                   self.value == y.value and \
                   self.subtrees == y.subtrees

        def _dot_lines(self):
            return ['q%s [label="%s"]' % (id(self), escape(str(self.value)))] + \
                   ['q%s -> q%s' % (id(self), id(c)) for c in self.subtrees] + \
                   sum([c._dot_lines() for c in self.subtrees], [])

        def dot_str(self):
            return '''\
digraph {
	%s
}
''' % ';\n\t'.join(self._dot_lines())

        def iter_leaves(self):
            if not self.subtrees:
                yield self.value
            else:
                for tree in self.subtrees:
                    for leaf in tree.iter_leaves():
                        yield leaf

        def all_leaves(self, func=(lambda x: x)):
            for leaf in self.iter_leaves():
                if not func(leaf):
                    return False
            return True

    return TreeClass
