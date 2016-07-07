import unittest
from os.path import join
from os.path import dirname
from os import mkdir
from os import remove
from os import utime
from tempfile import mkdtemp
from shutil import rmtree

from jinja2 import TemplateNotFound

from repodono.nunja.engine import Engine
from repodono.nunja.loader import NunjaLoader
from repodono.nunja.registry import Registry


class LoaderTestCase(unittest.TestCase):
    """
    There is a bit of coupling with registry as that is the only
    implementation that we intend to support at the moment.
    """

    def setUp(self):
        self.registry = Registry(__name__, {})
        # Jinja2 environment will be initialized.
        self.engine = Engine(self.registry)
        self.tempdir = mkdtemp()
        self.molddir = join(self.tempdir, 'mold')
        mkdir(self.molddir)
        self.main_template = join(self.molddir, 'template.jinja')
        self.sub_template = join(self.molddir, 'sub.jinja')

        with open(self.main_template, 'w') as fd:
            fd.write('<div>{% include "tmp/mold/sub.jinja" %}</div>')

        with open(self.sub_template, 'w') as fd:
            fd.write('<span>{{ data }}</span>')

        # force the mtime to some time way in the past
        utime(self.sub_template, (-1, 1))

    def tearDown(self):
        rmtree(self.tempdir)

    def test_loader_core(self):
        self.registry.register_mold(self.molddir, 'tmp/mold')
        loader = NunjaLoader(self.registry)
        src, p, checker = loader.get_source(None, 'tmp/mold/sub.jinja')
        self.assertEqual(src, '<span>{{ data }}</span>')

    def test_loader_core_notfound_checks(self):
        self.registry.register_mold(self.molddir, 'tmp/mold')
        loader = NunjaLoader(self.registry)
        with self.assertRaises(TemplateNotFound):
            loader.get_source(None, 'tmp/mold/nothere.jinja')

        # Especially won't work with raw filesystem paths.
        with self.assertRaises(TemplateNotFound):
            loader.get_source(None, self.sub_template)

    def test_loader_reload_checker(self):
        self.registry.register_mold(self.molddir, 'tmp/mold')
        loader = NunjaLoader(self.registry)
        src, p, checker = loader.get_source(None, 'tmp/mold/sub.jinja')
        remove(self.sub_template)
        self.assertFalse(checker())

    def test_unregistered_not_found(self):
        with self.assertRaises(TemplateNotFound):
            result = self.engine.load_template('some/id')

    def test_base_loading(self):
        self.registry.register_mold(self.molddir, 'tmp/mold')
        template = self.engine.load_template('tmp/mold/sub.jinja')
        result = template.render(data='Hello World!')
        self.assertEqual(result, '<span>Hello World!</span>')

    def test_nested_loading(self):
        self.registry.register_mold(self.molddir, 'tmp/mold')
        template = self.engine.load_template('tmp/mold/template.jinja')
        result = template.render(data='Hello World!')
        self.assertEqual(result, '<div><span>Hello World!</span></div>')

    def test_base_auto_reload(self):
        self.registry.register_mold(self.molddir, 'tmp/mold')
        template = self.engine.load_template('tmp/mold/template.jinja')
        result = template.render(data='Hello World!')
        self.assertEqual(result, '<div><span>Hello World!</span></div>')

        with open(self.sub_template, 'w') as fd:
            fd.write('<div>{{ data }}</div>')

        result = template.render(data='Hello World!')
        self.assertEqual(result, '<div><div>Hello World!</div></div>')
        remove(self.sub_template)

        with self.assertRaises(TemplateNotFound):
            # as that was removed
            template.render(data='Hello World!')
