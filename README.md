vedis-python
============

Python bindings for the Vedis embedded NoSQL database. Vedis is a fun, fast, embedded database modeled after Redis.

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

    db.hmset('my_hash', foo='bar', baz='nuggets')
    my_hash = d.hgetall('my_hash')
    # my_hash == {'foo': 'bar', 'baz': 'nuggets}

I will have documentation for the available commands and return types available soon!
