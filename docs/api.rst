.. _api:

API Documentation
=================

.. py:class:: Vedis([database=':mem:'])

    The :py:class:`Vedis` object provides a pythonic interface for interacting
    with `vedis databases <http://vedis.symisc.net/>`_. Vedis is a lightweight,
    embedded NoSQL database modeled after Redis.

    :param str database: The path to the database file.

    .. note::
        Vedis supports in-memory databases, which can be created by passing
        in ``':mem:'`` as the database file. This is the default behavior if
        no database file is specified.

    .. py:method:: close()

        Close the database connection.

    .. py:method:: execute(cmd[, params=None[, nlen=-1[, result=False[, iter_result=False]]]])

        Execute a Vedis command, optionally returning the result of the command.

        :param str cmd: The command to execute.
        :param list params: A list of parameters to pass into the command.
        :param int nlen: The number of parameters. By default this value is ``-1``, which means the count will be determined automatically.
        :param bool result: Return the result of this command.
        :param bool iter_result: Return an iterator that will yield the results of this command.

        Example:

        .. code-block:: python

            db = Vedis()

            # Execute a command, ignoring the result.
            db.execute('HSET %s %s %s', ['hash_key', 'key', 'some value'])

            # Execute a command that returns a single result.
            val = db.execute('HGET %s %s', ['hash_key', 'key'], result=True)

            # Execute a command return returns multiple values.
            gen = db.execute('HKEYS %s', ['hash_key'], iter_result=True)
            for key in gen:
                print 'Hash "hash_key" contains key "%s"' % key

    .. py:method:: get_result()

        Return the result of the last-executed Vedis command.

    .. py:method:: iter_result()

        Return a generator that will successively yield values from the last-executed
        Vedis command.

    .. py:method:: store(key, value)

        Store a value in the given key.

        :param str key: Identifier used for storing data.
        :param any value: A value to store in Vedis.

        Example:

        .. code-block:: python

            db = Vedis()
            db.store('some key', 'some value')
            db.store('another key', 'another value')

        You can also use the dictionary-style ``[key] = value`` to store a value:

        .. code-block:: python

            db['some key'] = 'some value'

    .. py:method:: fetch(key[, bufsize=4096])

        Retrieve the value stored at the given ``key``. If no value exists, a ``KeyError`` will be raised.

        :param str key: Identifier to retrieve
        :returns: The data stored at the given key.
        :raises: ``KeyError`` if the key does not exist.

        Example:

        .. code-block:: python

            db = Vedis()
            db.store('some key', 'some value')
            value = db.fetch('some key')

        You can also use the dictionary-style ``[key]`` lookup to retrieve a value:

        .. code-block:: python

            value = db['some key']

    .. py:method:: append(key, value)

        Append the given ``value`` to the data stored in the ``key``. If no data exists, the operation
        is equivalent to :py:meth:`~Vedis.store`.

        :param str key: The identifier of the value to append to.
        :param value: The value to append.

    .. py:method:: exists(key)

        Return whether the given ``key`` exists in the database.

        :param str key:
        :returns: A boolean value indicating whether the given ``key`` exists in the database.

        Example:

        .. code-block:: python

            def get_expensive_data():
                if not db.exists('cached-data'):
                    db.store('cached-data', calculate_expensive_data())
                return db.fetch('cached-data')

        You can also use the python ``in`` keyword to determine whether a key exists:

        .. code-block:: python

            def get_expensive_data():
                if 'cached-data' not in db:
                    db['cached-data'] = calculate_expensive_data()
                return db['cached-data']

    .. py:method:: delete(key)

        Remove the key and its associated value from the database.

        :param str key: The key to remove from the database.

        Example:

        .. code-block:: python

            def clear_cache():
                db.delete('cached-data')

        You can also use the python ``del`` keyword combined with a dictionary lookup:

        .. code-block:: python

            def clear_cache():
                del db['cached-data']

    .. py:method:: update(**kwargs)

        Set multiple key/value pairs in a single command, similar to Python's ``dict.update()``.

        Example:

        .. code-block:: python

            db = Vedis()
            db.update(
                hostname=socket.gethostname(),
                user=os.environ['USER'],
                home_dir=os.environ['HOME'],
                path=os.environ['PATH'])

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

    .. py:method:: mget(*keys)

        Retrieve the values of multiple keys in a single command. In the event a key
        does not exist, ``None`` will be returned for that particular value.

        :param keys: One or more keys to retrieve.
        :returns: The values for the given keys.
        :rtype: ``generator``

        Example:

        .. code-block:: pycon

            >>> db.update(k1='v1', k2='v2', k3='v3', k4='v4')
            >>> [val for val in db.mget('k1', 'k3', 'missing', 'k4')]
            ['v1', 'v3', None, 'v4']

    .. py:method:: mset(**kwargs)

        Set multiple key/value pairs in a single command. This is equivalent to
        the :py:meth:`~Vedis.update` method.

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

    .. py:method:: msetnx(**kwargs)

        Similar to :py:meth:`~Vedis.update`, except that existing keys will not be overwritten.

        :returns: ``True`` on success.

        Example:

        .. code-block:: pycon

            >>> db.msetnx(k1='v1', k2='v2')
            >>> list(db.mget('k1', 'k2'))
            ['v1', 'v2']

            >>> db.msetnx(k1='v1x', k2='v2x', k3='v3x')
            >>> list(db.mget('k1', 'k2', 'k3'))
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

        :returns: A generator that successively yields sub-strings.

        Example:

        .. code-block:: pycon

            >>> list(db.str_split('abcdefghijklmnop', 5))
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
