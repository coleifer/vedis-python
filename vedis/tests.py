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


class TestGetSet(BaseVedisTestCase):
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

    def test_random_string(self):
        rs = self.db.random_string(5)
        self.assertEqual(len(rs), 5)
        self.assertTrue(isinstance(rs, basestring))

    def test_random_number(self):
        rn = self.db.random_number()
        self.assertTrue(isinstance(rn, long))


if __name__ == '__main__':
    unittest.main(argv=sys.argv)
