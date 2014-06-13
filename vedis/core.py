from contextlib import contextmanager

from vedis._vedis import *


def handle_return_value(rc):
    if rc != VEDIS_OK:
        raise Exception({
            SXERR_NOTFOUND: 'Value not found.',
            VEDIS_ABORT: 'Executed command request an operation abort',
            VEDIS_NOMEM: 'Out of memory',
            VEDIS_UNKNOWN: 'Unknown command',
            VEDIS_IOERR: 'OS error',
            VEDIS_ABORT: 'Another thread released the database handle',
            VEDIS_BUSY: 'Database is locked by another thread/process',
            VEDIS_READ_ONLY: 'Database is in read-only mode',
        }.get(rc, 'Unknown exception'))


class Vedis(object):
    """
    Vedis database python bindings.
    """
    def __init__(self, database=':mem:'):
        self._vedis = POINTER(vedis)()
        rc = vedis_open(byref(self._vedis), database)
        if rc != VEDIS_OK:
            raise Exception('Unable to open Vedis database')

    def close(self):
        """Close the database."""
        handle_return_value(vedis_close(self._vedis))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()
        return False

    def execute(self, cmd, nlen=-1, result=False, iter_result=False):
        """Execute a Vedis command, optionally returning a result."""
        handle_return_value(vedis_exec(self._vedis, cmd, nlen))
        if result:
            return self.get_result()
        elif iter_result:
            return self.iter_result()

    def _convert_value(self, value):
        # Vedis supports dynamic typing, so we need to check the type of the
        # vedis value and the convert it.
        if vedis_value_is_string(value):
            nbytes = c_int()
            res = vedis_value_to_string(value, pointer(nbytes))
            return res.raw[:nbytes.value]
        elif vedis_value_is_array(value):
            accum = []
            while True:
                item = vedis_array_next_elem(value)
                if not item:
                    break
                accum.append(self._convert_value(item))
            return accum
        elif vedis_value_is_bool(value):
            return bool(vedis_value_to_bool(value))
        elif vedis_value_is_null(value):
            return None
        elif vedis_value_is_int(value):
            return vedis_value_to_int(value)
        else:
            raise TypeError('Unknown type encountered')

    def get_result(self):
        """Retrieve the result of the last executed Vedis command."""
        value = POINTER(vedis_value)()
        vedis_exec_result(self._vedis, byref(value))
        return self._convert_value(value)

    def iter_result(self):
        """Iterate over a result set."""
        value = POINTER(vedis_value)()
        vedis_exec_result(self._vedis, byref(value))
        if not vedis_value_is_array(value):
            raise TypeError('Value is not an array.')
        while True:
            item = vedis_array_next_elem(value)
            if item:
                yield self._convert_value(item)
            else:
                raise StopIteration

    def store(self, key, value):
        """Store a value in the given key."""
        handle_return_value(vedis_kv_store(
            self._vedis,
            key,
            len(key),
            value,
            len(value)))

    def fetch(self, key, buf_size=4096):
        """Retrieve a value in the given key."""
        buf = create_string_buffer(buf_size)
        nbytes = vedis_int64(buf_size)
        rc = vedis_kv_fetch(
            self._vedis,
            key,
            len(key),
            byref(buf),
            byref(nbytes))
        if rc == VEDIS_OK:
            return buf.raw[:nbytes.value]
        elif rc == SXERR_NOTFOUND:
            raise KeyError(key)
        handle_return_value(rc)

    def append(self, key, value):
        handle_return_value(vedis_kv_append(
            self._vedis,
            key,
            len(key),
            value,
            len(value)))

    def exists(self, key):
        nbytes = vedis_int64(0)
        res = vedis_kv_fetch(self._vedis, key, len(key), None, byref(nbytes))
        return res == VEDIS_OK

    def delete(self, key):
        handle_return_value(self._vedis, key, len(key))

    def random_string(self, nbytes):
        buf = create_string_buffer(nbytes)
        handle_return_value(vedis_util_random_string(
            self._vedis,
            byref(buf),
            nbytes))
        return buf.raw[:nbytes]

    def random_number(self):
        return vedis_util_random_num(self._vedis)

    __setitem__ = store
    __getitem__ = fetch
    __delitem__ = delete
    __contains__ = exists

    def transaction(self):
        return transaction(self)

    @property
    def vedis_version(self):
        return str(vedis_lib_version())

    # Vedis key/value/string commands.
    def strlen(self, key):
        return self.execute('STRLEN %s' % key, result=True)

    def copy(self, src, dest):
        return self.execute('COPY %s %s' % (src, desc), result=True)

    def move(self, src, dest):
        return self.execute('MOVE %s %s' % (src, desc), result=True)

    def mget(self, *keys):
        return self.execute('MGET %s' % (' '.join(keys)), iter_result=True)

    def setnx(self, key, value):
        return self.execute('SETNX %s %s' % (key, value), result=True)

    def _flatten(self, kwargs):
        return ' '.join(
            '%s %s' % (key, value) for key, value in kwargs.items())

    def mset(self, **kwargs):
        return self.execute('MSET %s' % self._flatten(kwargs), result=True)

    def msetnx(self, **kwargs):
        return self.execute('MSETNX %s' % self._flatten(kwargs), result=True)

    def get_set(self, key, value):
        return self.execute('GETSET %s %s' % (key, value), result=True)

    def incr(self, key):
        return self.execute('INCR %s' % key, result=True)

    def decr(self, key):
        return self.execute('DECR %s' % key, result=True)

    def incr_by(self, key, amt):
        return self.execute('INCRBY %s %s' % (key, amt), result=True)

    def decr_by(self, key, amt):
        return self.execute('DECRBY %s %s' % (key, amt), result=True)

    def csv(self, csv_data, delim=None, enclosure=None, escape=None):
        args = [csv_data]
        if delim or (enclosure or escape):
            args.append(delim or ',')
        if enclosure or escape:
            args.append(enclosure or '"')
        if escape:
            args.append(escape)
        return self.execute('GETCSV %s' % (' '.join(args)), iter_result=True)

    def strip_tags(self, html):
        return self.execute('STRIP_TAG %s' % html, result=True)

    def str_split(self, s, nchars=1):
        return self.execute('STR_SPLIT %s %s' % (s, nchars), iter_result=True)

    def size_format(self, nbytes):
        return self.execute('SIZE_FMT %s' % nbytes, result=True)

    def soundex(self, s):
        return self.execute('SOUNDEX %s' % s, result=True)

    def base64(self, data):
        return self.execute('BASE64 %s' % data, result=True)

    def base64_decode(self, data):
        return self.execute('BASE64_DEC %s' % data, result=True)

    # Vedis Hash commands.
    def hset(self, hash_key, key, value):
        self.execute('HSET %s %s %s' % (hash_key, key, value))

    def hget(self, hash_key, key):
        return self.execute('HGET %s %s' % (hash_key, key), result=True)

    def hdel(self, hash_key, key):
        self.execute('HDEL %s %s' % (hash_key, key))

    def hkeys(self, hash_key):
        return self.execute('HKEYS %s' % hash_key, iter_result=True)

    def hvals(self, hash_key):
        return self.execute('HVALS %s' % hash_key, iter_result=True)

    def hgetall(self, hash_key):
        result = self.execute('HGETALL %s' % hash_key, result=True)
        return dict(zip(result[::2], result[1::2]))

    def hlen(self, hash_key):
        return self.execute('HLEN %s' % hash_key, result=True)

    def hexists(self, hash_key, key):
        return self.execute('HEXISTS %s %s' % (hash_key, key), result=True)

    def hmset(self, hash_key, **kwargs):
        self.execute('HMSET %s %s' % (hash_key, self._flatten(kwargs)))

    def hmget(self, hash_key, *keys):
        return self.execute(
            'HMGET %s %s' % (hash_key, ' '.join(keys)),
            iter_result=True)

    def hsetnx(self, hash_key, key, value):
        return self.execute(
            'HSETNX %s %s %s' % (hash_key, key, value),
            result=True)

    # Vedis set commands.
    def sadd(self, key, value):
        return self.execute('SADD %s %s' % (key, value), result=True)

    def scard(self, key):
        return self.execute('SCARD %s' % key, result=True)

    def sismember(self, key, value):
        return self.execute('SISMEMBER %s %s' % (key, value), result=True)

    def spop(self, key):
        return self.execute('SPOP %s' % key, result=True)

    def speek(self, key):
        return self.execute('SPEEK %s' % key, result=True)

    def stop(self, key):
        return self.execute('STOP %s' % key, result=True)

    def srem(self, key, value):
        return self.execute('SREM %s %s' % (key, value), result=True)

    def smembers(self, key):
        return self.execute('SMEMBERS %s' % key, iter_result=True)

    def sdiff(self, k1, k2):
        return self.execute('SDIFF %s %s' % (k1, k2), iter_result=True)

    def sinter(self, k1, k2):
        return self.execute('SINTER %s %s' % (k1, k2), iter_result=True)

    def slen(self, key):
        return self.execute('SLEN %s' % key, result=True)

    # Vedis list commands.
    def lindex(self, key, idx):
        return self.execute('LINDEX %s %s' % (key, idx), result=True)

    def llen(self, key):
        return self.execute('LLEN %s' % key, result=True)

    def lpop(self, key):
        return self.execute('LPOP %s' % key, result=True)

    def lpushx(self, key, *vals):
        values = ' '.join(vals)
        return self.execute('LPUSHX %s %s' % (key, values), result=True)

    def lpush(self, key, *vals):
        values = ' '.join(vals)
        return self.execute('LPUSH %s %s' % (key, values), result=True)

    # Vedis misc commands.
    def rand(self, lower_bound=None, upper_bound=None):
        args = ['RAND']
        if lower_bound or upper_bound:
            args.append(str(lower_bound or 0))
        if upper_bound:
            args.append(str(upper_bound))
        return self.execute(' '.join(args), result=True)

    def time(self):
        return self.execute('TIME', result=True)

    def date(self):
        return self.execute('DATE', result=True)

    def os(self):
        return self.execute('OS', result=True)

    def table_list(self):
        return self.execute('TABLE_LIST', result=True)

    def vedis_info(self):
        return self.execute('VEDIS', result=True)

    def begin(self):
        self.execute('BEGIN')

    def commit(self):
        self.execute('COMMIT')

    def rollback(self):
        self.execute('ROLLBACK')


class transaction(object):
    def __init__(self, vedis):
        self.vedis = vedis

    def __enter__(self):
        self.vedis.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.vedis.rollback()
        else:
            try:
                self.vedis.commit()
            except:
                self.vedis.rollback()
                raise
