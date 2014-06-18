from contextlib import contextmanager
from functools import wraps

from vedis._vedis import *
from vedis._vedis import _libs as _c_libraries


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
        }.get(rc, 'Unknown exception: %s' % rc))

def _convert_value(value):
    # Vedis supports dynamic typing, so we need to check the type of the
    # vedis value and the convert it.
    if vedis_value_is_string(value):
        nbytes = c_int()
        res = vedis_value_to_string(value, pointer(nbytes))
        return res.raw[:nbytes.value].replace('\\"', '"')
    elif vedis_value_is_array(value):
        accum = []
        while True:
            item = vedis_array_next_elem(value)
            if not item:
                break
            accum.append(_convert_value(item))
        return accum
    elif vedis_value_is_bool(value):
        return bool(vedis_value_to_bool(value))
    elif vedis_value_is_null(value):
        return None
    elif vedis_value_is_int(value):
        return vedis_value_to_int(value)
    else:
        raise TypeError('Unknown type encountered')

def _push_result(context, result):
    if isinstance(result, basestring):
        return vedis_result_string(context, result, -1)
    elif isinstance(result, (int, long)):
        return vedis_result_int(context, result)
    elif isinstance(result, bool):
        return vedis_result_bool(context, result)
    elif isinstance(result, float):
        return vedis_result_double(context, result)
    return vedis_result_null(context)

_command_callback = CFUNCTYPE(
    UNCHECKED(c_int),
    POINTER(vedis_context),
    c_int,
    POINTER(POINTER(vedis_value)))

_vedis_lib = _c_libraries['vedis']

def wrap_command(fn):
    def inner(vedis_context, nargs, values):
        converted_args = [_convert_value(values[i]) for i in range(nargs)]
        try:
            ret = fn(vedis_context, *converted_args)
        except:
            return VEDIS_UNKNOWN
        else:
            _push_result(vedis_context, ret)
            return VEDIS_OK
    return _command_callback(inner), inner

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

    def execute(self, cmd, params=None, nlen=-1, result=False,
                iter_result=False):
        """Execute a Vedis command, optionally returning a result."""
        if params is not None:
            params = map(self.escape, params)
            cmd = cmd % tuple(params)

        handle_return_value(vedis_exec(self._vedis, cmd, nlen))
        if result:
            return self.get_result()
        elif iter_result:
            return self.iter_result()

    def get_result(self):
        """Retrieve the result of the last executed Vedis command."""
        value = POINTER(vedis_value)()
        vedis_exec_result(self._vedis, byref(value))
        return _convert_value(value)

    def iter_result(self):
        """Iterate over a result set."""
        value = POINTER(vedis_value)()
        vedis_exec_result(self._vedis, byref(value))
        if not vedis_value_is_array(value):
            if vedis_value_is_null(value):
                return None
            raise TypeError('Value is not an array.')
        return self.iter_vedis_array(value)

    def iter_vedis_array(self, value):
        while True:
            item = vedis_array_next_elem(value)
            if item:
                yield _convert_value(item)
            else:
                raise StopIteration

    # Key/Value APIs.
    def store(self, key, value):
        """Store a value in the given key."""
        key, value = str(key), str(value)
        handle_return_value(vedis_kv_store(
            self._vedis,
            key,
            len(key),
            value,
            len(value)))

    def fetch(self, key, buf_size=4096):
        """Retrieve a value in the given key."""
        key = str(key)
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
        key, value = str(key), str(value)
        handle_return_value(vedis_kv_append(
            self._vedis,
            key,
            len(key),
            value,
            len(value)))

    def exists(self, key):
        nbytes = vedis_int64(0)
        key = str(key)
        res = vedis_kv_fetch(self._vedis, key, len(key), None, byref(nbytes))
        return res == VEDIS_OK

    def delete(self, key):
        key = str(key)
        handle_return_value(vedis_kv_delete(self._vedis, key, len(key)))

    def random_string(self, nbytes):
        buf = create_string_buffer(nbytes)
        handle_return_value(vedis_util_random_string(
            self._vedis,
            addressof(buf),
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

    def _flatten_list(self, args):
        return ' '.join(map(self.escape, args))

    def _flatten(self, kwargs):
        return ' '.join(
            '%s %s' % (self.escape(key), self.escape(value))
            for key, value in kwargs.items())

    def escape(self, s):
        return '"%s"' % str(s).replace('"', '\\"')

    # Vedis key/value/string commands.
    def strlen(self, key):
        return self.execute('STRLEN %s', (key,), result=True)

    def copy(self, src, dest):
        return self.execute('COPY %s %s', (src, dest), result=True)

    def move(self, src, dest):
        return self.execute('MOVE %s %s', (src, dest), result=True)

    def mget(self, *keys):
        return self.execute(
            'MGET %s' % self._flatten_list(keys),
            iter_result=True)

    def setnx(self, key, value):
        return self.execute('SETNX %s %s', (key, value), result=True)

    def mset(self, **kwargs):
        return self.execute('MSET %s' % self._flatten(kwargs), result=True)

    def msetnx(self, **kwargs):
        return self.execute('MSETNX %s' % self._flatten(kwargs), result=True)

    def get_set(self, key, value):
        return self.execute('GETSET %s %s', (key, value), result=True)

    def incr(self, key):
        return self.execute('INCR %s', (key,), result=True)

    def decr(self, key):
        return self.execute('DECR %s', (key,), result=True)

    def incr_by(self, key, amt):
        return self.execute('INCRBY %s %s', (key, amt), result=True)

    def decr_by(self, key, amt):
        return self.execute('DECRBY %s %s', (key, amt), result=True)

    def csv(self, csv_data, delim=None, enclosure=None, escape=None):
        args = [csv_data]
        if delim or (enclosure or escape):
            args.append(delim or ',')
        if enclosure or escape:
            args.append(enclosure or '"')
        if escape:
            args.append(escape)
        param_str = ' '.join(['%s'] * len(args))
        return self.execute('GETCSV %s' % param_str, args, iter_result=True)

    def strip_tags(self, html):
        return self.execute('STRIP_TAG %s', (html,), result=True)

    def str_split(self, s, nchars=1):
        return self.execute('STR_SPLIT %s %s', (s, nchars), iter_result=True)

    def size_format(self, nbytes):
        return self.execute('SIZE_FMT %s', (nbytes,), result=True)

    def soundex(self, s):
        return self.execute('SOUNDEX %s', (s,), result=True)

    def base64(self, data):
        return self.execute('BASE64 %s', (data,), result=True)

    def base64_decode(self, data):
        return self.execute('BASE64_DEC %s', (data,), result=True)

    # Vedis Hash commands.
    def Hash(self, key):
        return Hash(self, key)

    def hset(self, hash_key, key, value):
        self.execute('HSET %s %s %s', (hash_key, key, value))

    def hget(self, hash_key, key):
        return self.execute('HGET %s %s', (hash_key, key), result=True)

    def hdel(self, hash_key, key):
        self.execute('HDEL %s %s', (hash_key, key))

    def hkeys(self, hash_key):
        return self.execute('HKEYS %s', (hash_key,), iter_result=True)

    def hvals(self, hash_key):
        return self.execute('HVALS %s', (hash_key,), iter_result=True)

    def hgetall(self, hash_key):
        result = self.execute('HGETALL %s', (hash_key,), result=True)
        if result is not None:
            return dict(zip(result[::2], result[1::2]))

    def hitems(self, hash_key):
        result = self.execute('HGETALL %s', (hash_key,), result=True)
        if result is not None:
            return zip(result[::2], result[1::2])

    def hlen(self, hash_key):
        return self.execute('HLEN %s', (hash_key,), result=True)

    def hexists(self, hash_key, key):
        return self.execute('HEXISTS %s %s', (hash_key, key), result=True)

    def hmset(self, hash_key, **kwargs):
        self.execute('HMSET %%s %s' % self._flatten(kwargs), (hash_key,))

    def hmget(self, hash_key, *keys):
        return self.execute(
            'HMGET %%s %s' % self._flatten_list(keys),
            (hash_key,),
            iter_result=True)

    def hsetnx(self, hash_key, key, value):
        return self.execute(
            'HSETNX %s %s %s',
            (hash_key, key, value),
            result=True)

    # Vedis set commands.
    def Set(self, name):
        return Set(self, name)

    def sadd(self, key, *values):
        return self.execute(
            'SADD %%s %s' % self._flatten_list(values),
            (key,),
            result=True)

    def scard(self, key):
        return self.execute('SCARD %s', (key,), result=True)

    def sismember(self, key, value):
        return self.execute('SISMEMBER %s %s', (key, value), result=True)

    def spop(self, key):
        return self.execute('SPOP %s', (key,), result=True)

    def speek(self, key):
        return self.execute('SPEEK %s', (key,), result=True)

    def stop(self, key):
        return self.execute('STOP %s', (key,), result=True)

    def srem(self, key, *values):
        return self.execute(
            'SREM %%s %s' % self._flatten_list(values),
            (key,),
            result=True)

    def smembers(self, key):
        return self.execute('SMEMBERS %s', (key,), iter_result=True)

    def sdiff(self, k1, k2):
        return self.execute('SDIFF %s %s', (k1, k2), iter_result=True)

    def sinter(self, k1, k2):
        return self.execute('SINTER %s %s', (k1, k2), iter_result=True)

    def slen(self, key):
        return self.execute('SLEN %s', (key,), result=True)

    # Vedis list commands.
    def List(self, name):
        return List(self, name)

    def lindex(self, key, idx):
        return self.execute('LINDEX %s %s', (key, idx), result=True)

    def llen(self, key):
        return self.execute('LLEN %s', (key,), result=True)

    def lpop(self, key):
        return self.execute('LPOP %s', (key,), result=True)

    def lpushx(self, key, *vals):
        return self.execute(
            'LPUSHX %%s %s' % self._flatten_list(vals),
            (key,),
            result=True)

    def lpush(self, key, *vals):
        return self.execute(
            'LPUSH %%s %s' % self._flatten_list(vals),
            (key,),
            result=True)

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
        return self.execute('BEGIN', result=True)

    def commit(self):
        return self.execute('COMMIT', result=True)

    def rollback(self):
        return self.execute('ROLLBACK', result=True)

    def commit_on_success(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with self.transaction():
                return fn(*args, **kwargs)
        return wrapper

    def register(self, command_name, user_data=None):
        def _decorator(fn):
            c_callback, inner = wrap_command(fn)
            vedis_register_command(
                self._vedis,
                command_name,
                c_callback,
                user_data or '')
            return inner
        return _decorator

    def delete_command(self, command_name):
        handle_return_value(vedis_delete_command(self._vedis, command_name))


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


class VedisObject(object):
    def __init__(self, vedis, key):
        self._vedis = vedis
        self._key = key


class Hash(VedisObject):
    def get(self, key):
        return self._vedis.hget(self._key, key)

    def set(self, key, value):
        return self._vedis.hset(self._key, key, value)

    def delete(self, key):
        return self._vedis.hdel(self._key, key)

    def keys(self):
        return self._vedis.hkeys(self._key)

    def values(self):
        return self._vedis.hvals(self._key)

    def items(self):
        return self._vedis.hitems(self._key)

    def update(self, **kwargs):
        return self._vedis.hmset(self._key, **kwargs)

    def to_dict(self):
        return self._vedis.hgetall(self._key)

    def __len__(self):
        return self._vedis.hlen(self._key)

    def __contains__(self, key):
        return self._vedis.hexists(self._key, key)

    def __setitem__(self, key, value):
        return self.set(key, value)

    def __getitem__(self, key):
        return self.get(key)

    def __delitem__(self, key):
        return self.delete(key)

    def __iter__(self):
        return iter(self.keys())

    def __repr__(self):
        return '<Hash: %s>' % self.to_dict()

class Set(VedisObject):
    def add(self, *values):
        return self._vedis.sadd(self._key, *values)

    def __len__(self):
        return self._vedis.scard(self._key)

    def __contains__(self, value):
        return self._vedis.sismember(self._key, value)

    def pop(self):
        return self._vedis.spop(self._key)

    def peek(self):
        return self._vedis.speek(self._key)

    def top(self):
        return self._vedis.stop(self._key)

    def remove(self, *values):
        return self._vedis.srem(self._key, *values)

    def __iter__(self):
        return iter(self._vedis.smembers(self._key))

    def to_set(self):
        return set(item for item in self)

    def __sub__(self, rhs):
        return set(self._vedis.sdiff(self._key, rhs._key))

    def __and__(self, rhs):
        return set(self._vedis.sinter(self._key, rhs._key))

class List(VedisObject):
    def __getitem__(self, index):
        return self._vedis.lindex(self._key, index)

    def __len__(self):
        return self._vedis.llen(self._key)

    def pop(self):
        return self._vedis.lpop(self._key)

    def append(self, *values):
        return self._vedis.lpush(self._key, *values)
