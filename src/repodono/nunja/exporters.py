# -*- coding: utf-8 -*-
from repodono.nunja.registry import registry

umd_requirejs_tmpl = """\
(function() {
    'use strict';

    var requirejsOptions = %s;

    if (typeof exports !== 'undefined' && typeof module !== 'undefined') {
        module.exports = requirejsOptions;
    }
    if (typeof requirejs !== 'undefined' && requirejs.config) {
        requirejs.config(requirejsOptions);
    }

}());
"""


def export_umd():
    return (umd_requirejs_tmpl % registry.export_nunja_requirejs_json())
