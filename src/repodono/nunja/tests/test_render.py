import unittest
from os.path import join
from os.path import dirname

import repodono.nunja
from repodono.nunja.engine import Engine
from repodono.nunja.registry import Registry
import repodono.nunja.testing


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.registry = Registry(__name__, {})
        self.registry.register_module(repodono.nunja.testing, subdir='mold')
        self.engine = Engine(self.registry)

    def tearDown(self):
        pass

    def test_base_rendering(self):
        result = self.engine.execute(
            'repodono.nunja.testing.mold/basic',
            data={'value': 'Hello World!'})

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.testing.mold/basic">\n'
            '<span>Hello World!</span>\n'
            '</div>'
        )

        # Should work again, from cache.
        result = self.engine.execute(
            'repodono.nunja.testing.mold/basic',
            data={'value': 'Hello World!'})

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.testing.mold/basic">\n'
            '<span>Hello World!</span>\n'
            '</div>'
        )

    def test_base_xss_handling(self):
        result = self.engine.execute(
            'repodono.nunja.testing.mold/basic',
            data={'value': '<xss>'})

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.testing.mold/basic">\n'
            '<span>&lt;xss&gt;</span>\n'
            '</div>'
        )
