# -*- coding: utf-8 -*-
from os.path import join

from jinja2 import Environment

from repodono.nunja.registry import registry as default_registry
from repodono.nunja.registry import REQ_TMPL_NAME
from repodono.nunja.registry import DEFAULT_WRAPPER_NAME
from repodono.nunja.loader import NunjaLoader


class Engine(object):
    """
    Nunja core engine

    This takes a nunja mold registry and is able to execute the
    rendering of templates through nunja identifiers.
    """

    def __init__(
            self,
            registry=default_registry,
            env=None,
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
        self.env = env if env else Environment(
            autoescape=True,
            loader=NunjaLoader(registry)
        )
        self._required_template_name = _required_template_name

        self._core_template_ = self.load_mold(_wrapper_name)

    def lookup_path(self, name):
        """
        Lookup the path of the underlying resource identified by name
        through the loader.
        """

        return self.registry.verify_path(name)

    def load_template(self, name):
        """
        Load the template identified by name as found in the registry.
        """

        return self.env.get_template(name)

    def load_mold(self, mold_id):
        """
        Load the default, required template from the mold `mold_id`.
        """

        return self.load_template(join(mold_id, self._required_template_name))

    def execute(self, mold_id, data, wrapper_tag='div'):
        """
        Execute a mold `mold_id` by rendering through ``env``.

        This is done using its default template, with data provided as
        dict.

        This returns the wrapped content.
        """

        template = self.load_mold(mold_id)

        kwargs = {}
        kwargs.update(data)
        kwargs['_nunja_data_'] = 'data-nunja="%s"' % mold_id
        kwargs['_template_'] = template
        kwargs['_wrapper_tag_'] = wrapper_tag

        return self._core_template_.render(**kwargs)
