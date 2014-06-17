import base64
import csv
import re
from StringIO import StringIO
import sys
import unittest

try:
    from vedis import Vedis
except ImportError:
    sys.stderr.write('Unable to import `vedis`. Make sure it is properly '
                     'installed.\n')
    sys.stderr.flush()
    raise


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
    def test_get_set(self):
        self.set_k1_k2()
        self.assertEqual(self.db['k1'], 'v1')
        self.assertEqual(self.db['k2'], 'v2')
        self.assertRaises(KeyError, lambda: self.db['k3'])

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

    def test_delete(self):
        self.set_k1_k2()

        self.assertEqual(self.db['k1'], 'v1')
        del self.db['k1']
        self.assertRaises(KeyError, lambda: self.db['k1'])

        self.assertEqual(self.db['k2'], 'v2')
        self.db.delete('k2')
        self.assertRaises(KeyError, lambda: self.db['k2'])

    def test_exists(self):
        self.set_k1_k2()
        self.db['k2'] = ''
        self.assertTrue(self.db.exists('k1'))
        self.assertTrue(self.db.exists('k2'))
        self.assertFalse(self.db.exists('k3'))

        del self.db['k1']
        self.assertFalse(self.db.exists('k1'))

        self.assertIn('k2', self.db)
        self.assertNotIn('k1', self.db)

    def test_mget(self):
        self.set_k1_k2()
        res = self.db.mget('k1', 'missing', 'k2')
        self.assertEqual(list(res), ['v1', None, 'v2'])

    def test_setnx(self):
        self.db['k1'] = 'v1'
        self.db.setnx('k1', 'v-x')
        self.assertEqual(self.db['k1'], 'v1')

        self.db.setnx('k2', 'v-x')
        self.assertEqual(self.db['k2'], 'v-x')

    def test_mset(self):
        self.db['k1'] = 'v1'
        self.db.mset(k1='v-x', k2='v2', foo='bar')
        self.assertEqual(
            list(self.db.mget('k1', 'k2', 'foo')),
            ['v-x', 'v2', 'bar'])

        self.db.mset(**{'k s': 'vs', 'k s2': 'vs2'})
        self.assertEqual(
            list(self.db.mget('k s', 'k s2')),
            ['vs', 'vs2'])

    def test_msetnx(self):
        self.db['k1'] = 'v1'
        self.db.msetnx(k1='v-x', k2='v2', foo='bar')
        self.assertEqual(
            list(self.db.mget('k1', 'k2', 'foo')),
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
        self.assertTrue(isinstance(rs, basestring))

    def test_random_number(self):
        rn = self.db.random_number()
        self.assertTrue(isinstance(rn, long))

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
        self.assertEqual(encoded, base64.b64encode(data))


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
        self.db.hmset('hash', k1='v1', k2='v2', k3='v3')
        self.assertEqual(self.db.hgetall('hash'), {
            'k1': 'v1',
            'k2': 'v2',
            'k3': 'v3'})

        self.assertEqual(
            list(self.db.hmget('hash', 'k1', 'missing', 'k2')),
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
        self.assertEqual(self.db.hgetall('missing'), None)
        self.assertEqual(self.db.hlen('missing'), 0)
        self.assertEqual(self.db.hmget('missing', 'x'), None)
        self.assertFalse(self.db.hexists('missing', 'x'))


class TestSetCommands(BaseVedisTestCase):
    def test_set_methods(self):
        vals = set(['v1', 'v2', 'v3', 'v4'])
        for val in vals:
            self.db.sadd('set', val)

        self.assertEqual(self.db.scard('set'), 4)
        self.assertTrue(self.db.sismember('set', 'v1'))
        self.assertFalse(self.db.sismember('set', 'missing'))

        self.assertEqual(self.db.speek('set'), 'v4')
        self.assertEqual(self.db.spop('set'), 'v4')

        self.assertEqual(self.db.stop('set'), 'v1')
        self.assertEqual(self.db.slen('set'), 3)

        self.assertTrue(self.db.srem('set', 'v2'))
        self.assertEqual(self.db.slen('set'), 2)
        self.assertFalse(self.db.srem('set', 'missing'))

        self.assertEqual(set(self.db.smembers('set')), set(['v1', 'v3']))

    def test_intersection_difference(self):
        self.db.sadd('s1', 'v1')
        self.db.sadd('s1', 'v2')
        self.db.sadd('s1', 'v3')

        self.db.sadd('s2', 'v2')
        self.db.sadd('s2', 'v3')
        self.db.sadd('s2', 'v4')

        self.assertEqual(
            set(self.db.sinter('s1', 's2')),
            set(['v2', 'v3']))

        self.assertEqual(set(self.db.sdiff('s1', 's2')), set(['v1']))
        self.assertEqual(set(self.db.sdiff('s2', 's1')), set(['v4']))


class TestListCommands(BaseVedisTestCase):
    def test_list_methods(self):
        self.db.lpush('list', 'v1', 'v2', 'v3')
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


if __name__ == '__main__':
    unittest.main(argv=sys.argv)
