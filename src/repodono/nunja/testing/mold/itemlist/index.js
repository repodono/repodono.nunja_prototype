define([
    'repodono.nunja.core',
], function(core) {
    'use strict';

    var Model = function(element) {
        this.element = element;
        var ul = element.querySelector('[id]');
        this.id = ul ? ul.getAttribute('id') : '';
        var items = [];
        // generate pre-rendered data, as this mold does not make its
        // own xhr to source end-point (as no endpoints are defined).
        Array.prototype.slice.call(element.querySelectorAll('li')
            ).forEach(function (e) { items.push(e.textContent)});
        this.items = items;
    };

    Model.prototype.render = function () {
        // This one does not poke to a server, but just reorders the
        // list locally here derived from pre-rendered data.
        core.engine.populate(this.element, {
            list_id: this.id,
            items: this.items,
        });
    };

    var init = function(element) {
        var model = new Model(element);
        var rootEl = element.parentElement;
        // only really for testing purposes.
        rootEl.classList.add('nunja-test-itemlist');
        if (rootEl.querySelector('.reset')) {
            console.log('reset');
        }
        element.model = model;
    };

    // Thought: core.render should in theory be able to render _any_
    // templates that it knows - could simply define multiple molds and
    // only call the limited internal ones.

    // Now how does this fit together with other JS frameworks (like
    // backbone)?  I have no idea yet.

    return {
        'init': init
    };
});
