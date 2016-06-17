/* RequireJS configuration */

/* global module:true */

(function() {
    'use strict';

    var requirejsOptions = {
        baseUrl: './',
        optimize: 'none',

        paths: {
            // dependencies
            'text': 'node_modules/require-text/text',
            'nunjucks': 'node_modules/nunjucks/browser/nunjucks',
            // our application
            'repodononunja-url': 'src/repodono/nunja/js'
        },

        shim: {
            'nunjucks': { exports: 'nunjucks' }
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
