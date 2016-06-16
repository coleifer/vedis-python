![](http://media.charlesleifer.com/blog/photos/vedis-python-logo.png)

Fast Python bindings for the Vedis embedded NoSQL database. Vedis is a fun, fast, embedded database modeled after Redis.

[View the vedis-python documentation](https://vedis-python.readthedocs.io/).

### Features

Vedis features:

* Embedded, zero-conf database
* Transactional (ACID)
* Single file or in-memory database
* Key/value store
* [Over 70 commands](http://vedis.symisc.net/commands.html) similar to standard [Redis](http://redis.io) commands.
* Thread-safe
* Terabyte-sized databases

Vedis-Python features:

* Compiled library, extremely fast with minimal overhead.
* Supports key/value operations and transactions using Pythonic APIs.
* Support for executing Vedis commands.
* Write custom commands in Python.
* Python 2.x and 3.x.

Limitations:

* Not tested on Windoze.

The previous version (0.2.0) of `vedis-python` utilized `ctypes` to wrap the Vedis C library. By switching to Cython, key/value and Vedis command operations are significantly faster.

Links:

* [vedis-python documentation](https://vedis-python.readthedocs.io/)
* [Vedis's C API](http://vedis.symisc.net/c_api.html)

If you like Vedis, you might also want to check out [UnQLite](http://unqlite.symisc.net), an embedded key/value database with cursors and a cool JSON document store (python bindings: [unqlite-python](https://unqlite-python.readthedocs.io)).

## Installation

You can install vedis-python using `pip`.

    pip install vedis

Basic usage
-----------

First you instantiate a `Vedis` object, passing in either the path to the database
file or the special string `':mem:'` for an in-memory database.

Below is a sample interactive console session designed to show some of the basic features and functionality of the vedis-python library. Also check out the [full API documentation](https://vedis-python.readthedocs.io/en/latest/api.html) as well as the [vedis command documentation](http://vedis.symisc.net/commands.html).

### Key/value features

You can use Vedis like a dictionary for simple key/value lookups:

```python

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
>>> 'k1' in db
False
>>> db['k1']
None
```

You can set and get multiple items at a time:

```python

>>> db.mset(dict(k1='v1', k2='v2', k3='v3'))
True

>>> db.mget(['k1', 'k2', 'missing key', 'k3'])
['v1', 'v2', None, 'v3']
```

In addition to storing string keys/values, you can also implement counters:

```python

>>> db.incr('counter')
1
>>> db.incr('counter')
2

>>> db.incr_by('counter', 10)
12
>>> db.decr('counter')
11
```

### Hashes

Vedis supports nested key/value lookups which have the additional benefit of supporting operations to retrieve all keys, values, the number of items in the hash, and so on.

```python

>>> h = db.Hash('some key')
>>> h['k1'] = 'v1'
>>> h.update(k2='v2', k3='v3')

>>> h
<Hash: {'k3': 'v3', 'k2': 'v2', 'k1': 'v1'}>

>>> h.to_dict()
{'k3': 'v3', 'k2': 'v2', 'k1': 'v1'}

>>> h.items()
[('k1', 'v1'), ('k3', 'v3'), ('k2', 'v2')]

>>> h.keys()
['k1', 'k3', 'k2']

>>> del h['k2']

>>> len(h)
2

>>> 'k1' in h
True

>>> [key for key in h]
['k1', 'k3']
```

### Sets

Vedis supports a set data-type which stores a unique collection of items.

```python

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

>>> del s['v2']
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
```

### Lists

Vedis also supports a list data type.

```python

>>> l = db.List('my list')
>>> l.append('v1')
1
>>> l.extend(['v2', 'v3', 'v4'])
4

>>> len(l)
4

>>> l[1]
'v2'

>>> l.pop(), l.pop()
('v1', 'v2')

>>> len(l)
2
```

### Misc

Vedis has a somewhat quirky collection of other miscellaneous commands. Below is a sampling:

```python

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
```

### Writing your own Vedis commands

It is easy to write your own Vedis commands:

```python

db = Vedis()

@db.register('CONCAT')
def concat(context, glue, *params):
    return glue.join(params)

@db.register('TITLE')
def title(context, *params):
    # The `context` can be used to access the key/value store.
    for param in params:
        context[param] = param.title()
    return True
```

Here is how you might call the custom commands:

```python

>>> print db.execute('CONCAT | foo bar baz')
foo|bar|baz

>>> db.execute('TITLE "testing" "this is a test" "another"')
True
>>> print db['testing']
Testing
>>> print db['this is a test']
This Is A Test

>>> title('foo', 'bar')  # Calling the wrapped function will go through Vedis.
True
>>> print db['foo']
Foo
>>> print db['bar']
Bar
```

-------------------------------------------

This code is based in part on [buaabyl's pyUnQLite](https://github.com/buaabyl/pyUnQLite/).
