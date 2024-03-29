import unittest
from os.path import join
from os.path import dirname

from jinja2 import TemplateNotFound
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

    def test_template_retrieval_and_render(self):
        # As this was retrieved directly, none of the "mold" bits are
        # provided by the result.
        result = self.engine.load_template(
            'repodono.nunja.testing.mold/basic/template.jinja'
        ).render(value='Hello World!')
        self.assertEqual(result, '<span>Hello World!</span>')

    def test_template_retrieval_not_found(self):
        with self.assertRaises(TemplateNotFound):
            result = self.engine.load_template(
                'repodono.nunja.testing.mold/basic/no_such_template.jinja')

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
            'list_template': self.engine.load_mold(
                'repodono.nunja.testing.mold/itemlist'),
            'itemlists': [['list_1', ['Item 1', 'Item 2']]],
        }

        result = self.engine.execute(
            'repodono.nunja.testing.mold/include_by_value', data=data)

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.testing.mold/include_by_value">\n'
            '<dl id="">\n\n'
            '  <dt>list_1</dt>\n'
            '  <dd><ul id="list_1">\n\n'
            '  <li>Item 1</li>\n'
            '  <li>Item 2</li>\n'
            '</ul></dd>\n'
            '</dl>\n'
            '</div>'
        )

    def test_manual_include_multilist(self):
        data = {
            'list_template': self.engine.load_mold(
                'repodono.nunja.testing.mold/itemlist'),
            'list_id': 'root_id',
            'itemlists': [
                ['list_1', ['Item 1', 'Item 2']],
                ['list_2', ['Item 3', 'Item 4']],
                ['list_3', ['Item 5', 'Item 6']],
            ],
        }

        result = self.engine.execute(
            'repodono.nunja.testing.mold/include_by_value', data=data)

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.testing.mold/include_by_value">\n'
            '<dl id="root_id">\n\n'
            '  <dt>list_1</dt>\n'
            '  <dd><ul id="list_1">\n\n'
            '  <li>Item 1</li>\n'
            '  <li>Item 2</li>\n'
            '</ul></dd>\n'
            '  <dt>list_2</dt>\n'
            '  <dd><ul id="list_2">\n\n'
            '  <li>Item 3</li>\n'
            '  <li>Item 4</li>\n'
            '</ul></dd>\n'
            '  <dt>list_3</dt>\n'
            '  <dd><ul id="list_3">\n\n'
            '  <li>Item 5</li>\n'
            '  <li>Item 6</li>\n'
            '</ul></dd>\n'
            '</dl>\n'
            '</div>'
        )

    def test_named_include_multilist(self):
        data = {
            'list_id': 'root_id',
            'itemlists': [
                ['list_1', ['Item 1', 'Item 2']],
                ['list_2', ['Item 3', 'Item 4']],
                ['list_3', ['Item 5', 'Item 6']],
            ],
        }

        result = self.engine.execute(
            'repodono.nunja.testing.mold/include_by_name', data=data)

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.testing.mold/include_by_name">\n'
            '<dl id="root_id">\n\n'
            '  <dt>list_1</dt>\n'
            '  <dd><ul id="list_1">\n\n'
            '  <li>Item 1</li>\n'
            '  <li>Item 2</li>\n'
            '</ul></dd>\n'
            '  <dt>list_2</dt>\n'
            '  <dd><ul id="list_2">\n\n'
            '  <li>Item 3</li>\n'
            '  <li>Item 4</li>\n'
            '</ul></dd>\n'
            '  <dt>list_3</dt>\n'
            '  <dd><ul id="list_3">\n\n'
            '  <li>Item 5</li>\n'
            '  <li>Item 6</li>\n'
            '</ul></dd>\n'
            '</dl>\n'
            '</div>'
        )
