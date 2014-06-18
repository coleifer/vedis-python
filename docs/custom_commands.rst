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

    print db.execute('CONCAT | foo bar baz', result=True)  # foo|bar|baz

At the moment only scalar return types (or ``None``) are supported, though I intend on adding support for returning lists as well.
