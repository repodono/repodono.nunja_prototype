# -*- coding: utf-8 -*-
from os.path import getmtime
from os.path import exists

from jinja2.loaders import BaseLoader
from jinja2.loaders import TemplateNotFound


def uptodate_checker(filename):
    mtime = getmtime(filename)
    def checker():
        try:
            return getmtime(filename) == mtime
        except OSError:
            return False
    return checker


class NunjaLoader(BaseLoader):

    def __init__(self, registry):
        self.registry = registry

    def get_source(self, environment, template):
        try:
            path = self.registry.lookup_path(template)
        except KeyError:
            raise TemplateNotFound(template)

        if not exists(path):
            raise TemplateNotFound(template)

        mtime = getmtime(path)
        with file(path) as f:
            source = f.read().decode('utf-8')
        return source, path, uptodate_checker(path)

