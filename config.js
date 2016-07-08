/* RequireJS configuration
  */

/* global module:true */

(function() {
    'use strict';

    var requirejsOptions = {
        baseUrl: './',
        optimize: 'none',
        paths: {
            'text': 'node_modules/requirejs-text/text',
            'nunjucks': 'node_modules/nunjucks/browser/nunjucks',
            'repodono.nunja.core': 'src/repodono/nunja/js/core',
            'repodono.nunja.engine': 'src/repodono/nunja/js/engine',
            'repodono.nunja.loader': 'src/repodono/nunja/js/loader',
            'repodono.nunja.registry': 'src/repodono/nunja/js/registry',
        },
        shim: {
        },
        wrapShim: true
    };

    if (typeof exports !== 'undefined' && typeof module !== 'undefined') {
        module.exports = requirejsOptions;
    }
    if (typeof requirejs !== 'undefined' && requirejs.config) {
        requirejs.config(requirejsOptions);
    }

}());
