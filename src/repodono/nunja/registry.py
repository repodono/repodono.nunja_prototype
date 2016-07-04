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
by the ``/`` character.

For example, given the identifier ``repodono.nunja.testmold/basic``, in
the context of the mold registry the prefix ``repodono.nunja.testmold``
will be resolved to the directory and then the subdirectory named
``basic`` will then be used.  While any name can be used, packages
should keep to names within their namespace.

However, the entry points only point to where the molds are.  For normal
usage and initialization, the molds will have to be registered and
instantiated.  Separate registration methods are offered.

For general usage, a default registry that include the entry points is
instantiated, however users are able to create their own registry class
that omit this like so::

    custom_registry = Registry('namespace.custom_registry', entry_points={})

This will omit all entry points so that the default lookup or register
methods will not make use of them.
"""

import json
from os import listdir
from os.path import basename
from os.path import dirname
from os.path import exists
from os.path import isdir
from os.path import join
from logging import getLogger
from types import ModuleType

from .exc import TemplateNotFoundError

REQ_TMPL_NAME = 'template.jinja'
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

    def __init__(self, registry_name, entry_points=None):
        self.entry_points = {} if entry_points is None else entry_points
        self.registry_name = registry_name
        self.molds = {}
        # Forcibly register the default one here as the core rendering
        # need this wrapper.
        self.molds.update(DEFAULT_MOLDS)

    def lookup_path(self, mold_id, default=_marker):
        """
        Lookup the path of a mold identifier.
        """

        def handle_default(debug_msg=None):
            if debug_msg:
                logger.debug('lookup_path:' + debug_msg, mold_id)
            if default is _marker:
                raise KeyError(
                    'Failed to lookup mold_id %s to a path' % mold_id)
            return default

        result = self.molds.get(mold_id)
        if result:
            return result

        try:
            prefix, mold_dir = mold_id.split('/')
        except ValueError:
            return handle_default(
                'mold_id %s not found and not in standard format')

        ep = self.entry_points[prefix]
        try:
            module = __import__(ep.module_name, fromlist=['__name__'], level=0)
        except ImportError:
            return handle_default(
                'mold_id %s resolves to entry point that failed to import')

        # XXX not searching through all paths
        for path in module.__path__:
            full_path = join(path, ep.attrs[0], mold_dir)
            try:
                self.verify_path(full_path)
            except TemplateNotFoundError:
                continue
            else:
                return full_path

        return handle_default(
            'mold_id %s does not lead to a valid template.jinja')

    def verify_path(self, path):
        if not exists(join(path, REQ_TMPL_NAME)):
            raise TemplateNotFoundError(
                'required template not found at `%s`' % path)
        return True

    def register_mold(self, path, mold_id=None):
        """
        Register the path as a usable mold.

        If mold_id is not provided, default to the basename of the dir.
        """

        if mold_id is None:
            mold_id = basename(path)

        if mold_id in self.molds:
            raise KeyError(
                'duplicate mold_id `%s` cannot be registered as mold' %
                mold_id)

        self.verify_path(path)
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

    def export_local_requirejs(self):
        """
        Export the registered molds as local requirejs configuration
        """

        return json.dumps({
            # karma base url
            'baseUrl': '/base',
            # These will be in absolute paths
            # karma.js configuration will need to mark them as provided
            # but not directly included.
            'paths': self.molds,
        })


# Finally, make use of this via the pkg_resources
_entry_points = {}

try:
    from pkg_resources import iter_entry_points
except ImportError:  # pragma: no cover
    logger.error(
        'The `repodono.nunja` registry is disabled as the setuptools package '
        'is missing the `pkg_resources` module'
    )
else:  # pragma: no cover
    # First just dump all the relevant bits from the entry point into
    # the _source dict.
    for ep in iter_entry_points(ENTRY_POINT_NAME):
        _entry_points[ep.name] = ep


# Then create the default registry based on that.
registry = Registry(__name__, _entry_points)
