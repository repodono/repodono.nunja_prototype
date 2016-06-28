# -*- coding: utf-8 -*-
import unittest
from os.path import join
from os.path import dirname

import repodono.nunja
from repodono.nunja.engine import Engine
from repodono.nunja.registry import registry
import repodono.nunja.testing


class DummyTableData(object):
    """
    This is a data provider that feeds stuff to the table mold.
    """

    def __init__(self, columns, data, css=None):
        self.columns = columns
        self.data = data
        self.css = css or {}

    def to_jsonable(self):
        """
        Convert to a dict that can be dumped into json.
        """

        column_ids = [c[0] for c in self.columns]

        results = {
            "active_columns": [id_ for id_, name in self.columns],
            "column_map": dict(self.columns),
            "data": [
                dict(zip(column_ids, datum)) for datum in self.data
            ],
            "css": self.css,
        }

        return results


class TestDummyTableData(unittest.TestCase):
    """
    These tests here serves as active documentation on what a given
    endpoint will need to generate.
    """

    def test_basic(self):
        data = DummyTableData([], [])
        self.assertEqual(data.to_jsonable(), {
            'active_columns': [],
            'column_map': {},
            'data': [],
            'css': {},
        })

    def test_one(self):
        data = DummyTableData([
            ['ID', 'Identifier']
        ], [
            ['1'],
            ['2'],
        ])
        self.assertEqual(data.to_jsonable(), {
            'active_columns': ['ID'],
            'column_map': {
                'ID': 'Identifier',
            },
            'data': [
                {'ID': '1'},
                {'ID': '2'},
            ],
            'css': {},
        })

    def test_two(self):
        data = DummyTableData([
            ['id', 'Id'],
            ['name', 'Given Name'],
        ], [
            ['1', 'John Smith'],
            ['2', 'Eve Adams'],
        ])
        self.assertEqual(data.to_jsonable(), {
            'active_columns': ['id', 'name'],
            'column_map': {
                'id': 'Id',
                'name': 'Given Name',
            },
            'data': [
                {'id': '1', 'name': 'John Smith'},
                {'id': '2', 'name': 'Eve Adams'},
            ],
            'css': {},
        })


class MoldTableTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = Engine(registry)

    def tearDown(self):
        pass

    def test_null_rendering(self):
        result = self.engine.execute('repodono.nunja.molds/table', data={
            'css': {},
        })

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.molds/table">\n'
            '<table class="">\n'
            '  <thead>\n'
            '    <tr class="">\n'
            '    \n'
            '    </tr>\n'
            '  </thead>\n'
            '  <tbody>\n'
            '    \n'
            '  </tbody>\n'
            '</table>\n'
            '</div>'
        )

    def test_basic_table_contents(self):
        data = DummyTableData([
            ['id', 'Id'],
            ['name', 'Given Name'],
        ], [
            ['1', 'John Smith'],
            ['2', 'Eve Adams'],
        ])

        result = self.engine.execute(
            'repodono.nunja.molds/table', data=data.to_jsonable())

        self.assertEqual(
            result,
            '<div data-nunja="repodono.nunja.molds/table">\n'
            '<table class="">\n'
            '  <thead>\n'
            '    <tr class="">\n'
            '    <td>Id</td><td>Given Name</td>\n'
            '    </tr>\n'
            '  </thead>\n'
            '  <tbody>\n'
            '    <tr class="">\n'
            '      <td>1</td><td>John Smith</td>\n'
            '    </tr><tr class="">\n'
            '      <td>2</td><td>Eve Adams</td>\n'
            '    </tr>\n'
            '  </tbody>\n'
            '</table>\n'
            '</div>'
        )
