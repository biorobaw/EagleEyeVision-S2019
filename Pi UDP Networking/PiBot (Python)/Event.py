class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x
    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()
    >>> e += f
    >>> e += g
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)
    >>> e -= g
    >>> e()
    """
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)

    def __iadd__(self, x):
        self.append(x)
        return self

    def __isub__(self, x):
        self.remove(x)
        return self
