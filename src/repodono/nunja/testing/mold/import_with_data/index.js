define([
    'repodono.nunja.core',
], function(core) {
    'use strict';

    var Model = function(element) {
        // have to assume this was already prepared.
        this.element = element;
        this.itemlists = [];
        // Prepare by loading the compiled template here.
        this.list_template = core.engine.load_template(
            'repodono.nunja.testing.mold/itemlist');
    };

    Model.prototype.render = function () {
        // This one does not poke to a server, but just reorders the
        // list locally here derived from pre-rendered data.
        core.engine.populate(this.element, {
            list_template: this.list_template,
            itemlists: this.itemlists,
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
