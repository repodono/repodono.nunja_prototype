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

    def test_manual_include(self):
        data = {
            'list_template': self.engine.load_template(
                'repodono.nunja.testing.mold/itemlist'),
            'itemlists': [['list_1', ['Item 1', 'Item 2']]],
        }

        result = self.engine.execute(
            'repodono.nunja.testing.mold/import_with_data', data=data)

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.testing.mold/import_with_data">\n'
            '<dl id="">\n\n'
            '  <dt>list_1</dt>\n'
            '  <dd><ul id="list_1">\n\n'
            '  <li>Item 1</li>\n'
            '  <li>Item 2</li>\n'
            '</ul></dd>\n'
            '</dl>\n'
            '</div>'
        )
