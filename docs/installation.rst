.. _installation:

Installation
============

You can use ``pip`` to install ``vedis-python``:

.. code-block:: console

    pip install cython vedis

The project is hosted at https://github.com/coleifer/vedis-python and can be installed from source:

.. code-block:: console

    git clone https://github.com/coleifer/vedis-python
    cd vedis-python
    python setup.py build
    python setup.py install

.. note::
    ``vedis-python`` depends on Cython to generate the Python extension. By default vedis-python no longer ships with a generated C source file, so it is necessary to install Cython in order to compile ``vedis-python``.

After installing vedis-python, you can run the unit tests by executing the ``tests`` module:

.. code-block:: console

    python tests.py
