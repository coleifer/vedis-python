.. _api:

API Documentation
=================


.. py:class:: Vedis([filename=':mem:'[, open_database=True]])

    The :py:class:`Vedis` object provides a pythonic interface for interacting
    with `vedis databases <http://vedis.symisc.net/>`_. Vedis is a lightweight,
    embedded NoSQL database modeled after Redis.

    :param str filename: The path to the database file. For in-memory databases, you can either leave this parameter empty or specify the string ``:mem:``.
    :param bool open_database: When set to ``True``, the database will be opened automatically when the class is instantiated. If set to ``False`` you will need to manually call :py:meth:`~Vedis.open`.

    .. note::
        Vedis supports in-memory databases, which can be created by passing in ``':mem:'`` as the database file. This is the default behavior if no database file is specified.

    Example usage:

    .. code-block:: pycon

        >>> db = Vedis()  # Create an in-memory database.
        >>> db['foo'] = 'bar'  # Use as a key/value store.
        >>> print db['foo']
        bar

        >>> db.update({'k0': 'v0', 'k1': 'v1', 'k2': 'v2', 'k3': 'v3'})

        >>> 'k3' in db
        True
        >>> 'k4' in db
        False
        >>> del db['k3']

        >>> db.append('k2', 'XXXX')
        >>> db.mget(['k1', 'k2', 'k3'])
        ['1', '2XXXX', None]

        >>> db.incr('counter_1')
        1
        >>> db.incr_by('counter_1', 10)
        11

        >>> hash_obj = db.Hash('my-hash')
        >>> hash_obj['k1'] = 'v1'
        >>> hash_obj.update(k2='v2', k3='v3')
        2
        >>> hash_obj.to_dict()
        {'k1': 'v1', 'k2': 'v2', 'k3': 'v3'}
        >>> hash_obj.items()
        [('k1', 'v1'), ('k2', 'v2'), ('k3', 'v3')]
        >>> [key for key in hash_obj]
        ['k1', 'k2', 'k3']
        >>> len(hash_obj)
        3

        >>> set_obj = db.Set('my-set')
        >>> set_obj.add('foo', 'bar', 'baz', 'foo')
        3
        >>> 'foo' in set_obj
        True
        >>> del set_obj['bar']
        1
        >>> set_obj.to_set()
        {'baz', 'foo'}
        >>> [item for item in set_obj]
        ['baz', 'foo']
        >>> len(set_obj)
        2

        >>> list_obj = db.List('my-list')
        >>> list_obj.extend(['foo', 'bar', 'baz', 'nug'])
        4
        >>> list_obj.append('another')
        5
        >>> [item for item in list_obj]
        ['foo', 'bar', 'baz', 'nug', 'another']
        >>> list_obj[1]
        'bar'
        >>> list_obj.pop()
        'foo'
        >>> len(l)
        4

    .. py:method:: open()

        Open the database connection.

    .. py:method:: close()

        Close the database connection.

        .. warning::
            If you are using a file-based database, by default any uncommitted changes will be committed when the database is closed. If you wish to discard uncommitted changes, you can use :py:meth:`~Vedis.disable_autocommit`.

    .. py:method:: __enter__()

        Use the database as a context manager, opening the connection and closing it at the end of the wrapped block:

        .. code-block:: python

            with Vedis('my_db.vdb') as db:
                db['foo'] = 'bar'

            # When the context manager exits, the database is closed.

    .. py:method:: disable_autocommit()

        When the database is closed, prevent any uncommitted writes from being saved.

        .. note:: This method only affects file-based databases.

    .. py:method:: set(key, value)

        Store a value in the given key.

        :param str key: Identifier used for storing data.
        :param str value: A value to store in Vedis.

        Example:

        .. code-block:: python

            db = Vedis()
            db.set('some key', 'some value')
            db.set('another key', 'another value')

        You can also use the dictionary-style ``[key] = value`` to store a value:

        .. code-block:: python

            db['some key'] = 'some value'

    .. py:method:: get(key)

        Retrieve the value stored at the given ``key``. If no value exists, a ``KeyError`` will be raised.

        :param str key: Identifier to retrieve.
        :returns: The data stored at the given key.
        :raises: ``KeyError`` if the given key does not exist.

        Example:

        .. code-block:: python

            db = Vedis()
            db.set('some key', 'some value')
            value = db.get('some key')

        You can also use the dictionary-style ``[key]`` lookup to retrieve a value:

        .. code-block:: python

            value = db['some key']

    .. py:method:: delete(key)

        Remove the key and its associated value from the database.

        :param str key: The key to remove from the database.
        :raises: ``KeyError`` if the given key does not exist.

        Example:

        .. code-block:: python

            def clear_cache():
                db.delete('cached-data')

        You can also use the python ``del`` keyword combined with a dictionary lookup:

        .. code-block:: python

            def clear_cache():
                del db['cached-data']

    .. py:method:: append(key, value)

        Append the given ``value`` to the data stored in the ``key``. If no data exists, the operation is equivalent to :py:meth:`~Vedis.set`.

        :param str key: The identifier of the value to append to.
        :param value: The value to append.

    .. py:method:: exists(key)

        Return whether the given ``key`` exists in the database. Oddly, this only
        seems to work for simple key/value pairs. If, for instance, you have stored
        a hash at the given key, ``exists`` will return ``False``.

        :param str key:
        :returns: A boolean value indicating whether the given ``key`` exists in the database.

        Example:

        .. code-block:: python

            def get_expensive_data():
                if not db.exists('cached-data'):
                    db.set('cached-data', calculate_expensive_data())
                return db.get('cached-data')

        You can also use the python ``in`` keyword to determine whether a key exists:

        .. code-block:: python

            def get_expensive_data():
                if 'cached-data' not in db:
                    db['cached-data'] = calculate_expensive_data()
                return db['cached-data']

    .. py:method:: update(data)

        :param dict data: Dictionary of data to store in the database.

        Set multiple key/value pairs in a single command, similar to Python's ``dict.update()``.

        Example:

        .. code-block:: python

            db = Vedis()
            db.update(dict(
                hostname=socket.gethostname(),
                user=os.environ['USER'],
                home_dir=os.environ['HOME'],
                path=os.environ['PATH']))

    .. py:method:: mget(keys)

        Retrieve the values of multiple keys in a single command. In the event a key
        does not exist, ``None`` will be returned for that particular value.

        :param list keys: A list of one or more keys to retrieve.
        :returns: The values for the given keys.

        Example:

        .. code-block:: pycon

            >>> db.update(dict(k1='v1', k2='v2', k3='v3', k4='v4'))
            >>> db.mget(['k1', 'k3', 'missing', 'k4'])
            ['v1', 'v3', None, 'v4']

    .. py:method:: mset(data)

        :param dict data: Dictionary of data to store in the database.

        Set multiple key/value pairs in a single command. This is equivalent to the :py:meth:`~Vedis.update` method.

    .. py:method:: setnx(key, value)

        Set the value for the given key *only* if the key does not exist.

        :returns: ``True`` if the value was set, ``False`` if the key already existed.

        Example:

        .. code-block:: python

            def create_user(email, password_hash):
                if db.setnx(email, password_hash):
                    print 'User added successfully'
                    return True
                else:
                    print 'Error: username already taken.'
                    return False

    .. py:method:: msetnx(kwargs)

        Similar to :py:meth:`~Vedis.update`, except that existing keys will not be overwritten.

        :returns: ``True`` on success.

        Example:

        .. code-block:: pycon

            >>> db.msetnx({'k1': 'v1', 'k2': 'v2'})
            >>> db.mget(['k1', 'k2'])
            ['v1', 'v2']

            >>> db.msetnx({'k1': 'v1x', 'k2': 'v2x', 'k3': 'v3x'})
            >>> db.mget(['k1', 'k2', 'k3'])
            ['v1', 'v2', 'v3x']

    .. py:method:: get_set(key, value)

        Get the value at the given ``key`` and set it to the new ``value`` in a single operation.

        :returns: The original value at the given ``key``.

        Example:

        .. code-block:: pycon

            >>> db['k1'] = 'v1'
            >>> db.get_set('k1', 'v-x')
            'v1'

            >>> db['k1']
            'v-x'

    .. py:method:: incr(key)

        Increment the value stored in the given ``key`` by ``1``. If no value exists or the value
        is not an integer, the counter will be initialized at zero then incremented.

        :returns: The integer value stored in the given counter.

        .. code-block:: pycon

            >>> db.incr('my-counter')
            1
            >>> db.incr('my-counter')
            2

    .. py:method:: decr(key)

        Decrement the value stored in the given ``key`` by ``1``. If no value exists or the value
        is not an integer, the counter will be initialized at zero then decremented.

        :returns: The integer value stored in the given counter.

        Example:

        .. code-block:: pycon

            >> db.decr('my-counter')
            3
            >> db.decr('my-counter')
            2
            >> db.decr('does-not-exist')
            -1

    .. py:method:: incr_by(key, amt)

        Increment the given ``key`` by the integer ``amt``. This method has the same behavior as
        :py:meth:`~Vedis.incr`.

    .. py:method:: decr_by(key, amt)

        Decrement the given ``key`` by the integer ``amt``. This method has the same behavior as
        :py:meth:`~Vedis.decr`.

    .. py:method:: begin()

        Begin a transaction.

    .. py:method:: rollback()

        Roll back the current transaction.

    .. py:method:: commit()

        Commit the current transaction.

    .. py:method:: transaction()

        Create a context manager for performing multiple operations in a transaction.

        .. warning::
            Transactions occur at the disk-level and have no effect on in-memory databases.

        Example:

        .. code-block:: python

            # Transfer $100 in a transaction.
            with db.transaction():
                db['from_acct'] = db['from_account'] - 100
                db['to_acct'] = db['to_acct'] + 100

            # Make changes and then roll them back.
            with db.transaction():
                db['foo'] = 'bar'
                db.rollback()  # Whoops, do not commit these changes.

    .. py:method:: commit_on_success(fn)

        Function decorator that will cause the wrapped function to have all statements wrapped in a transaction. If the function returns without an exception, the transaction is committed. If an exception occurs in the function, the transaction is rolled back.

        Example:

        .. code-block:: pycon

            >>> @db.commit_on_success
            ... def save_value(key, value, exc=False):
            ...     db[key] = value
            ...     if exc:
            ...         raise Exception('uh-oh')
            ...
            >>> save_value('k3', 'v3')
            >>> save_value('k3', 'vx', True)
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
              File "unqlite/core.py", line 312, in wrapper
                return fn()
              File "<stdin>", line 5, in save_value
            Exception: uh-oh
            >>> db['k3']
            'v3'

    .. py:method:: Hash(key)

        Create a :py:class:`Hash` object, which provides a dictionary-like
        interface for working with Vedis hashes.

        :param str key: The key for the Vedis hash object.
        :returns: a :py:class:`Hash` object representing the Vedis hash at the
                  specified key.

        Example:

        .. code-block:: pycon

            >>> my_hash = db.Hash('my_hash')
            >>> my_hash.update(k1='v1', k2='v2')
            >>> my_hash.to_dict()
            {'k2': 'v2', 'k1': 'v1'}

    .. py:method:: hset(hash_key, key, value)

        Set the value for the key in the Vedis hash identified by ``hash_key``.

        Example:

        .. code-block:: pycon

            >>> db.hset('my_hash', 'k3', 'v3')
            >>> db.hget('my_hash', 'k3')
            'v3'

    .. py:method:: hsetnx(hash_key, key, value)

        Set a value for the given key in a Vedis hash only if the key
        does not already exist. Returns boolean indicating whether the
        value was successfully set.

        :rtype: bool

        Example:

        .. code-block:: pycon

            >>> db.hsetnx('my_hash', 'kx', 'vx')
            True
            >>> db.hsetnx('my_hash', 'kx', 'vx')
            False

    .. py:method:: hget(hash_key, key)

        Retrieve the value for the key in the Vedis hash identified by ``hash_key``.

        :returns: The value for the given key, or ``None`` if the key does not
                  exist.

        Example:

        .. code-block:: pycon

            >>> db.hset('my_hash', 'k3', 'v3')
            >>> db.hget('my_hash', 'k3')
            'v3'

    .. py:method:: hdel(hash_key, key)

        Delete a ``key`` from a Vedis hash. If the key does not exist in the
        hash, the operation is a no-op.

        :returns: The number of keys deleted.

        Example:

        .. code-block:: pycon

            >>> db.hdel('my_hash', 'k3')
            1
            >>> db.hget('my_hash', 'k3') is None
            True

    .. py:method:: hkeys(hash_key)

        Get the keys for the Vedis hash identified by ``hash_key``.

        :returns: All keys for the Vedis hash.

        Example:

        .. code-block:: pycon

            >>> db.hkeys('my_hash')
            ['k2', 'k1']

    .. py:method:: hvals(hash_key)

        Get the values for the Vedis hash identified by ``hash_key``.

        :returns: All values for the Vedis hash.

        Example:

        .. code-block:: pycon

            >>> db.hvals('my_hash')
            ['v2', 'v1']

    .. py:method:: hgetall(hash_key)

        Return a ``dict`` containing all items in the Vedis hash identified
        by ``hash_key``.

        :returns: A dictionary containing the key/value pairs stored in the
                  given Vedis hash, or an empty ``dict`` if a hash does not exist at the
                  given key.
        :rtype: dict

        Example:

        .. code-block:: pycon

            >>> db.hgetall('my_hash')
            {'k2': 'v2', 'k1': 'v1'}

            >>> db.hgetall('does not exist')
            {}

    .. py:method:: hitems(hash_key)

        Get a list to key/value pairs stored in the given Vedis hash.

        :returns: A list of key/value pairs stored in the given Vedis hash, or
                  an empty list if a hash does not exist at the given key.
        :rtype: list of 2-tuples

        Example:

        .. code-block:: pycon

            >>> db.hitems('my_hash')
            [('k2', 'v2'), ('k1', 'v1')]

    .. py:method:: hlen(hash_key)

        Return the number of items stored in a Vedis hash. If a hash does not
        exist at the given key, ``0`` will be returned.

        :rtype: int

        Example:

        .. code-block:: pycon

            >>> db.hlen('my_hash')
            2
            >>> db.hlen('does not exist')
            0

    .. py:method:: hexists(hash_key, key)

        Return whether the given key is stored in a Vedis hash. If a hash does not
        exist at the given key, ``False`` will be returned.

        :rtype: bool

        Example:

        .. code-block:: pycon

            >>> db.hexists('my_hash', 'k1')
            True
            >>> db.hexists('my_hash', 'kx')
            False
            >>> db.hexists('does not exist', 'kx')
            False

    .. py:method:: hmset(hash_key, data)

        Set multiple key/value pairs in the given Vedis hash. This method is
        analagous to Python's ``dict.update``.

        Example:

        .. code-block:: pycon

            >>> db.hmset('my_hash', {'k1': 'v1', 'k2': 'v2', 'k3': 'v3', 'k4': 'v4'})
            >>> db.hgetall('my_hash')
            {'k3': 'v3', 'k2': 'v2', 'k1': 'v1', 'k4': 'v4'}

    .. py:method:: hmget(hash_key, keys)

        Return the values for multiple keys in a Vedis hash. If the key does
        not exist in the given hash, ``None`` will be returned for the missing
        key.

        Example:

        .. code-block:: pycon

            >>> db.hmget('my_hash', ['k1', 'k4', 'missing', 'k2'])
            ['v1', 'v4', None, 'v2']

    .. py:method:: hmdel(hash_key, keys)

        Delete multiple keys from a Vedis hash.

        :returns: The number of keys actually deleted.

        Example:

        .. code-block:: pycon

            >>> db.hmdel('my_hash', ['k1', 'k2', 'invalid-key'])
            2

    .. py:method:: Set(key)

        Create a :py:class:`Set` object, which provides a set-like
        interface for working with Vedis sets.

        :param str key: The key for the Vedis set object.
        :returns: a :py:class:`Set` object representing the Vedis set at the
                  specified key.

        Example:

        .. code-block:: pycon

            >>> my_set = db.Set('my_set')
            >>> my_set.add('v1', 'v2', 'v3')
            3
            >>> my_set.to_set()
            set(['v1', 'v2', 'v3'])

    .. py:method:: sadd(key, value)

        Add a single value to a Vedis set, returning the number of
        items added.

        Example:

        .. code-block:: pycon

            >>> db.sadd('my_set', 'v1')
            1
            >>> db.sadd('my_set', 'v2')
            1
            >>> db.smembers('my_set')
            {'v1', 'v2'}

    .. py:method:: smadd(key, values)

        Add one or more values to a Vedis set, returning the number of
        items added.

        Unlike :py:meth:`~Vedis.sadd`, ``smadd`` accepts a list of values to add to the set.

        Example:

        .. code-block:: pycon

            >>> db.smadd('my_set', ['v1', 'v2', 'v3'])
            >>> db.smembers('my_set')
            {'v1', 'v2', 'v3'}

    .. py:method:: scard(key)

        Return the cardinality, or number of items, in the given set. If
        a Vedis set does not exist at the given key, ``0`` will be returned.

        Example:

        .. code-block:: pycon

            >>> db.scard('my_set')
            3
            >>> db.scard('does not exist')
            0

    .. py:method:: sismember(key, value)

        Return a boolean indicating whether the provided value is a member
        of a Vedis set. If a Vedis set does not exist at the given key,
        ``False`` will be returned.

        Example:

        .. code-block:: pycon

            >>> db.sismember('my_set', 'v1')
            True
            >>> db.sismember('my_set', 'vx')
            False
            >>> print db.sismember('does not exist', 'xx')
            False

    .. py:method:: spop(key)

        Remove and return the last record from a Vedis set. If a Vedis set does
        not exist at the given key, or the set is empty, ``None`` will be returned.

        Example:

        .. code-block:: pycon

            >>> db.sadd('my_set', 'v1', 'v2', 'v3')
            3
            >>> db.spop('my_set')
            'v3'

    .. py:method:: speek(key)

        Return the last record from a Vedis set without removing it. If a Vedis
        set does not exist at the given key, or the set is empty, ``None`` will
        be returned.

        Example:

        .. code-block:: pycon

            >>> db.sadd('my_set', 'v1', 'v2', 'v3')
            3
            >>> db.speek('my_set')
            'v3'

    .. py:method:: stop(key)

        Return the first record from a Vedis set without removing it.

        Example:

        .. code-block:: pycon

            >>> db.sadd('my_set', 'v1', 'v2', 'v3')
            >>> db.stop('my_set')
            'v1'

    .. py:method:: srem(key, value)

        Remove the given value from a Vedis set.

        :returns: The number of items removed.

        Example:

        .. code-block:: pycon

            >>> db.sadd('my_set', 'v1', 'v2', 'v3')
            3
            >>> db.srem('my_set', 'v2')
            1
            >>> db.srem('my_set', 'v2')
            0
            >>> list(db.smembers('my_set'))
            ['v1', 'v3']

    .. py:method:: smrem(key, values)

        Remove one or more values from the Vedis set.

        :returns: The number of items removed.

        Example:

        .. code-block:: pycon

            >>> db.smadd('my_set', ['v1', 'v2', 'v3'])
            3
            >>> db.smrem('my_set', ['v1', 'v2', 'xxx'])
            >>> db.smembers('my_set')
            {'v3'}

    .. py:method:: smembers(key)

        Return all members of a given set.

        :rtype: set

        Example:

        .. code-block:: pycon

            >>> db.smembers('my_set')
            {'v1', 'v3'}

    .. py:method:: sdiff(k1, k2)

        Return the set difference of two Vedis sets identified by ``k1`` and ``k2``.

        Example:

        .. code-block:: pycon

            >>> db.sadd('my_set', 'v1', 'v2', 'v3')
            3
            >>> db.sadd('other_set', 'v2', 'v3', 'v4')
            3
            >>> db.sdiff('my_set', 'other_set')
            {'v1'}

    .. py:method:: sinter(k1, k2)

        Return the intersection of two Vedis sets identified by ``k1`` and ``k2``.

        Example:

        .. code-block:: pycon

            >>> db.sadd('my_set', 'v1', 'v2', 'v3')
            3
            >>> db.sadd('other_set', 'v2', 'v3', 'v4')
            3
            >>> db.sinter('my_set', 'other_set')
            {'v3', 'v2'}

    .. py:method:: List(key)

        Create a :py:class:`List` object, which provides a list-like
        interface for working with Vedis lists.

        :param str key: The key for the Vedis list object.
        :returns: a :py:class:`List` object representing the Vedis list at the
                  specified key.

        Example:

        .. code-block:: pycon

            >>> my_list = db.List('my_list')
            >>> my_list.append('i1')
            >>> my_list.extend(['i2', 'i3'])
            >>> my_list[0]
            'i1'
            >>> my_list.pop()
            'i1'
            >>> len(my_list)
            2

    .. py:method:: lpush(key, value)

        Append one value to a Vedis list, returning the number of
        items added.

        Example:

        .. code-block:: pycon

            >>> db.lpush('my_list', 'i1')
            1

    .. py:method:: lmpush(key, values)

        Append one or more values to a Vedis list, returning the number of
        items added.

        Example:

        .. code-block:: pycon

            >>> db.lmpush('my_list', ['i2', 'i3', 'i4'])
            3

    .. py:method:: lindex(key, idx)

        Returns the element at the given index in the Vedis list. Indices are
        zero-based, and negative indices can be used to designate elements
        starting from the end of the list.

        Example:

        .. code-block:: pycon

            >>> db.lmpush('my_list', ['i1', 'i2', 'i3'])
            >>> db.lindex('my_list', 0)
            'i1'
            >>> db.lindex('my_list', -1)
            'i3'

    .. py:method:: llen(key)

        Return the length of a Vedis list.

        Example:

        .. code-block:: pycon

            >>> db.llen('my_list')
            3
            >>> db.llen('does not exist')
            0

    .. py:method:: lpop(key)

        Remove and return the first element of a Vedis list. If no elements
        exist, ``None`` is returned.

        Example:

        .. code-block:: pycon

            >>> db.lmpush('a list', ['i1', 'i2'])
            2
            >>> db.lpop('a list')
            'i1'

    .. py:method:: register(command_name)

        Function decorator used to register user-defined Vedis commands.
        User-defined commands must accept a special :py:class:`VedisContext` as their
        first parameter, followed by any number of parameters specified when the command was invoked. The following
        are valid return types for user-defined commands:

        * lists (arbitrarily nested)
        * strings
        * boolean values
        * integers
        * floating point numbers
        * ``None``

        Here is a simple example of a custom command that converts its arguments
        to title-case:

        .. code-block:: python

            @db.register('TITLE')
            def title_cmd(vedis_ctx, *params):
                return [param.title() for param in params]

        Here is how you might call your user-defined function:

        .. code-block:: pycon

            >>> db.execute('TITLE %s %s %s', ('foo', 'this is a test', 'bar'))
            ['Foo', 'This Is A Test', 'Bar']

        You can also call the wrapped function directly, and the call will be routed through Vedis:

        .. code-block:: pycon

            >>> title('foo', 'this is a test', 'bar')
            ['Foo', 'This Is A Test', 'Bar']

        For more information, see the :ref:`custom_commands` section.

    .. py:method:: delete_command(command_name)

        Unregister a custom command.

    .. py:method:: strlen(key)

        Return the length of the value stored at the given key.

        Example:

        .. code-block:: pycon

            >>> db = Vedis()
            >>> db['foo'] = 'testing'
            >>> db.strlen('foo')
            7

    .. py:method:: copy(src, dest)

        Copy the contents of one key to another, leaving the original intact.

    .. py:method:: move(src, dest)

        Move the contents of one key to another, deleting the original key.

    .. py:method:: strip_tags(html)

        Remove HTML formatting from a given string.

        :param str html: A string containing HTML.
        :returns: A string with all HTML removed.

        Example:

        .. code-block:: pycon

            >>> db.strip_tags('<p>This <span>is</span> <a href="#">a <b>test</b></a>.</p>')
            'This is a test.'

    .. py:method:: str_split(s[, nchars=1])

        Split the given string, ``s``.

        Example:

        .. code-block:: pycon

            >>> db.str_split('abcdefghijklmnop', 5)
            ['abcde', 'fghij', 'klmno', 'p']

    .. py:method:: size_format(nbytes)

        Return a user-friendly representation of a given number of bytes.

        Example:

        .. code-block:: pycon

            >>> db.size_format(1337)
            '1.3 KB'
            >>> db.size_format(1337000)
            '1.2 MB'

    .. py:method:: soundex(s)

        Calculate the ``soundex`` value for a given string.

        Example:

        .. code-block:: pycon

            >>> db.soundex('howdy')
            'H300'
            >>> db.soundex('huey')
            'H000'

    .. py:method:: base64(data)

        Encode ``data`` in base64.

        Example:

        .. code-block:: pycon

            >>> db.base64('hello')
            'aGVsbG8='

    .. py:method:: base64_decode(data)

        Decode the base64-encoded ``data``.

        Example:

        .. code-block:: pycon

            >>> db.base64_decode('aGVsbG8=')
            'hello'

    .. py:method:: rand(lower_bound, upper_bound)

        Return a random integer within the lower and upper bounds (inclusive).

    .. py:method:: randstr(nbytes)

        Return a random string of ``nbytes`` length, made up of the characters a-z.

    .. py:method:: time()

        Return the current GMT time, formatted as HH:MM:SS.

    .. py:method:: date()

        Return the current date in ISO-8601 format (YYYY-MM-DD).

    .. py:method:: operating_system()

        Return a brief description of the host operating system.

    .. py:method:: table_list()

        Return a list of all vedis tables (i.e. Hashes, Sets, List) in memory.

    .. py:method:: execute(cmd[, params=None[, result=True]])

        Execute a Vedis command.

        :param str cmd: The command to execute.
        :param tuple params: A tuple of parameters to pass into the command.
        :param bool result: Return the result of this command.

        Example:

        .. code-block:: python

            db = Vedis()

            # Execute a command, ignoring the result.
            db.execute('HSET %s %s %s', ('hash_key', 'key', 'some value'))

            # Execute a command that returns a single result.
            val = db.execute('HGET %s %s', ('hash_key', 'key'))

            # Execute a command return returns multiple values.
            keys = db.execute('HKEYS %s', ('hash_key',))
            for key in keys:
                print 'Hash "hash_key" contains key "%s"' % key


Hash objects
------------

.. py:class:: Hash(vedis, key)

    Provides a high-level API for working with Vedis hashes. As much as seemed
    sensible, the :py:class:`Hash` acts like a python dictionary.

    .. note::
        This class should not be constructed directly, but through the
        factory method :py:meth:`Vedis.Hash`.

    Here is an example of how you might use the various ``Hash`` APIs:

    .. code-block:: pycon

        >>> h = db.Hash('my_hash')

        >>> h['k1'] = 'v1'
        >>> h.update(k2='v2', k3='v3')

        >>> len(h)
        3

        >>> 'k1' in h
        True
        >>> 'k4' in h
        False

        >>> h.to_dict()
        {'k3': 'v3', 'k2': 'v2', 'k1': 'v1'}

        >>> h.keys()
        ['k1', 'k3', 'k2']
        >>> h.values()
        ['v1', 'v3', 'v2']
        >>> h.items()
        [('k1', 'v1'), ('k3', 'v3'), ('k2', 'v2')]

        >>> del h['k2']
        >>> h.items()
        [('k1', 'v1'), ('k3', 'v3')]

        >>> h.mget('k3', 'kx', 'k1')
        ['v3', None, 'v1']

        >>> h
        <Hash: {'k3': 'v3', 'k1': 'v1'}>

Set objects
-----------

.. py:class:: Set(vedis, key)

    Provides a high-level API for working with Vedis sets. As much as seemed
    sensible, the :py:class:`Set` acts like a python set.

    .. note::
        This class should not be constructed directly, but through the
        factory method :py:meth:`Vedis.Set`.

    Here is an example of how you might use the various ``Set`` APIs:

    .. code-block:: pycon

        >>> s = db.Set('my_set')

        >>> s.add('v1', 'v2', 'v1', 'v3')
        4
        >>> len(s)
        3

        >>> [item for item in s]
        ['v1', 'v2', 'v3']

        >>> s.top()
        'v1'
        >>> s.peek()
        'v3'
        >>> s.pop()
        'v3'

        >>> 'v2' in s
        True
        >>> 'v3' in s
        False

        >>> s.add('v3', 'v4')
        2
        >>> del s['v4']
        >>> s.to_set()
        {'v1', 'v2', 'v3'}

    Vedis also supports set difference and intersection:

    .. code-block:: pycon

        >>> s2 = db.Set('other_set')
        >>> s2.add('v3', 'v4', 'v5')
        3

        >>> s - s2
        {'v1', 'v2'}

        >>> s2 - s
        {'v4', 'v5'}

        >>> s & s2
        {'v3'}

List objects
------------

.. py:class:: List(vedis, key)

    Provides a high-level API for working with Vedis lists.

    .. note::
        This class should not be constructed directly, but through the
        factory method :py:meth:`Vedis.List`.

    Here is an example of how you might use the various ``List`` APIs:

    .. code-block:: pycon

        >>> l = db.List('my_list')

        >>> l.append('v1')
        1
        >>> l.extend(['v2', 'v3', 'v4'])
        4

        >>> len(l)
        4

        >>> l[0]
        'v1'
        >>> l[-1]
        'v4'

        >>> [item for item in l]
        ['v1', 'v2', 'v3', 'v4']

        >>> l.pop()
        'v1'

Vedis Context
-------------

When a user-defined command is executed, the first parameter sent to the
callback is a ``vedis_context`` instance. The ``vedis_context`` allows user-defined
commands to set return codes (handled automatically by vedis-python), but
perhaps more interestingly, modify other keys and values in the database.

In this way, your user-defined command can set, get, and delete keys in
the vedis database. Because the vedis_context APIs are a bit low-level,
vedis-python wraps the ``vedis_context``, providing a nicer API to work with.

.. py:class:: VedisContext(vedis_context)

    This class will almost never be instantiated directly, but will instead
    by created by vedis-python when executing a user-defined callback.

    :param vedis_context: A pointer to a ``vedis_context``.

    Usage:

    .. code-block:: python

        @db.register('TITLE_VALUES')
        def title_values(context, *values):
            """
            Create key/value pairs for each value consisting of the
            original value -> the title-cased version of the value.

            Returns the number of values processed.
            """
            for value in values:
                context[value] = value.title()
            return len(values)

    .. code-block:: pycon

        >>> db.execute('TITLE_VALUES %s %s', ('val 1', 'another value'))
        2
        >>> db['val 1']
        'Val 1'
        >>> db['another val']
        'Another Val'

    .. py:method:: fetch(key)

        Return the value of the given key. Identical to :py:meth:`Vedis.get`.

        Instead of calling ``fetch()`` you can also use a dictionary-style
        lookup on the context:

        .. code-block:: python

            @db.register('MY_COMMAND')
            def my_command(context, *values):
                some_val = context['the key']
                # ...

    .. py:method:: store(key, value)

        Set the value of the given key. Identical to :py:meth:`Vedis.set`.

        Instead of calling ``store()`` you can also use a dictionary-style
        assignment on the context:

        .. code-block:: python

            @db.register('MY_COMMAND')
            def my_command(context, *values):
                context['some key'] = 'some value'
                # ...

    .. py:method:: append(key, value)

        Append a value to the given key. If the key does not exist, the
        operation is equivalent to :py:meth:`~VedisContext.store`. Identical
        to :py:meth:`Vedis.append`.

    .. py:method:: delete(key)

        Delete the given key. Identical to :py:meth:`Vedis.delete`.

        Instead of calling ``delete()`` you can also use a the python
        ``del`` keyword:

        .. code-block:: python

            @db.register('MY_COMMAND')
            def my_command(context, *values):
                del context['some key']
                # ...

    .. py:method:: exists(key)

        Check for the existence of the given key. Identical to :py:meth:`Vedis.exists`.

        Instead of calling ``exists()`` you can also use a the python
        ``in`` keyword:

        .. code-block:: python

            @db.register('MY_COMMAND')
            def my_command(context, *values):
                if 'some key' in context:
                    # ...

Transactions
------------

.. py:class:: Transaction(vedis)

    :param Vedis vedis: An :py:class:`Vedis` instance.

    Context-manager for executing wrapped blocks in a transaction. Rather than instantiating this object directly, it is recommended that you use :py:meth:`Vedis.transaction`.

    Example:

    .. code-block:: python

        with db.transaction():
            db['from_acct'] = db['from_acct'] + 100
            db['to_acct'] = db['to_acct'] - 100

    To roll back changes inside a transaction, call :py:meth:`Vedis.rollback`:

    .. code-block:: python

        with db.transaction():
            db['from_acct'] = db['from_acct'] + 100
            db['to_acct'] = db['to_acct'] - 100
            if int(db['to_acct']) < 0:
                db.rollback()  # Not enough funds!
