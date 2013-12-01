'''A set of mixin classes.'''

class Comparable(object):
    '''A mixin class which defines all of the rich comparison methods in terms
    of the __eq__ and __lt__ methods.'''

    def __ne__(self, y):
        return not self.__eq__(y)

    def __gt__(self, y):
        return y.__lt__(self)

    def __ge__(self, y):
        return not self.__lt__(y)

    def __le__(self, y):
        return not y.__lt__(self)

class Keyed(object):
    '''A mixin class which defines hash value and equality methods in terms of
    a single __key__ method.'''

    def __lt__(self, y):
        return self.__key__().__lt__(y.__key__())

    def __hash__(self):
        return self.__key__().__hash__()

    def __eq__(self, y):
        return self.__key__().__eq__(y.__key__())

class Subscripted(object):
    '''A mixin class which affixes a "subscript" to its objects, which is
    useful for creating similar but non-equal objects from the same value.'''

    def __init__(self, subscript):
        '''Initialize the object with a subscript, usually an integer.'''
        self.subscript = subscript

    def __str__(self):
        '''The subscript appears in brackets after the object's normal string
        value unless it is a single integer, when it appears without brackets.
        '''
        if type(self.subscript) == int:
            substr = str(self.subscript)
        else:
            substr = '[%s]' % self.subscript
        return super(Subscripted, self).__str__() + substr

    def __eq__(self, y):
        '''Two subscripted objects must have equal values and equal subscripts
        to be equal.'''
        return isinstance(y, Subscripted) and \
               self.subscript == y.subscript and \
               super(Subscripted, self).__eq__(y)

class Primed(Subscripted):
    '''A mixin class which affixes a "prime mark" to an object, to distinguish
    it from its original value.'''

    def __init__(self, num_primes):
        assert isinstance(num_primes, int) and num_primes > 0
        Subscripted.__init__(self, num_primes)

    @property
    def num_primes(self):
        return self.subscript

    def __str__(self):
        return super(Subscripted, self).__str__() + '\'' * self.subscript

    def __eq__(self, y):
        '''A primed object is equal to another if and only if the other object
        is a primed object with the same value.'''
        return isinstance(y, Primed) and \
               super(Primed, self).__eq__(y)

