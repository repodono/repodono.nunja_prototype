define([
    'repodono.nunja.core',
    // Templates has to be preloaded first to emulate its availability.
    'text!repodono.nunja.testing.mold/basic/template.jinja',
    'text!repodono.nunja.testing.mold/itemlist/template.jinja',
    // also the itemlist entry point
    'repodono.nunja.testing.mold/itemlist/index',
], function(core) {
    'use strict';

    window.mocha.setup('bdd');

    describe('Engine template core rendering', function() {
        beforeEach(function() {
            this.clock = sinon.useFakeTimers();
            this.engine = core.engine;
        });

        afterEach(function() {
            this.clock.restore();
            document.body.innerHTML = "";
        });

        it('Core engine renders the correct template', function() {
            document.body.innerHTML = (
                '<div data-nunja="repodono.nunja.testing.mold/basic"></div>');
            this.engine.doOnLoad(document.body);

            this.clock.tick(500);

            var results = this.engine.render(
                'repodono.nunja.testing.mold/basic', { value: 'Hello User' });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold/basic">\n' +
                '<span>Hello User</span>\n</div>\n'
            )
        });
    });

    describe('Engine main script loading and ui hooks', function() {
        beforeEach(function() {
            this.clock = sinon.useFakeTimers();
            this.engine = core.engine;
            // create new root element to aid cleanup.
            document.body.innerHTML = '<div id="root"></div>';
            this.rootEl = document.body.querySelector('#root');
        });

        afterEach(function() {
            this.clock.restore();
            document.body.innerHTML = "";
        });

        it('Mold index entry point triggered', function() {
            this.rootEl.innerHTML = (
                '<ul data-nunja="repodono.nunja.testing.mold/itemlist"></ul>'
            );
            this.engine.doOnLoad(this.rootEl);
            this.clock.tick(500);

            // Show that the hook fired.
            expect(this.rootEl.classList.contains('nunja-test-itemlist')
                ).to.equal(true);
        });

        it('Basic in-place rendering', function() {
            // Note that this is manual, so formatting is different to
            // final result.
            this.rootEl.innerHTML = (
                '<ul data-nunja="repodono.nunja.testing.mold/itemlist" ' +
                    'id="sample-list">\n' +
                '<li>Test Item</li>\n' +
                '</ul>'
            );
            this.engine.doOnLoad(this.rootEl);
            this.clock.tick(500);

            // now invoke the assigned model to the element and trigger
            // the render
            this.rootEl.querySelector('#sample-list').model.render();
            // should be different to what we assigned originally.
            expect(this.rootEl.innerHTML).to.equal(
                '<ul id="sample-list" ' +
                    'data-nunja="repodono.nunja.testing.mold/itemlist">\n' +
                '\n' +
                '  <li>Test Item</li>\n' +
                '</ul>\n'
            );

        });

        it('Mismatched root tag', function() {
            // I have no idea what the "correct" behavior is, but I am
            // going to define this as able to trigger the load and
            // hook based on the data-nunja identifier.
            this.rootEl.innerHTML = (
                '<div data-nunja="repodono.nunja.testing.mold/itemlist"></div>'
            );
            this.engine.doOnLoad(this.rootEl);
            this.clock.tick(500);

            // now invoke the assigned model to the element and trigger
            // the render - in our case it replaces outerHTML.
            this.rootEl.querySelector('div').model.render();
            // should be different to what we assigned originally.
            expect(this.rootEl.innerHTML).to.equal(
                '<ul id="" ' +
                    'data-nunja="repodono.nunja.testing.mold/itemlist">\n' +
                '\n' +
                '</ul>\n'
            );
        });

        // TODO test with other lists, and hook with events.
        // TODO need a test that has a module that didn't return an
        // index.

    });

});
