import unittest
from os.path import join
from os.path import dirname

import repodono.nunja
from repodono.nunja.engine import Engine


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = Engine()
        path = join(dirname(repodono.nunja.__file__), 'mold', 'basic')
        self.engine.register_mold(path)

    def tearDown(self):
        pass

    def test_base_rendering(self):
        result = self.engine.execute('basic', data={'value': 'Hello World!'})
        self.assertEqual(
            result,
            '<div data-nunja="basic">\n'
            '<span>Hello World!</span>\n'
            '</div>'
        )
        # Should work again, from cache.
        result = self.engine.execute('basic', data={'value': 'Hello World!'})
        self.assertEqual(
            result,
            '<div data-nunja="basic">\n'
            '<span>Hello World!</span>\n'
            '</div>'
        )
