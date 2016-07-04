define([
    'nunjucks',
    // Note that this MUST be available by the environment.
    'text!_core_/_default_wrapper_/template.jinja',
], function(nunjucks, default_wrapper_str) {
    'use strict';

    var REQ_TMPL_NAME = 'template.jinja';
    var DEFAULT_WRAPPER_NAME = '_core_/_default_wrapper_';

    // TODO figure out how/which/what system to actually use that will
    // make providing pre-compiled templates easier.
    //
    // Ideally, the module will contain everything and the exported
    // attributes will provide the intended rendering and hooks in a
    // consistent manner (i.e. consistently named functions).  However
    // in practice this is difficult to foresee especially at this point
    // of the development cycle.

    var COMPILED_SUFFIX = '.compiled';

    // Create an environment here for specific safe settings as templates
    // are untrusted by default - need safe filter for rendering HTML, so
    // that auditing unsafe usage can be done a bit easier.

    var env = nunjucks.configure({ autoescape: true });

    // Don't quite need all of jQuery but the selector.
    function $(selector, context) {
        return (context || document).querySelectorAll(selector);
    }

    // TODO break this "module" up into the actual bits when this
    // matures a bit, i.e. move engine out of here if needed.
    var engine = {

        // XXX changing these are currently not supported.
        '_core_template_': nunjucks.compile(default_wrapper_str, env),
        '_wrapper_tag_': 'div',

        // global scan function - looks up data-nunja ids and look up
        // the default script, execute it on the afflicted element.
        scan: function (content) {
            var elements = $('[data-nunja]');
            return Array.prototype.slice.call(elements);
        },

        loadTemplateAsync: function(moldId) {
            // this ensures the templates are loaded and compiled and
            // make it available via requirejs.
            var template_id = 'text!' + moldId + '/' + REQ_TMPL_NAME;
            require([template_id], function(templateString) {
                var compiledId = moldId + COMPILED_SUFFIX;
                define(compiledId, nunjucks.compile(templateString, env));
                require([compiledId]);
            });
        },

        loadElement: function(element) {
            /*
            Process this element.  This also ensures the template is
            available at some point.

            Returns the moldID associated with this.
            */

            var moldId = element.attributes.getNamedItem('data-nunja').value;
            if (!requirejs.defined(moldId + COMPILED_SUFFIX)) {
                // XXX we shouldn't repeatedly trigger multiple async
                // calls with the same moldId - need a way to manage
                // this here?
                engine.loadTemplateAsync(moldId);
            }

            return moldId
        },

        initElement: function(element, index, array) {
            /*
            element - The element we want.
            index - passed in by forEach
            array - passed in by forEach
            */
            var moldId = engine.loadElement(element);
            var entry_point = moldId + '/index';
            if (requirejs.defined(entry_point)) {
                var main = require(entry_point);
                main.init(element);
            }
        },

        doOnLoad: function (content) {
            var elements = engine.scan(content);
            elements.forEach(engine.initElement);
        },

        execute: function (moldId, data) {
            /*
            Execute the complete template, which renders a parent block
            enclosing with the template that provides the nunja-data
            attribute.
            */
            var template = require(moldId + COMPILED_SUFFIX);

            var data = data || {};
            // force _nunja_data_ to be consistent with the framework.
            data['_nunja_data_'] = 'data-nunja="' + moldId + '"';
            data['_template_'] = template;
            data['_wrapper_tag_'] = engine._wrapper_tag_;

            var results = engine._core_template_.render(data);

            // XXX this should actually replace the relevant element
            // that triggered this render.
            return results;
            // It should also trigger initElement
        },

        render: function (moldId, data) {
            /*
            Very simple, basic rendering method.
            */
            var template = require(moldId + COMPILED_SUFFIX);
            var results = template.render(data);
            return results;
        }

    };

    return {
        'engine': engine,
    };
});
