from os.path import basename
from os.path import join

from jinja2 import Template


class Renderer(object):

    def __init__(self, name, template_str):
        # TODO normalize the name to the same system that the underlying
        # node/javascript framework understands.  Build a system of sort
        # to achieve this.
        self.name = name
        self.template = Template(template_str)

    def __call__(self, data):
        nunja_data = 'data-nunja="%s"' % self.name
        return self.template.render(_nunja_data_=nunja_data, **data)


class Engine(object):

    def __init__(self):
        self.molds = {}
        self._renderer_cache = {}

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

        self.molds[name] = path

    def execute(self, name, data):
        """
        Execute a mold with data provided as dict
        """

        # TODO cache invalidation
        if name not in self._renderer_cache:
            path = self.molds[name]
            with open(join(path, 'template.jinja')) as fd:
                tmpl = fd.read()
                self._renderer_cache[name] = renderer = Renderer(name, tmpl)
        else:
            renderer = self._renderer_cache[name]

        return renderer(data)
