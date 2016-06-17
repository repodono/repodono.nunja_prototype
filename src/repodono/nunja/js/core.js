define([
    'nunjucks',
], function(nunjucks) {
    'use strict';

    var REQ_TMPL_NAME = 'template.jinja';

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

    var loadTemplateAsync = function(moldId) {
        // this ensures the templates are loaded and compiled and
        // make it available via requirejs.
        var target = 'text!' + moldId + '/' + REQ_TMPL_NAME;
        require([target], function(templateString) {
            var compiledId = moldId + COMPILED_SUFFIX;
            define(compiledId, nunjucks.compile(templateString, env));
            require([compiledId]);
        });
    };

    // TODO break this "module" up into the actual bits when this
    // matures a bit, i.e. move engine out of here if needed.
    var engine = {
        // global scan function - looks up data-nunja ids and look up
        // the default script, execute it on the afflicted element.
        scan: function (content) {
            var elements = $('[data-nunja]');
            return Array.prototype.slice.call(elements);
        },

        loadElement: function(element, index, array) {
            var moldId = element.attributes.getNamedItem('data-nunja').value;
            if (requirejs.defined(moldId + COMPILED_SUFFIX)) {
                // XXX we shouldn't repeatedly trigger multiple async
                // calls with the same moldId - need a way to manage
                // this here?
                return;
            }

            loadTemplateAsync(moldId);
        },

        doOnLoad: function (content) {
            var elements = this.scan(content);
            elements.forEach(this.loadElement);
        },

        render: function (moldId, data) {
            var template = require(moldId + COMPILED_SUFFIX);

            // XXX data need to be defined somehow as an endpoint.
            // TODO explore the idea of standardized function names for
            // passing in the data() block associated with the activated
            // element, or extracting the href and calling that using
            // async json loading.

            var data = data || {};
            // force _nunja_data_ to be consistent with the framework.
            data['_nunja_data_'] = 'data-nunja="' + moldId + '"';

            var results = template.render(data);

            // XXX this should actually replace the relevant element
            // that triggered this render.
            return results;
        }

    };

    return {
        'engine': engine,
    };
});
