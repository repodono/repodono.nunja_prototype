import unittest

import json
from pkg_resources import EntryPoint
from os.path import join
from os.path import dirname
import sys

import repodono.nunja
from repodono.nunja import exc
from repodono.nunja.registry import Registry
import repodono.nunja.testing

basic_tmpl_str = '<span>{{ value }}</span>\n'


class RegistryTestCase(unittest.TestCase):

    def setUp(self):
        self.registry = Registry('repodono.nunja.testing.registry', {})

    def tearDown(self):
        pass

    def emulate_register_entrypoint(self, raw):
        # Emulate the default lookup and registration
        ep = EntryPoint.parse(raw)
        self.registry.entry_points[ep.name] = ep

    def test_registry_register_mold(self):
        target = join(
            dirname(repodono.nunja.testing.__file__), 'mold', 'basic')
        self.registry.register_mold(target)
        # Default prefix is automatically added.
        self.assertEqual(self.registry.molds['_/basic'], target)

        # can't duplicate register
        with self.assertRaises(KeyError):
            self.registry.register_mold(target)

    def test_registry_register_mold_manual(self):
        target = join(
            dirname(repodono.nunja.testing.__file__), 'mold', 'basic')
        self.registry.register_mold(target, mold_id='blah/basic')
        # Default prefix is automatically added.
        self.assertEqual(self.registry.molds['blah/basic'], target)
        self.assertEqual(self.registry.mold_id_to_path('blah/basic'), target)

    def test_registry_register_mold_manual_failures(self):
        target = join(
            dirname(repodono.nunja.testing.__file__), 'mold', 'basic')

        with self.assertRaises(KeyError):
            self.registry.register_mold(target, mold_id='basic')

        with self.assertRaises(KeyError):
            self.registry.register_mold(target, mold_id='not/asic')

        with self.assertRaises(KeyError):
            self.registry.register_mold(target, mold_id='is/invalid/basic')

    def test_registry_register_mold_bad(self):
        target = join(dirname(repodono.nunja.testing.__file__), 'badmold')
        with self.assertRaises(exc.TemplateNotFoundError):
            self.registry.register_mold(target)

    def test_registry_register_module(self):
        self.registry.register_module(repodono.nunja.testing, subdir='mold')
        items = [
            '_core_/_default_wrapper_',
            'repodono.nunja.testing.mold/basic',
            'repodono.nunja.testing.mold/include_by_value',
            'repodono.nunja.testing.mold/itemlist',
        ]
        self.assertEqual(sorted(self.registry.molds.keys()), items)
        # duplicate registration should do nothing extra.
        self.registry.register_module(repodono.nunja.testing, subdir='mold')
        self.assertEqual(sorted(self.registry.molds.keys()), items)

        # Test that the lookup works.
        path = self.registry.mold_id_to_path(
            'repodono.nunja.testing.mold/basic')
        with open(join(path, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_mold_id_to_path_from_entrypoint_recommended(self):
        # Recommended syntax
        self.emulate_register_entrypoint(
            'repodono.nunja.testing.mold = repodono.nunja.testing:mold')
        path = self.registry.mold_id_to_path(
            'repodono.nunja.testing.mold/basic')
        with open(join(path, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_mold_id_to_path_from_entrypoint_alternative(self):
        # Working but alternative to the recommended naming
        self.emulate_register_entrypoint(
            'repodono.nunja.testmold = repodono.nunja.testing:mold')
        path = self.registry.mold_id_to_path('repodono.nunja.testmold/basic')
        with open(join(path, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_mold_id_to_path_from_entrypoint_import_error(self):
        # Working but alternative to the recommended naming
        self.emulate_register_entrypoint(
            'repodono.nunja.no.such.module = repodono.nunja.no:mold')
        with self.assertRaises(KeyError):
            self.registry.mold_id_to_path('repodono.nunja.no.such.module/mold')
        self.assertEqual(self.registry.mold_id_to_path(
            'repodono.nunja.no.such.module/mold', ''), '')

    def test_bad_mold_id_to_path_no_entrypoint(self):
        with self.assertRaises(KeyError):
            self.registry.mold_id_to_path('repodono.nunja.testing.mold')

        self.assertEqual(
            self.registry.mold_id_to_path(
                'repodono.nunja.testing.mold', ''), '')

        with self.assertRaises(KeyError):
            self.registry.mold_id_to_path('repodono.nunja.testing.mold/basic')

        self.assertEqual(
            self.registry.mold_id_to_path(
                'repodono.nunja.testing.mold/basic', ''), '')

    def test_bad_mold_id_to_path_with_entrypoint(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.testing.mold = repodono.nunja.testing:mold')

        with self.assertRaises(KeyError):
            self.registry.mold_id_to_path('repodono.nunja.testing.mold')

        self.assertEqual(
            self.registry.mold_id_to_path(
                'repodono.nunja.testing.mold', ''), '')

        with self.assertRaises(KeyError):
            self.registry.mold_id_to_path(
                'repodono.nunja.testing.mold/missing')

        self.assertEqual(
            self.registry.mold_id_to_path(
                'repodono.nunja.testing.mold/missing', ''), '')

    def test_bad_mold_id_to_path_with_entrypoint_missing_template(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.testing.badmold = repodono.nunja.testing:badmold')

        with self.assertRaises(KeyError):
            self.registry.mold_id_to_path(
                'repodono.nunja.testing.badmold/nomold')

        self.assertEqual(self.registry.mold_id_to_path(
            'repodono.nunja.testing.badmold/nomold', ''), '')

    @unittest.skipIf(sys.version_info < (3, 3), "py3.3 __init__.py optional")
    def test_mold_id_to_path_with_entrypoint_dir_not_real_mod_py3_3(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.testing.py3 = repodono.nunja.testing.py3mod:molds')

        self.assertNotEqual(self.registry.mold_id_to_path(
            'repodono.nunja.testing.py3/mold', ''), '')

    def test_register_all_entrypoints_fail(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.no.such.module = repodono.nunja.testing.no:mold')
        self.registry.init_entrypoints()
        # Defaults.
        self.assertEqual(len(self.registry.molds), 1)

    def test_register_all_entrypoints_fail_no_module(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.testing.badmold = repodono.nunja.no:badmold')
        self.registry.init_entrypoints()
        self.assertEqual(len(self.registry.molds), 1)

    def test_register_all_entrypoints_fail_no_template(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.testing.badmold = repodono.nunja.testing:badmold')
        self.registry.init_entrypoints()
        self.assertEqual(len(self.registry.molds), 1)

    def test_register_all_entrypoints_success(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.testing.mold = repodono.nunja.testing:mold')
        path1 = self.registry.mold_id_to_path(
            'repodono.nunja.testing.mold/basic')
        self.registry.init_entrypoints()
        path2 = self.registry.mold_id_to_path(
            'repodono.nunja.testing.mold/basic')
        self.assertEqual(path1, path2)
        path3 = self.registry.molds['repodono.nunja.testing.mold/basic']
        self.assertEqual(path1, path3)

        with open(join(path2, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_register_all_entrypoints_lookup_path(self):
        self.emulate_register_entrypoint(
            'rntm = repodono.nunja.testing:mold')

        with self.assertRaises(KeyError):
            # As this is not a valid mold_id
            path1 = self.registry.mold_id_to_path(
                'rntm/itemlist/template.jinja')

        # can lookup before registration
        path1 = self.registry.lookup_path('rntm/itemlist/template.jinja')

        self.registry.init_entrypoints()
        # lookup after registration
        path2 = self.registry.lookup_path('rntm/itemlist/template.jinja')
        self.assertEqual(path1, path2)

        with open(join(path2), 'r') as fd:
            contents = fd.readline()
        self.assertEqual(contents, '<ul id="{{ list_id }}">\n')

    def test_lookup_block_parent_traversal(self):
        self.emulate_register_entrypoint(
            'rntm = repodono.nunja.testing:mold')

        # Parent traversal blocked.
        with self.assertRaises(KeyError):
            self.registry.lookup_path('rntm/itemlist/../../../registry.py')

        # single dots will be omitted.
        path1 = self.registry.lookup_path('rntm/itemlist/./template.jinja')
        self.assertTrue(path1.endswith('testing/mold/itemlist/template.jinja'))

    def test_register_all_entrypoints_success_alt_name(self):
        self.emulate_register_entrypoint(
            'repodono.nunja.testmold = repodono.nunja.testing:mold')
        path1 = self.registry.mold_id_to_path('repodono.nunja.testmold/basic')
        self.registry.init_entrypoints()
        path2 = self.registry.mold_id_to_path('repodono.nunja.testmold/basic')
        self.assertEqual(path1, path2)
        path3 = self.registry.molds['repodono.nunja.testmold/basic']
        self.assertEqual(path1, path3)

        with open(join(path2, 'template.jinja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_lookup_path_default_missing_registration(self):
        default = '/some/path'
        self.assertEqual(
            self.registry.lookup_path(
                '__/itemlist/template.jinja', default=default),
            default,
        )

    def test_lookup_path_default_invalid_path(self):
        self.emulate_register_entrypoint(
            'rntm = repodono.nunja.testing:mold')

        with self.assertRaises(KeyError):
            self.registry.lookup_path('__/itemlist/template.jinja')

        default = '/some/path'
        self.assertEqual(
            self.registry.lookup_path(
                '__/itemlist/template.jinja', default=default),
            default,
        )

    def test_export_local_requirejs(self):
        # TODO contents are currently absolute paths, hope it's okay.
        self.emulate_register_entrypoint(
            'repodono.nunja.testmold = repodono.nunja.testing:mold')
        self.registry.init_entrypoints()
        result = json.loads(self.registry.export_local_requirejs())
        p = self.registry.mold_id_to_path('repodono.nunja.testmold/basic')
        self.assertEqual(result['paths']['repodono.nunja.testmold/basic'], p)

    # Test cases for ensuring no failures done by register_module

    def test_registry_register_module_not_module(self):
        self.registry.register_module(None)
        self.assertEqual(len(self.registry.molds), 1)

    def test_registry_register_module_subdir_missing(self):
        self.registry.register_module(repodono.nunja.testing, subdir='notmold')
        self.assertEqual(len(self.registry.molds), 1)

    def test_registry_register_module_baddir(self):
        self.registry.register_module(repodono.nunja.testing, subdir='badmold')
        self.assertEqual(len(self.registry.molds), 1)
