import unittest

from pkg_resources import EntryPoint
from os.path import join
from os.path import dirname

import repodono.nunja
from repodono.nunja import exc
from repodono.nunja.registry import Registry
import repodono.nunja.testing

basic_tmpl_str = """\
<div {{ _nunja_data_ | safe }}>
<span>{{ value }}</span>
</div>
"""

class RegistryTestCase(unittest.TestCase):

    def setUp(self):
        self.registry = Registry('repodono.nunja.testing.registry', {})

    def tearDown(self):
        pass

    def register_entrypoint(self, raw):
        # Emulate the default lookup and registration
        ep = EntryPoint.parse(raw)
        self.registry.entry_points[ep.name] = ep

    def test_registry_register_mold(self):
        target = join(
            dirname(repodono.nunja.testing.__file__), 'mold', 'basic')
        self.registry.register_mold(target)
        self.assertEqual(self.registry.molds['basic'], target)

        # can't duplicate register
        with self.assertRaises(KeyError):
            self.registry.register_mold(target)

    def test_registry_register_mold_bad(self):
        target = join(dirname(repodono.nunja.testing.__file__), 'badmold')
        with self.assertRaises(exc.TemplateNotFoundError):
            self.registry.register_mold(target)

    def test_registry_register_module(self):
        self.registry.register_module(repodono.nunja.testing, subdir='mold')
        self.assertEqual(list(self.registry.molds.keys()), [
            'repodono.nunja.testing.mold/basic',
            'repodono.nunja.testing.mold/itemlist'
        ])
        # duplicate registration should do nothing extra.
        self.registry.register_module(repodono.nunja.testing, subdir='mold')
        self.assertEqual(list(self.registry.molds.keys()), [
            'repodono.nunja.testing.mold/basic',
            'repodono.nunja.testing.mold/itemlist'
        ])

        # Test that the lookup works.
        path = self.registry.lookup_path('repodono.nunja.testing.mold/basic')
        with open(join(path, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_lookup_from_entrypoint_recommended(self):
        # Recommended syntax
        self.register_entrypoint(
            'repodono.nunja.testing.mold = repodono.nunja.testing:mold')
        path = self.registry.lookup_path('repodono.nunja.testing.mold/basic')
        with open(join(path, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_lookup_from_entrypoint_alternative(self):
        # Working but alternative to the recommended naming
        self.register_entrypoint(
            'repodono.nunja.testmold = repodono.nunja.testing:mold')
        path = self.registry.lookup_path('repodono.nunja.testmold/basic')
        with open(join(path, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_bad_lookup_no_entrypoint(self):
        with self.assertRaises(KeyError):
            self.registry.lookup_path('repodono.nunja.testing.mold')

        with self.assertRaises(KeyError):
            self.registry.lookup_path('repodono.nunja.testing.mold/basic')

    def test_bad_lookup_with_entrypoint(self):
        self.register_entrypoint(
            'repodono.nunja.testing.mold = repodono.nunja.testing:mold')

        with self.assertRaises(KeyError):
            self.registry.lookup_path('repodono.nunja.testing.mold')

        self.assertIsNone(
            self.registry.lookup_path('repodono.nunja.testing.mold', None))

        with self.assertRaises(exc.TemplateNotFoundError):
            self.registry.lookup_path('repodono.nunja.testing.mold/missing')

    # Test cases for ensuring no failures done by register_module

    def test_registry_register_module_not_module(self):
        self.registry.register_module(None)
        self.assertFalse(self.registry.molds)

    def test_registry_register_module_subdir_missing(self):
        self.registry.register_module(repodono.nunja.testing, subdir='notmold')
        self.assertFalse(self.registry.molds)

    def test_registry_register_module_baddir(self):
        self.registry.register_module(repodono.nunja.testing, subdir='badmold')
        self.assertFalse(self.registry.molds)
