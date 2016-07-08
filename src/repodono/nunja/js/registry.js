define([
    'nunjucks',
], function(nunjucks) {
    'use strict';
    /*
    This is just to facilitate lookup, a module that provides certain
    common default values for the system.
    */

    var REQ_TMPL_NAME = 'template.jinja';
    var ENTRY_POINT_NAME = 'repodono.nunja.mold';
    var DEFAULT_WRAPPER_NAME = '_core_/_default_wrapper_'
    var DEFAULT_WRAPPER_TAG = 'div'

    var Registry = function() {
    };

    Registry.prototype.lookup_path = function(mold_id_path) {
        return 'text!' + mold_id_path;
    };

    return {
        'Registry': Registry,
        'DEFAULT_WRAPPER_NAME': DEFAULT_WRAPPER_NAME,
        'DEFAULT_WRAPPER_TAG': DEFAULT_WRAPPER_TAG,
    };

});
