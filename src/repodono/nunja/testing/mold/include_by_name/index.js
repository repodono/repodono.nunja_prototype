define([
    'repodono.nunja.core',
], function(core) {
    'use strict';

    var Model = function(element) {
        // have to assume this was already prepared.
        this.element = element;
        this.itemlists = [];
    };

    Model.prototype.render = function (list_id) {
        // This one does not poke to a server, but just reorders the
        // list locally here derived from pre-rendered data.
        core.engine.populate(this.element, {
            'itemlists': this.itemlists,
            'list_id': list_id ? list_id : '',
        });
    };

    var init = function(element) {
        // to basically provide a render method reachable from element.
        var model = new Model(element);
        element.model = model;
    };

    return {
        'init': init
    };
});
