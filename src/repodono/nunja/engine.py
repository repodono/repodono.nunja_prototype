# -*- coding: utf-8 -*-
from os.path import join

from jinja2 import Environment

from repodono.nunja.registry import registry as default_registry
from repodono.nunja.registry import REQ_TMPL_NAME
from repodono.nunja.registry import DEFAULT_WRAPPER_NAME

jinja = Environment(autoescape=True)


class Engine(object):
    """
    Nunja core engine

    This takes a nunja mold registry and is able to execute the
    rendering of templates through nunja identifiers.
    """

    def __init__(
            self, registry=default_registry,
            _wrapper_name=DEFAULT_WRAPPER_NAME,
            _required_template_name=REQ_TMPL_NAME,
            ):
        """
        By default, the engine can be created without arguments which
        will initialize using the default registry.

        It is possible to initialize using other arguments, but this is
        unsupported by the main system, and only useful for certain
        specialized implementations.
        """

        self.registry = registry
        self._template_cache = {}
        self._required_template_name = _required_template_name

        self._core_template_ = self.load_template(_wrapper_name)

    def load_template(self, name):
        """
        Load/cache the template identified by the template name as found
        in the registry
        """

        # TODO cache invalidation
        if name not in self._template_cache:
            path = self.registry.lookup_path(name)
            with open(join(path, self._required_template_name)) as fd:
                tstr = fd.read()
                self._template_cache[name] = template = jinja.from_string(tstr)
        else:
            template = self._template_cache[name]

        return template

    def execute(self, name, data, wrapper_tag='div'):
        """
        Execute a mold with data provided as dict using template
        identified by the template name as found in the registry.

        This returns the wrapped content.
        """

        template = self.load_template(name)

        kwargs = {}
        kwargs.update(data)
        kwargs['_nunja_data_'] = 'data-nunja="%s"' % name
        kwargs['_template_'] = template
        kwargs['_wrapper_tag_'] = wrapper_tag

        return self._core_template_.render(**kwargs)
