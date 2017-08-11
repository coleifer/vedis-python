import base64
import csv
import os
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
import unittest

try:
    from vedis import Vedis
except ImportError:
    sys.stderr.write('Unable to import `vedis`. Make sure it is properly '
                     'installed.\n')
    sys.stderr.flush()
    raise


if sys.version_info[0] == 3:
    basestring = str
    long = int


class BaseVedisTestCase(unittest.TestCase):
    def setUp(self):
        super(BaseVedisTestCase, self).setUp()
        self.db = Vedis(':memory:')

    def tearDown(self):
        self.db.close()
        super(BaseVedisTestCase, self).tearDown()

    def set_k1_k2(self):
        # Short-hand for setting two keys.
        self.db['k1'] = 'v1'
        self.db['k2'] = 'v2'


class TestKeyValueAPI(BaseVedisTestCase):
    def test_kv_api(self):
        self.db.store('k1', 'v1')
        self.db.store('k2', 'v2')
        self.assertEqual(self.db.fetch('k1'), 'v1')
        self.assertEqual(self.db.fetch('k2'), 'v2')
        self.assertRaises(KeyError, self.db.fetch, 'k3')

        self.db.append('k1', 'V1')
        self.assertEqual(self.db.fetch('k1'), 'v1V1')

        self.db.append('k3', 'v3')
        self.assertEqual(self.db.fetch('k3'), 'v3')

        self.assertTrue(self.db.exists('k1'))
        self.db.delete('k1')
        self.assertFalse(self.db.exists('k1'))

        self.assertRaises(KeyError, lambda: self.db.delete('kx'))

        self.db['k3'] = ''
        self.assertTrue(self.db.exists('k3'))

    def test_dict_api(self):
        self.db['k1'] = 'v1'
        self.db['k2'] = 'v2'
        self.assertEqual(self.db['k1'], 'v1')
        self.assertEqual(self.db['k2'], 'v2')
        self.assertRaises(KeyError, lambda: self.db['k3'])

        self.db.update({'k3': 'v3', 'k2': ''})
        self.assertEqual(self.db['k3'], 'v3')
        self.assertEqual(self.db['k2'], '')

        self.assertTrue('k1' in self.db)
        self.assertTrue('k3' in self.db)
        self.assertFalse('k4' in self.db)

        del self.db['k3']
        self.assertFalse('k3' in self.db)
        self.assertRaises(KeyError, lambda: self.db['k3'])

    def test_storing_ints(self):
        self.db['k1'] = 1
        self.db['k2'] = 1234567890
        self.assertEqual(self.db['k1'], '1')
        self.assertEqual(self.db['k2'], '1234567890')


class TestBasicCommands(BaseVedisTestCase):
    def test_get_set(self):
        # XXX: These actually use the key/value API for performance.
        self.db.set('k1', 'v1')
        self.db.set('k2', 'v2')
        self.assertEqual(self.db.get('k1'), 'v1')
        self.assertEqual(self.db.get('k2'), 'v2')
        self.assertRaises(KeyError, lambda: self.db['k3'])

    def test_exists_and_object_types(self):
        # For some reason, `EXIST` does not work with object types.
        self.db.hset('my_hash', 'k1', 'v1')
        self.db.sadd('my_set', 'v1')
        self.db.lpush('my_list', 'i1')

        self.assertFalse(self.db.exists('my_hash'))
        self.assertFalse(self.db.exists('my_set'))
        self.assertFalse(self.db.exists('my_list'))

    def test_mget(self):
        self.set_k1_k2()
        res = self.db.mget(['k1', 'missing', 'k2'])
        self.assertEqual(res, ['v1', None, 'v2'])

    def test_setnx(self):
        self.db['k1'] = 'v1'
        self.db.setnx('k1', 'v-x')
        self.assertEqual(self.db['k1'], 'v1')

        self.db.setnx('k2', 'v-x')
        self.assertEqual(self.db['k2'], 'v-x')

    def test_mset(self):
        self.db['k1'] = 'v1'
        self.db.mset(dict(k1='v-x', k2='v2', foo='bar'))
        self.assertEqual(
            self.db.mget(['k1', 'k2', 'foo']),
            ['v-x', 'v2', 'bar'])

        self.db.mset({'k s': 'vs', 'k s2': 'vs2'})
        self.assertEqual(
            self.db.mget(['k s', 'k s2']),
            ['vs', 'vs2'])

    def test_msetnx(self):
        self.db['k1'] = 'v1'
        self.db.msetnx(dict(k1='v-x', k2='v2', foo='bar'))
        self.assertEqual(
            self.db.mget(['k1', 'k2', 'foo']),
            ['v1', 'v2', 'bar'])

    def test_getset(self):
        res = self.db.get_set('k1', 'v1')
        self.assertIsNone(res)

        res = self.db.get_set('k1', 'v-x')
        self.assertEqual(res, 'v1')
        self.assertEqual(self.db['k1'], 'v-x')

    def test_incr(self):
        res = self.db.incr('counter')
        self.assertEqual(res, 1)

        res = self.db.incr('counter')
        self.assertEqual(res, 2)

    def test_decr(self):
        res = self.db.decr('counter')
        self.assertEqual(res, -1)

        res = self.db.decr('counter')
        self.assertEqual(res, -2)

    def test_incr_by_decr_by(self):
        res = self.db.incr_by('c', 100)
        self.assertEqual(res, 100)

        res = self.db.incr_by('c', 10)
        self.assertEqual(res, 110)

        res = self.db.decr_by('c', 90)
        self.assertEqual(res, 20)

    def test_quoted_values(self):
        self.db['k"1"'] = 'value "with quotes"'
        res = self.db['k"1"']
        self.assertEqual(res, 'value "with quotes"')

    def test_numbers(self):
        self.db['1'] = '2'
        self.assertEqual(self.db['1'], '2')
        self.db.append('1', '3')
        self.assertEqual(self.db['1'], '23')
        self.assertTrue(self.db.exists('1'))
        self.assertFalse(self.db.exists('2'))


class TestStringCommands(BaseVedisTestCase):
    def test_strlen(self):
        self.db['k1'] = 'foo'
        self.db['k2'] = ''
        self.assertEqual(self.db.strlen('k1'), 3)
        self.assertEqual(self.db.strlen('k2'), 0)
        self.assertEqual(self.db.strlen('missing'), 0)

    def test_copy(self):
        self.db['k1'] = 'v1'
        self.db.copy('k1', 'k2')
        self.assertEqual(self.db['k2'], 'v1')
        self.assertEqual(self.db['k1'], self.db['k2'])

    def test_move(self):
        self.db['k1'] = 'v1'
        self.db.move('k1', 'k2')
        self.assertEqual(self.db['k2'], 'v1')
        self.assertFalse(self.db.exists('k1'))

    def test_random_string(self):
        rs = self.db.random_string(5)
        self.assertEqual(len(rs), 5)
        self.assertTrue(isinstance(rs, bytes))

        rs2 = self.db.randstr(5)
        self.assertEqual(len(rs2), 5)

    def test_random_int(self):
        rn = self.db.random_int()
        self.assertTrue(isinstance(rn, int))

        rn2 = self.db.rand(1, 10)
        self.assertTrue(isinstance(rn, int))

    def test_strip_tags(self):
        data = '<p>This <span>is</span> a test.</p>'
        res = self.db.strip_tags(data)
        self.assertEqual(res, 'This is a test.')

    def test_str_split(self):
        res = self.db.str_split('abcdefghijklmnopqrstuvwxyz', 5)
        self.assertEqual(list(res), [
            'abcde',
            'fghij',
            'klmno',
            'pqrst',
            'uvwxy',
            'z',
        ])

    def test_size_format(self):
        res = self.db.size_format(100000)
        self.assertEqual(res, '97.6 KB')

    def test_base64(self):
        data = 'huey and mickey'
        encoded = self.db.base64(data)
        decoded = self.db.base64_decode(encoded)
        self.assertEqual(decoded, data)


class TestHashCommands(BaseVedisTestCase):
    def test_getsetdel(self):
        self.db.hset('hash', 'k1', 'v1')
        self.db.hset('hash', 'k2', 'v2')
        self.assertEqual(self.db.hget('hash', 'k1'), 'v1')
        self.assertIsNone(self.db.hget('hash', 'missing'))
        self.db.hdel('hash', 'k1')
        self.assertIsNone(self.db.hget('hash', 'k1'))

    def test_keys_vals(self):
        self.db.hset('hash', 'k1', 'v1')
        self.db.hset('hash', 'k2', 'v2')
        self.assertEqual(sorted(self.db.hkeys('hash')), ['k1', 'k2'])
        self.assertEqual(sorted(self.db.hvals('hash')), ['v1', 'v2'])
        self.assertEqual(self.db.hkeys('missing'), None)
        self.assertEqual(self.db.hvals('missing'), None)

    def test_hash_methods(self):
        self.db.hmset('hash', dict(k1='v1', k2='v2', k3='v3'))
        self.assertEqual(self.db.hgetall('hash'), {
            'k1': 'v1',
            'k2': 'v2',
            'k3': 'v3'})
        self.assertEqual(sorted(self.db.hitems('hash')), [
            ('k1', 'v1'),
            ('k2', 'v2'),
            ('k3', 'v3'),
        ])

        self.assertEqual(
            self.db.hmget('hash', ['k1', 'missing', 'k2']),
            ['v1', None, 'v2'])

        self.assertEqual(self.db.hlen('hash'), 3)
        self.assertTrue(self.db.hexists('hash', 'k1'))
        self.assertFalse(self.db.hexists('hash', 'missing'))

        self.db.hsetnx('hash', 'k1', 'v-x')
        self.db.hsetnx('hash', 'k4', 'v-x')
        self.assertEqual(self.db.hgetall('hash'), {
            'k1': 'v1',
            'k2': 'v2',
            'k3': 'v3',
            'k4': 'v-x'})

    def test_hash_methods_missing(self):
        self.assertEqual(self.db.hgetall('missing'), {})
        self.assertEqual(self.db.hlen('missing'), 0)
        self.assertEqual(self.db.hmget('missing', ['x']), None)
        self.assertFalse(self.db.hexists('missing', 'x'))

    def test_quoting(self):
        in_data = {
            'k "1"': 'v "1"',
            'k "2"': 'v "2"',
        }
        self.db.hmset('hash', in_data)
        out_data = self.db.hgetall('hash')
        self.assertEqual(in_data, out_data)


class TestSetCommands(BaseVedisTestCase):
    def test_set_methods(self):
        vals = set(['v1', 'v2', 'v3', 'v4'])
        for val in vals:
            self.db.sadd('set', val)

        self.assertEqual(self.db.scard('set'), 4)
        self.assertTrue(self.db.sismember('set', 'v1'))
        self.assertFalse(self.db.sismember('set', 'missing'))

        #self.assertEqual(self.db.speek('set'), 'v4')
        self.assertTrue(self.db.spop('set') in vals)

        #self.assertEqual(self.db.stop('set'), 'v1')
        self.assertEqual(self.db.slen('set'), 3)

        self.assertTrue(self.db.srem('set', 'v2'))
        self.assertEqual(self.db.slen('set'), 2)
        self.assertFalse(self.db.srem('set', 'missing'))

    def test_multi_add_remove(self):
        res = self.db.smadd('my_set', ['v1', 'v2', 'v3', 'v4', 'v1', 'v2'])
        self.assertEqual(res, 6)
        self.assertEqual(self.db.scard('my_set'), 4)
        self.assertEqual(sorted(list(self.db.smembers('my_set'))),
                         ['v1', 'v2', 'v3', 'v4'])

        res = self.db.smrem('my_set', ['v1', 'v3', 'v1', 'v1'])
        self.assertEqual(res, 2)
        self.assertEqual(sorted(list(self.db.smembers('my_set'))),
                         ['v2', 'v4'])

    def test_intersection_difference(self):
        self.db.smadd('s1', ['v1', 'v2', 'v3'])
        self.db.smadd('s2', ['v2', 'v3', 'v4'])

        self.assertEqual(
            set(self.db.sinter('s1', 's2')),
            set(['v2', 'v3']))

        self.assertEqual(set(self.db.sdiff('s1', 's2')), set(['v1']))
        self.assertEqual(set(self.db.sdiff('s2', 's1')), set(['v4']))


class TestListCommands(BaseVedisTestCase):
    def test_list_methods(self):
        self.db.lmpush('list', ['v1', 'v2', 'v3'])
        self.assertEqual(self.db.llen('list'), 3)
        self.assertEqual(self.db.lpop('list'), 'v1')
        self.assertEqual(self.db.lindex('list', 1), 'v2')
        self.assertEqual(self.db.lindex('list', 2), 'v3')
        self.assertEqual(self.db.lindex('list', 3), None)


class TestMiscCommands(BaseVedisTestCase):
    def test_rand(self):
        res = self.db.rand(1, 10)
        self.assertTrue(1 <= res <= 10)

    def test_time(self):
        res = self.db.time()
        self.assertTrue(re.match('\d{2}:\d{2}', res))

    def test_date(self):
        res = self.db.date()
        self.assertTrue(re.match('\d{4}-\d{2}-\d{2}', res))

    def test_table_list(self):
        self.db['k1'] = 'v1'
        self.db['k2'] = 'v2'
        self.db.hset('hash', 'k1', 'v2')
        self.db.sadd('set', 'v1')
        tables = self.db.table_list()
        self.assertEqual(sorted(tables), ['hash', 'set'])


class TestTransaction(BaseVedisTestCase):
    def setUp(self):
        self.db = Vedis('test.db')

    def tearDown(self):
        try:
            self.db.close()
        finally:
            if os.path.exists('test.db'):
                os.unlink('test.db')

    def test_transaction(self):
        self.db['k1'] = 'v1'

        @self.db.commit_on_success
        def succeed():
            self.db['k2'] = 'v2'

        @self.db.commit_on_success
        def fail():
            self.db['k3'] = 'v3'
            raise Exception('uh-oh')

        succeed()
        self.assertEqual(self.db['k2'], 'v2')

        self.assertRaises(Exception, fail)
        self.assertFalse(self.db.exists('k3'))

    def test_base_transaction_methods(self):
        self.db.begin()
        self.db['k1'] = 'v1'
        self.db.rollback()
        self.assertFalse(self.db.exists('k1'))


class TestHashObject(BaseVedisTestCase):
    def test_hash_object(self):
        h = self.db.Hash('my_hash')
        h['k1'] = 'v1'
        h['k2'] = 'v2'
        self.assertEqual(len(h), 2)
        self.assertEqual(sorted(h.keys()), ['k1', 'k2'])
        self.assertEqual(sorted(h.values()), ['v1', 'v2'])
        self.assertEqual(sorted(h.items()), [
            ('k1', 'v1'),
            ('k2', 'v2'),
        ])
        self.assertEqual(sorted(k for k in h), ['k1', 'k2'])
        del h['k1']
        self.assertFalse('k1' in h)

        h.update(k3='v3', k4='v4')
        self.assertEqual(h.to_dict(), {
            'k2': 'v2',
            'k3': 'v3',
            'k4': 'v4',
        })

        data = h.mget('k3', 'kx', 'k2')
        self.assertEqual(list(data), ['v3', None, 'v2'])


class TestSetObject(BaseVedisTestCase):
    def test_set_object(self):
        s = self.db.Set('my_set')
        s.add('v1', 'v2', 'v1')
        s.add('v2')
        self.assertEqual(len(s), 2)
        self.assertEqual(sorted([i for i in s]), ['v1', 'v2'])

        self.assertEqual(s.peek(), 'v2')
        self.assertEqual(s.top(), 'v1')
        self.assertEqual(s.pop(), 'v2')
        self.assertEqual(len(s), 1)

        self.assertIn('v1', s)
        self.assertNotIn('v2', s)

        s.add('v3')
        s.add('v4')
        del s['v3']
        self.assertEqual(s.to_set(), set(['v1', 'v4']))

        s2 = self.db.Set('other_set')
        s2.add('v1', 'v2', 'v3')

        self.assertEqual(s - s2, set(['v4']))
        self.assertEqual(s2 - s, set(['v2', 'v3']))
        self.assertEqual(s & s2, set(['v1']))
        self.assertEqual(s2 & s, set(['v1']))


class TestListObject(BaseVedisTestCase):
    def test_list_object(self):
        l = self.db.List('my_list')
        l.extend(['v1', 'v2', 'v3'])
        l.append('v4')
        items = [item for item in l]
        self.assertEqual(items, ['v1', 'v2', 'v3', 'v4'])
        self.assertEqual(len(l), 4)
        self.assertEqual(l.pop(), 'v1')
        self.assertEqual(l[0], None)  # This is kind of odd, perhaps a bug?
        self.assertEqual(l[1], 'v2')
        self.assertEqual(l[2], 'v3')
        self.assertEqual(l[3], 'v4')
        self.assertEqual(l[4], None)

        self.assertEqual(list(l[0:2]), [None, 'v2'])
        self.assertEqual(list(l[1:8]), ['v2', 'v3', 'v4'])
        self.assertEqual(list(l[3:4]), ['v4'])
        self.assertEqual(list(l[:]), [None, 'v2', 'v3', 'v4'])


class TestCustomCommands(BaseVedisTestCase):
    def test_custom_command(self):
        data = []

        @self.db.register('XTEST')
        def xtest(context, *params):
            data.extend(params)
            return 'hello'

        res = self.db.execute('XTEST %s %s', ('foo', 'barbaz'))
        self.assertEqual(data, ['foo', 'barbaz'])
        self.assertEqual(res, 'hello')

        res = self.db.execute('XTEST %s', ('single 111',))
        self.assertEqual(data, ['foo', 'barbaz', 'single 111'])
        self.assertEqual(res, 'hello')

        res = xtest('nug', 'baze')
        self.assertEqual(data, ['foo', 'barbaz', 'single 111', 'nug', 'baze'])
        self.assertEqual(res, 'hello')

        self.db.delete_command('XTEST')
        self.assertRaises(Exception, self.db.execute, 'XTEST')

    def test_multi_commands(self):
        @self.db.register('CMDA')
        def cmda(context, *params):
            return ['aa', ['bb', ['cc', 'dd'], 'ee'], 'ff']

        @self.db.register('CMDB')
        def cmdb(context, *params):
            return [param.title() for param in params]

        self.assertEqual(self.db.execute('CMDA'), [
            'aa',
            ['bb',
             ['cc',
              'dd'],
             'ee'],
            'ff',
        ])
        self.assertEqual(
            self.db.execute('CMDB %s %s %s', ('this', 'is a test', 'foo')),
            ['This', 'Is A Test', 'Foo'])

        self.db.delete_command('CMDA')
        self.db.delete_command('CMDB')

    def test_command_context(self):
        @self.db.register('MAGIC_SET')
        def magic_set(context, *params):
            for param in params:
                context[param] = param.title()
            return len(params)

        res = self.db.execute(
            'MAGIC_SET %s %s %s',
            ('foo', 'bar', 'this is a test'))
        self.assertEqual(res, 3)

        self.assertEqual(self.db['foo'], 'Foo')
        self.assertEqual(self.db['bar'], 'Bar')
        self.assertEqual(self.db['this is a test'], 'This Is A Test')

        self.db.delete_command('MAGIC_SET')

    def test_return_types(self):
        @self.db.register('TEST_RET')
        def test_ret(context, *params):
            return [
                ['list'],
                1337,
                3.14,
                True,
                None,
                'string',
                u'unicode',
            ]

        res = self.db.execute('TEST_RET')
        self.assertEqual(res, [
            ['list'],
            1337,
            3.14,
            1,
            None,
            'string',
            'unicode',
        ])

        self.db.delete_command('TEST_RET')


if __name__ == '__main__':
    unittest.main(argv=sys.argv)
