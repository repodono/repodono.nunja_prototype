define([
    'nunjucks',
], function(nunjucks) {
    'use strict';

    var default_kwargs = {
        '_required_template_name': 'template.jinja',
        '_wrapper_name': '_core_/_default_wrapper_',
        '_wrapper_tag_': 'div',
    };

    // TODO figure out how/which/what system to actually use that will
    // make providing pre-compiled templates easier.
    //
    // Ideally, the module will contain everything and the exported
    // attributes will provide the intended rendering and hooks in a
    // consistent manner (i.e. consistently named functions).  However
    // in practice this is difficult to foresee especially at this point
    // of the development cycle.  So we are just going to use a suffix
    // and register that into requirejs for the mean time.

    var COMPILED_SUFFIX = '.compiled';

    // Create an environment here for specific safe settings as templates
    // are untrusted by default - need safe filter for rendering HTML, so
    // that auditing unsafe usage can be done a bit easier.

    var env = nunjucks.configure({ autoescape: true });

    // Don't quite need all of jQuery but the selector.
    function $(selector, context) {
        return (context || document).querySelectorAll(selector);
    }

    var Engine = function(kwargs) {
        var self = this;
        for (var key in default_kwargs) {
            self[key] = kwargs[key] || default_kwargs[key];
        }

        var wrapper_str = require(self.to_template_id(self._wrapper_name));
        self.load_template_async(self._wrapper_name, function (tmpl) {
            self['_core_template_'] = tmpl;
        });
    };

    Engine.prototype.to_template_id = function(mold_id) {
        return 'text!' + mold_id + '/' + this._required_template_name;
    };

    Engine.prototype.to_compiled_id = function(mold_id) {
        return mold_id + COMPILED_SUFFIX;
    };

    // global scan function - looks up data-nunja ids and look up
    // the default script, execute it on the afflicted element.
    Engine.prototype.scan = function (content) {
        var elements = $('[data-nunja]');
        return Array.prototype.slice.call(elements);
    };

    Engine.prototype.load_template = function (mold_id) {
        /*
        This requires the template to have been compiled already and
        be provided through requirejs.
        */
        return require(this.to_compiled_id(mold_id));
    };

    Engine.prototype.load_template_async = function(mold_id, callback) {
        /*
        This ensures the templates are loaded and compiled and make it
        available through requirejs.

        A callback can be optionally supplied which will be triggered
        when the compiled template becomes available through requirejs.

        Do note that there are no checks against multiple calls before
        the define step was completed.
        */

        var do_callback = callback || function(dummy) {};
        var compiled_mold_id = this.to_compiled_id(mold_id);

        if (requirejs.defined(compiled_mold_id)) {
            require([compiled_mold_id], do_callback)
        }

        var template_id = this.to_template_id(mold_id);

        require([template_id], function(template_str) {
            var compiled = nunjucks.compile(template_str, env);
            define(compiled_mold_id, compiled);
            // plug that into the requirejs framework
            require([compiled_mold_id]);
            do_callback(compiled);
        });
    };

    Engine.prototype.load_element = function(element) {
        /*
        Process this element.  This also ensures the template is
        available at some point.

        Returns the moldID associated with this.
        */

        var mold_id = element.attributes.getNamedItem('data-nunja').value;
        this.load_template_async(mold_id);
        return mold_id;
    };

    Engine.prototype.init_element = function(element) {
        /*
        This should only be called once ever per element.

        element - The element we want.
        */
        var mold_id = this.load_element(element);
        var entry_point = mold_id + '/index';
        if (requirejs.defined(entry_point)) {
            var main = require(entry_point);
            main.init(element);
        }
    };

    Engine.prototype.do_onload = function (content) {
        var elements = this.scan(content);
        var self = this;
        elements.forEach(function (element, index, array) {
            self.init_element(element);
        });
    },

    Engine.prototype.execute = function (mold_id, data) {
        /*
        Execute the complete template, which renders a parent block
        enclosing with the template that provides the nunja-data
        attribute.
        */
        var template = require(this.to_compiled_id(mold_id));

        var data = data || {};
        // force _nunja_data_ to be consistent with the framework.
        data['_nunja_data_'] = 'data-nunja="' + mold_id + '"';
        data['_template_'] = template;
        data['_wrapper_tag_'] = this._wrapper_tag_;

        var results = this._core_template_.render(data);

        return results;
    };

    Engine.prototype.populate = function (element, data) {
        /*
        Populate the element that contains a data-nunja identifier
        with the data involved.
        */
        var mold_id = element.getAttribute('data-nunja');
        element.innerHTML = this.render(mold_id, data)
    };

    Engine.prototype.render = function (mold_id, data) {
        /*
        Very simple, basic rendering method.
        */
        var template = require(mold_id + COMPILED_SUFFIX);
        var results = template.render(data);
        return results;
    };

    return {
        'Engine': Engine,
    };

});
