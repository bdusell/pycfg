'''An easy method for reindexing a list.'''

class ReindexedList(list):
    '''A list-wrapper which reindexes the items by a certain offset.'''

    def __init__(self, shift=1, *vargs, **kwargs):
        super(ReindexedList, self).__init__(*vargs, **kwargs)
        self._shift = shift

    def __getitem__(self, i):
        self._check_index(i)
        return super(ReindexedList, self).__getitem__(i - self._shift)

    def __getslice__(self, i, j):
        self._check_index(i)
        self._check_index(j)
        return ReindexedList(self._shift, \
                             super(ReindexedList, self).__getslice__( \
                                 i - self._shift, j - self._shift))

    def __setitem__(self, i, y):
        self._check_index(i)
        return super(ReindexedList, self).__setitem__(i - self._shift, y)

    def __setslice__(self, i, j, y):
        self._check_index(i)
        self._check_index(j)
        return super(ReindexedList, self).__setslice__(i - self._shift, j - self._shift, y)

    def __delitem__(self, i):
        self._check_index(i)
        return super(ReindexedList, self).__delitem__(i - self._shift)

    def __delslice__(self, i, j):
        self._check_index(i)
        self._check_index(j)
        return super(ReindexedList, self).__delslice__(i - self._shift, \
                                                       j - self._shift)

    def __repr__(self):
        return 'ReindexedList(%s, %r)' % \
               (self._shift, super(ReindexedList, self))

    def index(self, o):
        return super(ReindexedList, self).index(o) + self._shift

    def _check_index(self, i):
        if i < self._shift:
            raise IndexError('got index %d for list with starting index %d' % (i, self._shift))


Seq = lambda x: ReindexedList(1, x)
