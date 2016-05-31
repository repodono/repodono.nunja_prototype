/* RequireJS configuration
 */

/* global module:true */

(function() {
  'use strict';

  var requirejsOptions = {
    baseUrl: './',
    optimize: 'none',
    paths: {
      'nunjucks': 'node_modules/nunjucks/browser/nunjucks',
      // test dependencies
      'expect': 'bower_components/expect/index',
      // our application
      'repodononunja-url': 'src/repodono/nunja/js'
    },
    shim: {
      'expect': { exports: 'window.expect' },
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
