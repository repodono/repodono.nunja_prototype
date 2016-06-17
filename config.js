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
