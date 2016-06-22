import unittest
from os.path import join
from os.path import dirname

import repodono.nunja
from repodono.nunja import exc
from repodono.nunja.registry import Registry
import repodono.nunja.testing


class RegistryTestCase(unittest.TestCase):

    def setUp(self):
        self.registry = Registry('repodono.nunja.testing.registry')

    def tearDown(self):
        pass

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
