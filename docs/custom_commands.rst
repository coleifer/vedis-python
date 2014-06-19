.. custom_commands:

Creating Your Own Commands
==========================

It is possible to create your own Vedis commands and execute them like any other. Use the :py:meth:`Vedis.register` method to decorate the function you wish to turn into a Vedis command. Your command callback must accept at least one argument, a `vedis context <http://vedis.symisc.net/c_api_object.html#vedis_context>`_. Any arguments supplied by the caller will also be passed to your callback.

Here is a small example:

.. code-block:: python

    db = Vedis()

    @db.register('CONCAT')
    def concat(context, glue, *params):
        return glue.join(params)

    @db.register('TITLE')
    def title(context, *params):
        return [param.title() for param in params]

Usage:

.. code-block:: pycon

    >>> print db.execute('CONCAT | foo bar baz', result=True)
    foo|bar|baz

    >>> print db.execute('TITLE "testing" "this is a test" "another"', result=True)
    ['Testing', 'This Is A Test', 'Another']

You can also use the short-hand:

.. code-block:: pycon

    >>> print db.TITLE('testing', 'this is a test', 'another')
    ['Testing', 'This Is A Test', 'Another']


Valid return types for user-defined commands
--------------------------------------------

* ``list`` or ``tuple`` (containing arbitrary levels of nesting).
* ``str``
* ``int`` and ``long``
* ``float``
* ``bool``
* ``None``
