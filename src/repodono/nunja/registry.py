from os import listdir
from os.path import basename
from os.path import exists
from os.path import isdir
from os.path import join
from logging import getLogger
from types import ModuleType

from jinja2 import Template

from .exc import TemplateNotFoundError

REQ_TMPL_NAME = 'template.jinja'

logger = getLogger(__name__)


class Registry(object):

    def __init__(self, name):
        self.name = name
        self.molds = {}

    def register_mold(self, path, name=None):
        """
        Register the path as a usable mold.

        If name is not provided, default to the basename of the dir.
        """

        if name is None:
            name = basename(path)

        if name in self.molds:
            raise KeyError(
                'duplicate name `%s` cannot be registered as mold' % name)

        if not exists(join(path, REQ_TMPL_NAME)):
            raise TemplateNotFoundError(
                'required template not found at `%s`' % path)

        self.molds[name] = path

    def register_module(self, module, subdir=None):
        """
        Register all subdirectories at the path of the specified module.

        All errors will be logged.

        Arguments

        module
            The Python module to search for the molds.
        subdir
            The subdirectory within the target module that contains all
            the molds to be registered.
        """

        if not isinstance(module, ModuleType):
            logger.warning('%s is not a module', module)
            return False

        paths = module.__path__
        count = 0

        for path in paths:
            if subdir:
                path = join(path, subdir)

            prefix = '.'.join(m for m in (module.__name__, subdir) if m)

            if not isdir(path):
                continue

            for target in listdir(path):
                target_path = join(path, target)
                if not isdir(target_path):
                    continue

                name = prefix + '/' + target

                try:
                    self.register_mold(target_path, name=name)
                except TemplateNotFoundError:
                    logger.debug(
                        '%s missing required %s', target_path, REQ_TMPL_NAME)
                except KeyError:
                    logger.warning(
                        '%s already registered to %s', name, self.name)
                else:
                    count += 1

registry = Registry(__name__)
