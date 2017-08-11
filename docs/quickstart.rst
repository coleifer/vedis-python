.. quickstart:

Quickstart
==========

Below is a sample interactive console session designed to show some of the basic features and functionality of the vedis-python library. Also check out the :ref:`full API docs <api>`.

Key/value features
------------------

You can use Vedis like a dictionary for simple key/value lookups:

.. code-block:: pycon

    >>> from vedis import Vedis
    >>> db = Vedis(':mem:')  # Create an in-memory database. Alternatively you could supply a filename for an on-disk database.
    >>> db['k1'] = 'v1'
    >>> db['k1']
    'v1'

    >>> db.append('k1', 'more data')  # Returns length of value after appending new data.
    11
    >>> db['k1']
    'v1more data'

    >>> del db['k1']
    >>> db['k1'] is None
    True

You can set and get multiple items at a time:

.. code-block:: pycon

    >>> db.mset(dict(k1='v1', k2='v2', k3='v3'))
    True

    >>> db.mget(['k1', 'k2', 'missing key', 'k3'])
    ['v1', 'v2', None, 'v3']

In addition to storing string keys/values, you can also implement counters:

.. code-block:: pycon

    >>> db.incr('counter')
    1

    >>> db.incr('counter')
    2

    >>> db.incr_by('counter', 10)
    12

    >>> db.decr('counter')
    11

Transactions
------------

Vedis has support for transactions when you are using an on-disk database. You can use the :py:meth:`~Vedis.transaction` context manager or explicitly call :py:meth:`~Vedis.begin`, :py:meth:`~Vedis.commit` and :py:meth:`~Vedis.rollback`.

.. code-block:: pycon

    >>> db = Vedis('/tmp/test.db')
    >>> with db.transaction():
    ...     db['k1'] = 'v1'
    ...     db['k2'] = 'v2'
    ...
    >>> db['k1']
    'v1'

    >>> with db.transaction():
    ...     db['k1'] = 'modified'
    ...     db.rollback()  # Undo changes.
    ...
    >>> db['k1']  # Value is not modified.
    'v1'

    >>> db.begin()
    >>> db['k3'] = 'v3-xx'
    >>> db.commit()
    True
    >>> db['k3']
    'v3-xx'

Hashes
------

Vedis supports nested key/value lookups which have the additional benefit of supporting operations to retrieve all keys, values, the number of items in the hash, and so on.

.. code-block:: pycon

    >>> h = db.Hash('some key')
    >>> h['k1'] = 'v1'
    >>> h.update(k2='v2', k3='v3')

    >>> h
    <Hash: {'k3': 'v3', 'k2': 'v2', 'k1': 'v1'}>

    >>> h.to_dict()
    {'k3': 'v3', 'k2': 'v2', 'k1': 'v1'}

    >>> h.items()
    [('k1', 'v1'), ('k3', 'v3'), ('k2', 'v2')]

    >>> list(h.keys())
    ['k1', 'k3', 'k2']

    >>> del h['k2']

    >>> len(h)
    2

    >>> 'k1' in h
    True

    >>> [key for key in h]
    ['k1', 'k3']

Sets
----

Vedis supports a set data-type which stores a unique collection of items.

.. code-block:: pycon

    >>> s = db.Set('some set')
    >>> s.add('v1', 'v2', 'v3')
    3

    >>> len(s)
    3

    >>> 'v1' in s, 'v4' in s
    (True, False)

    >>> s.top()
    'v1'

    >>> s.peek()
    'v3'

    >>> s.remove('v2')
    1

    >>> s.add('v4', 'v5')
    2

    >>> s.pop()
    'v5'

    >>> [item for item in s]
    ['v1', 'v3', 'v4']

    >>> s.to_set()
    set(['v1', 'v3', 'v4'])

    >>> s2 = db.Set('another set')
    >>> s2.add('v1', 'v4', 'v5', 'v6')
    4

    >>> s2 & s  # Intersection.
    set(['v1', 'v4'])

    >>> s2 - s  # Difference.
    set(['v5', 'v6'])


Lists
-----

Vedis also supports a list data type.

.. code-block:: pycon

    >>> l = db.List('my list')
    >>> l.append('v1')
    1
    >>> l.extend(['v2', 'v3', 'v1'])
    4

    >>> for item in l:
    ...     print item
    ...
    v1
    v2
    v3
    v4

    >>> for item in l[1:3]:
    ...     print item
    v2
    v3

    >>> len(l)
    4

    >>> l[1]
    'v2'

    >>> db.llen('my_list')
    2

    >>> l.pop(), l.pop()
    ('v1', 'v2')

    >>> len(l)
    2

Misc
----

Vedis has a somewhat quirky collection of other miscellaneous commands. Below is a sampling:

.. code-block:: pycon

    >>> db.base64('encode me')
    'ZW5jb2RlIG1l'

    >>> db.base64_decode('ZW5jb2RlIG1l')
    'encode me'

    >>> db.random_string(10)
    'raurquvsnx'

    >>> db.rand(1, 6)
    4

    >>> db.str_split('abcdefghijklmnop', 5)
    ['abcde', 'fghij', 'klmno', 'p']

    >>> db['data'] = 'abcdefghijklmnop'
    >>> db.strlen('data')
    16

    >>> db.strip_tags('<p>This <span>is</span> a <a href="#">test</a>.</p>')
    'This is a test.'
