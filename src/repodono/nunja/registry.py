# -*- coding: utf-8 -*-
"""
Pluggable registry system for the repodono.nunja framework

The registry system by default uses the entry point system as defined by
the setuptools package.  To include the molds provided by a given module
or a directory, the proper entry points must be declared in its package.
For example::

    [repodono.nunja.mold]
    example.namespace.module = example.namespace:module
    repodono.nunja.testmold = repodono.nunja.testing:mold

In both examples, the ``module_name`` of the defined entry point will be
imported to resolve the associated directory for which this module was
defined in.  Then the first attribute will be joined with that directory
and be associated with the name of the entry point, thus acting as the
container (or prefix) for resolution of all the molds within.  The molds
will be in directories one level deep and is separated from its prefix
by the ``/`` character, as that is the natural path separator and thus
the suffixes will match the basename of the immediate subdirectories.

For example, given the identifier ``repodono.nunja.testmold/basic``, in
the context of the mold registry the prefix ``repodono.nunja.testmold``
will be resolved to the directory and then the subdirectory named
``basic`` will then be used.  While any name can be used, packages
should keep to names within their namespace.

However, the entry points only point to where the molds are.  For normal
usage and initialization, the molds will have to be registered and
instantiated.  Separate registration methods are offered, however by
default the names must obey the existing limitations as per the main
class.  If child classes override any of these the behaviors of the
different combinations of instances of the classes that make use of that
registry will have effectively undefined behavior.  Extend this with
caution, as the rules in place here are to accommodate usage within the
jinja loader and to facilitate the generation of requirejs configuration
in typical JavaScript environments.

For general usage, a default registry that include the entry points is
instantiated, however users are able to create their own registry class
that omit this like so::

    custom_registry = Registry('namespace.custom_registry', entry_points={})

This will omit all entry points so that the default lookup or register
methods will not make use of them.
"""

import json
from os import listdir
from os import walk

from os.path import altsep
from os.path import sep
from os.path import pardir

from os.path import basename
from os.path import dirname
from os.path import exists
from os.path import isdir
from os.path import join
from os.path import relpath
from logging import getLogger
from types import ModuleType

from .exc import TemplateNotFoundError

TMPL_FN_EXT = '.jinja'
REQ_TMPL_NAME = 'template' + TMPL_FN_EXT
ENTRY_POINT_NAME = 'repodono.nunja.mold'

# I supposed this can all be hardcoded, but eating ones dogfood can be
# useful as a litmus test while this keeps the naming scheme consistent,
# even if usage is a bit different.
DEFAULT_WRAPPER_NAME = '_core_/_default_wrapper_'
DEFAULT_MOLDS = {
    DEFAULT_WRAPPER_NAME: join(dirname(__file__), DEFAULT_WRAPPER_NAME)
}

logger = getLogger(__name__)
_marker = object()


class Registry(object):
    """
    Default registry implementation.
    """

    def __init__(self, registry_name, entry_points=None, default_prefix='_'):
        """
        Arguments:

        registry_name
            The name of this registry.
        entry_points
            Dictionary of entry_point name to its entry_point that has
            the same name.
        default_prefix
            The default prefix to use for registration if no mold_id was
            provided.
        """

        self.entry_points = {} if entry_points is None else entry_points
        self.registry_name = registry_name
        self.default_prefix = default_prefix
        self.molds = {}
        # Forcibly register the default one here as the core rendering
        # need this wrapper.
        self.molds.update(DEFAULT_MOLDS)

    def mold_id_to_path(self, mold_id, default=_marker):
        """
        Lookup the path of a mold identifier.
        """

        def handle_default(debug_msg=None):
            if debug_msg:
                logger.debug('mold_id_to_path:' + debug_msg, mold_id)
            if default is _marker:
                raise KeyError(
                    'Failed to lookup mold_id %s to a path' % mold_id)
            return default

        result = self.molds.get(mold_id)
        if result:
            return result

        try:
            prefix, mold_basename = mold_id.split('/')
        except ValueError:
            return handle_default(
                'mold_id %s not found and not in standard format')

        try:
            ep = self.entry_points[prefix]
        except KeyError:
            return handle_default(
                'mold_id %s not found in self.entry_points.')

        try:
            module = __import__(ep.module_name, fromlist=['__name__'], level=0)
        except ImportError:
            return handle_default(
                'mold_id %s resolves to entry point that failed to import')

        for path in module.__path__:
            full_path = join(path, ep.attrs[0], mold_basename)
            try:
                self.verify_path(full_path)
            except TemplateNotFoundError:
                continue
            else:
                return full_path

        return handle_default(
            'mold_id %s does not lead to a valid template.jinja')

    def lookup_path(self, mold_id_path, default=_marker):
        """
        Lookup the filesystem path from a mold_id compatible path.
        """

        fragments = mold_id_path.split('/')
        mold_id = '/'.join(fragments[:2])
        try:
            subpath = []
            for piece in fragments[2:]:
                if (sep in piece or (altsep and altsep in piece) or
                        piece == pardir):
                    raise KeyError
                elif piece and piece != '.':
                    subpath.append(piece)
            path = self.mold_id_to_path(mold_id)
        except KeyError:
            if default is _marker:
                raise
            return default

        return join(path, *subpath)
        # TODO Should a lookup_template be implemented?

    def verify_path(self, path):
        """
        Verify that this base path (resolved from a mold_id) will lead
        to a working template file.
        """

        if not exists(join(path, REQ_TMPL_NAME)):
            raise TemplateNotFoundError(
                'required template not found at `%s`' % path)
        return True

    def verify_path_with_mold_id(self, path, mold_id):
        """
        Default verification/sanity checks to ensure the names are added
        with the consistency that we need for the system to work, which
        is that the basename of the path is equal to the second element
        of the 2-tuple generated by mold_id.split('/').
        """

        try:
            mold_prefix, mold_basename = mold_id.split('/')
        except ValueError:
            raise KeyError(
                'mold_id not following standard format of some prefix, '
                'followed by a `/`, and then the basename of provided path.'
            )

        if mold_basename != basename(path):
            raise KeyError(
                'mold_id suffix mismatch with basename of its to be defined '
                'path'
            )
        return True

    def register_mold(self, path, mold_id=None):
        """
        Register the path as a usable mold.

        If mold_id is not provided, default to the basename of the dir.
        """

        if mold_id is None:
            mold_id = self.default_prefix + '/' + basename(path)

        if mold_id in self.molds:
            raise KeyError(
                'duplicate mold_id `%s` cannot be registered as mold' %
                mold_id)

        self.verify_path(path)
        self.verify_path_with_mold_id(path, mold_id)
        self.molds[mold_id] = path

    def register_module(self, module, subdir=None, prefix=None, paths=None):
        """
        Register all subdirectories at the path of the specified module.

        All errors will be logged.

        Arguments

        module
            The Python module to search for the molds.  Note that all
            paths associated with the module will be searched.
        subdir
            The subdirectory within the target module that contains all
            the molds to be registered.
        prefix
            An explicit prefix to all the molds that will be registered.
            Default is to use the module + subpath.
        """

        if not isinstance(module, ModuleType):
            logger.warning('%s is not a module', module)
            return False

        if paths is None:
            paths = module.__path__

        pc = mc = 0

        if prefix is None:
            prefix = '.'.join(m for m in (module.__name__, subdir) if m)

        for path in paths:
            if subdir:
                path = join(path, subdir)

            if not isdir(path):
                continue

            pc += 1

            for target in listdir(path):
                target_path = join(path, target)
                if not isdir(target_path):
                    continue

                mold_id = prefix + '/' + target

                try:
                    self.register_mold(target_path, mold_id=mold_id)
                except TemplateNotFoundError:
                    logger.debug(
                        '%s missing required %s', target_path, REQ_TMPL_NAME)
                except KeyError:
                    logger.warning(
                        '%s already registered to %s',
                        mold_id, self.registry_name)
                else:
                    mc += 1

        logger.info(
            'Registered %d molds in %d subdir(s) named %s of module %s',
            mc, pc, subdir, module.__name__
        )

    def init_entrypoints(self, entry_points=None):
        """
        Register all the local entry points.  By default entry points
        recorded here will be loaded into the mold cache which will
        speed up lookups but disables to dynamic loading of all mock_ids
        that are prefixed with the entry point names.
        """

        if entry_points is None:
            entry_points = self.entry_points

        for ep in entry_points.values():
            try:
                module = __import__(
                    ep.module_name, fromlist=['__name__'], level=0)
            except ImportError:
                logger.warning(
                    'ImportError: %s; cannot register as mold', ep.module_name)
                continue

            subdir = ep.attrs[0]
            self.register_module(module, subdir, ep.name)

    def export_nunja_requirejs_json(self):
        """
        Export the registered molds for requirejs configuration function
        as a json encoded string.
        """

        return json.dumps({
            'paths': self.molds,
        })

    def export_jinja_template_paths(self, match_func=None):
        """
        Export all filenames that end with `.jinja` that can be imported
        from the nunja/nunjucks environment as json encoded string.
        """

        if match_func is None:
            match_func = lambda p: p.endswith(TMPL_FN_EXT)

        def generate_paths(path):
            for r, d, files in walk(path):
                for name in files:
                    if match_func(name):
                        yield relpath(join(r, name), path)

        results = {
            name: sorted(generate_paths(path))
            for name, path in self.molds.items()
        }

        return json.dumps({
            'template_map': results
        })


def create_default_registry(name):
    """
    Default registry constructor that will load all the entry points
    then add that to the returned Registry.
    """

    _entry_points = {}

    try:
        from pkg_resources import iter_entry_points
    except ImportError:  # pragma: no cover
        logger.error(
            'The `repodono.nunja` registry is disabled as the setuptools '
            'package is missing the `pkg_resources` module'
        )
    else:  # pragma: no cover
        # First just dump all the relevant bits from the entry point into
        # the _source dict.
        for ep in iter_entry_points(ENTRY_POINT_NAME):
            _entry_points[ep.name] = ep

    # Then create the default registry based on that.
    return Registry(name, _entry_points)


# Create a default, uninitialized instance.
registry = create_default_registry(__name__)
