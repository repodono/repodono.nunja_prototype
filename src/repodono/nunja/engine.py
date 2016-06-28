from os.path import basename
from os.path import join

from jinja2 import Template
from jinja2 import Environment

from repodono.nunja.registry import registry as default_registry

jinja = Environment(autoescape=True)


class Renderer(object):

    def __init__(self, name, template_str):
        # TODO normalize the name to the same system that the underlying
        # node/javascript framework understands.  Build a system of sort
        # to achieve this.
        self.name = name
        self.template = jinja.from_string(template_str)

    def __call__(self, data):
        # TODO i18n considerations, where the `_t` is a callable
        # that provides gettext functionality.
        nunja_data = 'data-nunja="%s"' % self.name
        return self.template.render(_nunja_data_=nunja_data, **data)


class Engine(object):

    def __init__(self, registry=default_registry):
        self.registry = registry
        self._renderer_cache = {}

    def execute(self, name, data):
        """
        Execute a mold with data provided as dict
        """

        # TODO cache invalidation
        if name not in self._renderer_cache:
            path = self.registry.lookup_path(name)
            with open(join(path, 'template.jinja')) as fd:
                tmpl = fd.read()
                self._renderer_cache[name] = renderer = Renderer(name, tmpl)
        else:
            renderer = self._renderer_cache[name]

        return renderer(data)
