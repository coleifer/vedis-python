.. vedis-python documentation master file, created by
   sphinx-quickstart on Mon Jun 16 23:34:38 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

vedis-python
============

.. image:: http://media.charlesleifer.com/blog/photos/vedis-python-logo.png

Fast Python bindings for `Vedis <http://vedis.symisc.net/>`_, an embedded, NoSQL key/value and data-structure store modeled after `Redis <http://redis.io>`_.

The source code for vedis-python is `hosted on GitHub <https://github.com/coleifer/vedis-python>`_.

Vedis features:

* Embedded, zero-conf database
* Transactional (ACID)
* Single file or in-memory database
* Key/value store
* `Over 70 commands <http://vedis.symisc.net/commands.html>`_ similar to standard `Redis <http://redis.io>`_ commands.
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

The previous version (0.2.0) of ``vedis-python`` utilized ``ctypes`` to wrap the Vedis C library. By switching to Cython, key/value and Vedis command operations are significantly faster.

.. note::
  If you encounter any bugs in the library, please `open an issue <https://github.com/coleifer/vedis-python/issues/new>`_, including a description of the bug and any related traceback.

.. note::
  If you like Vedis you might also want to check out `UnQLite <http://unqlite.org>`_, an embedded key/value database and JSON document store (python bindings: `unqlite-python <https://unqlite-python.readthedocs.io>`_.

Contents:

.. toctree::
   :maxdepth: 2
   :glob:

   installation
   quickstart
   api
   custom_commands


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

