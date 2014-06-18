vedis-python
============

Python bindings for the Vedis embedded NoSQL database. Vedis is a fun, fast, embedded database modeled after Redis.

[View the vedis-python documentation](http://vedis-python.readthedocs.org/).

Vedis does lots of little things.

![](http://media.charlesleifer.com/blog/photos/more-hueys.png)

[vedis homepage](http://vedis.symisc.net/) and [license](http://vedis.symisc.net/licensing.html).

Installation
------------

You can install vedis using `pip`.

    pip install vedis

Basic usage
-----------

You can treat Vedis as a key/value store:

    from vedis import Vedis
    db = Vedis('path/to/file.db')
    db['foo'] = 'bar'
    print db['foo']

But Vedis also supports many interesting Redis-type data structures and commands.

    h = db.Hash('my hash')
    h['sub-key'] = 'val'
    h.update(baz='nuggets', huey='kitten')
    my_hash = h.to_dict()
    # my_hash == {'sub-key': 'val', 'baz': 'nuggets', 'huey': 'kitten'}0

Check out the [quick start](http://vedis-python.readthedocs.org/en/latest/quickstart.html) for more examples.
