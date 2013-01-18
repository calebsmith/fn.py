from sys import version
from collections import deque
from operator import itemgetter, attrgetter
from functools import partial
from itertools import (islice, chain, 
                       izip, imap, ifilter, 
                       starmap, repeat, tee, cycle,
                       takewhile, dropwhile,
                       combinations)

from .op import flip
from .func import F

# Syntax sugar to deal with Python 2/Python 3 
# differences: this one will return generator
# even in Python 2.*
map = imap if version.startswith("2") else map
filter = ifilter if version.startswith("2") else filter
zip = izip if version.startswith("2") else zip

if version.startswith("3"):
    from functools import reduce
reduce = reduce 
range = xrange if version.startswith("2") else  range

if version.startswith("2"):
    from itertools import ifilterfalse as filterfalse
else:
    from itertools import filterfalse
filterfalse = filterfalse

if version.startswith("2"):
    from itertools import izip_longest as zip_longest
else:
    from itertools import zip_longest
zip_longest = zip_longest

def zipwith(f): 
    'zipwith(f)(seq1, seq2, ..) -> [f(seq1[0], seq2[0], ..), f(seq1[1], seq2[1], ..), ...]'
    return F(starmap, f) << zip

def take(limit, base): 
    return islice(base, limit)

def drop(limit, base): 
    return islice(base, limit, None)

def takelast(n, iterable):
    "Return iterator to produce last n items from origin"
    return iter(deque(iterable, maxlen=n))

def droplast(n, iterable):
    "Return iterator to produce items from origin except last n"
    t1, t2 = tee(iterable)
    return map(itemgetter(0), zip(t1, islice(t2, n, None)))

def consume(iterator, n=None):
    """Advance the iterator n-steps ahead. If n is none, consume entirely.

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)

def nth(iterable, n, default=None):
    """Returns the nth item or a default value

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    return next(islice(iterable, n, None), default)

# widely-spreaded shoutcust to get first item 
# and all but first item from iterator
head = partial(flip(nth), 0)
tail = partial(drop, 1)

def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.
    Useful for emulating the behavior of the built-in map() function.

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    return chain(iterable, repeat(None))

def ncycles(iterable, n):
    """Returns the sequence elements n times

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    return chain.from_iterable(repeat(tuple(iterable), n))

def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.
    Example:  repeatfunc(random.random)

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))

def grouper(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks, so
    grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)

def roundrobin(*iterables):
    """roundrobin('ABC', 'D', 'EF') --> A D E B F C
    Recipe originally credited to George Sakkis.
    Reimplemented to work both in Python 2+ and 3+. 

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    pending = len(iterables)
    next_attr = "next" if version.startswith("2") else "__next__"
    nexts = cycle(map(attrgetter(next_attr), map(iter, iterables)))
    while pending:
        try:
            for n in nexts:
                yield n()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def partition(pred, iterable):
    """Use a predicate to partition entries into false entries and true entries
    partition(is_odd, range(10)) --> 0 2 4 6 8   and  1 3 5 7 9

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)

def splitat(t, iterable):
    """Split iterable into two iterators after given number of iterations
    splitat(2, range(5)) --> 0 1 and 2 3 4
    """
    t1, t2 = tee(iterable)
    return islice(t1, t), islice(t2, t, None)

def splitby(pred, iterable):
    """Split iterable into two iterators at first false predicate
    splitby(is_even, range(5)) --> 0 and 1 2 3 4
    """
    t1, t2 = tee(iterable)
    return takewhile(pred, t1), dropwhile(pred, t2)

def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def pairwise(iterable):
    """pairwise(s) -> (s0,s1), (s1,s2), (s2, s3), ...

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def iter_except(func, exception, first=None):
    """ Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like __builtin__.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    Examples:
        iter_except(functools.partial(heappop, h), IndexError)   # priority queue iterator
        iter_except(d.popitem, KeyError)                         # non-blocking dict iterator
        iter_except(d.popleft, IndexError)                       # non-blocking deque iterator
        iter_except(q.get_nowait, Queue.Empty)                   # loop over a producer Queue
        iter_except(s.pop, KeyError)                             # non-blocking set iterator

    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    try:
        if first is not None:
            yield first()            # For database APIs needing an initial cast to db.first()
        while 1:
            yield func()
    except exception:
        pass

# XXX reimplement to work recursive with all levels
def flatten(listOfLists):
    """Flatten one level of nesting
    
    http://docs.python.org/3.4/library/itertools.html#itertools-recipes
    """
    return chain.from_iterable(listOfLists)

