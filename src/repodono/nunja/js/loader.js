define([
    'nunjucks',
], function(nunjucks) {
    'use strict';

    var NunjaLoader = function(registry, async) {
        this.registry = registry;
        // TODO figure out consequences of both these flags and best
        // settings for them.
        this.async = (async === true);
        this.noCache = true;
    };

    NunjaLoader.prototype.getSource = function(name, callback) {
        var self = this;
        var template_path = self.registry.lookup_path(name);

        if (this.async) {
            require([template_path], function(template_str) {
                callback(null, {
                    'src': template_str,
                    'path': name,
                    'noCache': self.noCache,
                });
            });
        }
        else {
            return {
                'src': require('text!' + name),
                'path': name,
                'noCache': self.noCache,
            }
        }
    };

    return {
        'NunjaLoader': NunjaLoader,
    };

});
