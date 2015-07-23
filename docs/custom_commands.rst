.. custom_commands:

Creating Your Own Commands
==========================

It is possible to create your own Vedis commands and execute them like any other. Use the :py:meth:`Vedis.register` method to decorate the function you wish to turn into a Vedis command. Your command callback must accept at least one argument, the :py:class:`VedisContext` (which wraps `vedis context <http://vedis.symisc.net/c_api_object.html#vedis_context>`_). Any arguments supplied by the caller will also be passed to your callback. Using the :py:class:`VedisContext` object, your function can perform key/value operations on the database.

Here is a small example:

.. code-block:: python

    db = Vedis()

    @db.register('CONCAT')
    def concat(context, glue, *params):
        return glue.join(params)

    @db.register('TITLE')
    def title(context, *params):
        return [param.title() for param in params]

    @db.register('HASH_VALUES')
    def hash_values(context, *values):
        # Calculate a hash for each value and store it in a
        # key.
        for value in values:
            context[value] = hashlib.sha1(value).hexdigest()
        return len(values)

Usage:

.. code-block:: pycon

    >>> print db.execute('CONCAT | foo bar baz')
    foo|bar|baz

    >>> print db.execute('TITLE "testing" "this is a test" "another"')
    ['Testing', 'This Is A Test', 'Another']

    >>> print db.execute('HASH_VALUES shh secret')
    2
    >>> db.mget(['shh', 'secret'])
    ['0c731a5f1dc781894b434c27b9f6a9cd9d9bdfcb',
     'e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4']

You can also directly call the function with your arguments, and the call will automatically be routed through Vedis:

.. code-block:: pycon

    >>> print title('testing', 'this is a test', 'another')
    ['Testing', 'This Is A Test', 'Another']

    >>> print concat('#', 'foo', '1', 'hello')
    'foo#1#hello'

Valid return types for user-defined commands
--------------------------------------------

* ``list`` or ``tuple`` (containing arbitrary levels of nesting).
* ``str``
* ``int`` and ``long``
* ``float``
* ``bool``
* ``None``

Operations supported by VedisContext
------------------------------------

The first parameter of your custom command is always a :py:class:`VedisContext` instance. This object can be used to access the key/value features of the database. It supports the following APIs:

* Getting, setting and deleting items using ``dict`` APIs.
* Checking whether a key exists using ``in``.
* Appending to an existing key.

Example:

.. code-block:: python

    @db.register('STORE_DATA')
    def store_data(context):
        context['foo'] = 'bar'
        assert context['foo'] == 'bar'
        del context['other key']
        assert 'foo' in context
        context.append('foo', 'more data')
