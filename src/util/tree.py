'''A generic tree class.'''

from util.dot import escape
from util.mixin import Keyed

def Tree(node_type):
    '''A parameterized tree class which asserts that its nodes carry values
    that are instances of a particular type.'''
    
    class TreeClass(Keyed):

        def __init__(self, value, subtrees=None):
            if not isinstance(value, node_type):
                raise TypeError('tree value is not an instance of %s' % node_type.__name__)
            if subtrees is None: subtrees = []
            for t in subtrees:
                assert isinstance(t, self.__class__)
            self._value = value
            self._subtrees = tuple(subtrees)

        @property
        def value(self):
            '''Return the value stored at this node.'''
            return self._value

        @property
        def subtrees(self):
            '''Return the subtrees under this node.'''
            return self._subtrees

        def __str__(self):
            if self.subtrees:
                children = '(' + ''.join(str(s) for s in self.subtrees) + ')'
            else:
                children = ''
            return str(self.value) + children

        def __repr__(self):
            return '%s(%r, %r)' % (self.__class__.__name__, self.value, self.subtrees)

        def __key__(self):
            return (self._value, self._subtrees)

        def __eq__(self, y):
            return (
                isinstance(y, TreeClass) and
                super(TreeClass, self).__eq__(y))

        def _dot_lines(self):
            return ['q%s [label="%s"]' % (id(self), escape(str(self.value)))] + \
                   ['q%s -> q%s' % (id(self), id(c)) for c in self.subtrees] + \
                   sum([c._dot_lines() for c in self.subtrees], [])

        def dot_str(self):
            return '''\
digraph {
	%s
}''' % ';\n\t'.join(['graph [ordering="out"]'] + self._dot_lines())

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
