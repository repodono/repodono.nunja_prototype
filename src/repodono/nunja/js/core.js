define([
    'repodono.nunja.engine',
    // As we are using the default identifier, this is provided here
    // to bootstrap the construction of the default engine using default
    // arguments.
    'text!_core_/_default_wrapper_/template.jinja',
], function(engine, default_wrapper_str) {
    'use strict';

    return {
        'engine': new engine.Engine({}),
    };
});
