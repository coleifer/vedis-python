.. quickstart:

Quickstart
==========

Below is a sample interactive console session designed to show some of the basic features and functionality of the vedis-python library. Full API documentation will be available soon.

Key/value features
------------------

You can use Vedis like a dictionary for simple key/value lookups:

.. code-block:: pycon

    In [1]: from vedis import Vedis

    In [2]: db = Vedis(':memory:')  # Create an in-memory database. Alternatively you could supply a filename for an on-disk database.

    In [3]: db['k1'] = 'v1'

    In [4]: db['k1']
    Out[4]: 'v1'

    In [5]: db.append('k1', 'more data')

    In [6]: db['k1']
    Out[6]: 'v1more data'

    In [7]: del db['k1']

    In [8]: db['k1']
    ---------------------------------------------------------------------------
    KeyError                                  Traceback (most recent call last)
    <ipython-input-8-a988c6a20437> in <module>()
    ----> 1 db['k1']

    /home/charles/tmp/scrap/z1/src/vedis/vedis/core.pyc in fetch(self, key, buf_size)
        125             return buf.raw[:nbytes.value]
        126         elif rc == SXERR_NOTFOUND:
    --> 127             raise KeyError(key)
        128         handle_return_value(rc)
        129

    KeyError: 'k1'

You can set and get multiple items at a time:

.. code-block:: pycon

    In [10]: db.mset(k1='v1', k2='v2', k3='v3')
    Out[10]: True

    In [11]: db.mget('k1', 'k2', 'missing key', 'k3')
    Out[11]: <generator object iter_vedis_array at 0x7f37dd58be10>

    In [12]: list(db.mget('k1', 'k2', 'missing key', 'k3'))
    Out[12]: ['v1', 'v2', None, 'v3']

In addition to storing string keys/values, you can also implement counters:

.. code-block:: pycon

    In [13]: db.incr('counter')
    Out[13]: 1

    In [14]: db.incr('counter')
    Out[14]: 2

    In [15]: db.incr_by('counter', 10)
    Out[15]: 12

    In [16]: db.decr('counter')
    Out[16]: 11

Copying and Moving
------------------

Keys can be copied or moved.

.. code-block:: pycon

    In [55]: db['k1']
    Out[55]: 'v1'

    In [56]: db.copy('k1', 'k-new1')
    Out[56]: True

    In [57]: db['k-new1']
    Out[57]: 'v1'

    In [58]: db.move('k-new1', 'k-moved')
    Out[58]: True

    In [59]: db['k-moved']
    Out[59]: 'v1'

    In [60]: db['k-new1']  # Raises KeyError

Hashes
------

Vedis supports nested key/value lookups which have the additional benefit of supporting operations to retrieve all keys, values, the number of items in the hash, and so on.

.. code-block:: pycon

    In [17]: db.hset('my_hash', 'k1', 'v1')

    In [18]: db.hmset('my_hash', k2='v2', k3='v3')

    In [19]: db.hgetall('my_hash')
    Out[19]: {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}

    In [20]: list(db.hmget('my_hash', 'k1', 'k3'))
    Out[20]: ['v1', 'v3']

    In [21]: db.hlen('my_hash')
    Out[21]: 3

    In [22]: db.hkeys('my_hash')
    Out[22]: <generator object iter_vedis_array at 0x7f37dd59d410>

    In [23]: list(db.hkeys('my_hash'))
    Out[23]: ['k1', 'k3', 'k2']

    In [24]: list(db.hvals('my_hash'))
    Out[24]: ['v1', 'v3', 'v2']

Sets
----

Vedis supports a set data-type which stores a unique collection of items.

.. code-block:: pycon

    In [29]: db.sadd('my_set', 'item1')
    Out[29]: 1

    In [30]: db.sadd('my_set', 'item2')
    Out[30]: 1

    In [31]: db.scard('my_set')
    Out[31]: 2

    In [32]: db.smembers('my_set')
    Out[32]: <generator object iter_vedis_array at 0x7f37dd59d5a0>

    In [33]: list(db.smembers('my_set'))
    Out[33]: ['item1', 'item2']

    In [34]: db.speek('my_set')
    Out[34]: 'item2'

    In [35]: db.stop('my_set')
    Out[35]: 'item1'

    In [36]: db.spop('my_set')
    Out[36]: 'item2'

    In [37]: db.sismember('my_set', 'item1')
    Out[37]: True

    In [38]: db.srem('my_set', 'item1')
    Out[38]: 1

If you have two sets, you can calculate the intersection and difference:

.. code-block:: pycon

    In [39]: db.sadd('s1', 'i1')
    Out[39]: 1

    In [40]: db.sadd('s1', 'i2')
    Out[40]: 1

    In [41]: db.sadd('s2', 'i2')
    Out[41]: 1

    In [42]: db.sadd('s2', 'i3')
    Out[42]: 1

    In [43]: db.sinter('s1', 's2')
    Out[43]: <generator object iter_vedis_array at 0x7f37dd59da50>

    In [44]: list(db.sinter('s1', 's2'))
    Out[44]: ['i2']

    In [45]: list(db.sdiff('s1', 's2'))
    Out[45]: ['i1']

Lists
-----

Vedis also supports a list data type.

.. code-block:: pycon

    In [46]: db.lpush('my_list', 'i1')
    Out[46]: 1

    In [47]: db.lpush('my_list', 'i2')
    Out[47]: 2

    In [48]: db.llen('my_list')
    Out[48]: 2

    In [49]: db.lindex('my_list', 0)
    Out[49]: 'i1'

    In [50]: db.lindex('my_list', 1)
    Out[50]: 'i2'

    In [51]: db.lindex('my_list', 2)

    In [52]: db.lpop('my_list')
    Out[52]: 'i1'

Misc
----

Vedis has a somewhat quirky collection of other miscellaneous commands. Below is a sampling:

.. code-block:: pycon

    In [64]: db.base64('encode me')
    Out[64]: 'ZW5jb2RlIG1l'

    In [65]: db.base64_decode(_)
    Out[65]: 'encode me'

    In [66]: db.random_string(10)
    Out[66]: 'raurquvsnx'

    In [67]: db.rand(1, 6)
    Out[67]: 4

    In [68]: db.size_format(100000)
    Out[68]: '97.6 KB'

    In [69]: list(db.str_split('abcdefghijklmnop', 5))
    Out[69]: ['abcde', 'fghij', 'klmno', 'p']

    In [70]: db['data'] = 'abcdefghijklmnop'

    In [71]: db.strlen('data')
    Out[71]: 16

    In [72]: db.strip_tags('<p>This <span>is</span> a <a href="#">test</a>.</p>')
    Out[72]: 'This is a test.'
