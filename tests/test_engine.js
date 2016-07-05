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
            expect(results).to.equal('<span>Hello User</span>\n');
        });

        it('Core engine executes the correct template', function() {
            document.body.innerHTML = (
                '<div data-nunja="repodono.nunja.testing.mold/basic"></div>');
            this.engine.doOnLoad(document.body);

            this.clock.tick(500);

            var results = this.engine.execute(
                'repodono.nunja.testing.mold/basic', { value: 'Hello User' });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold/basic">\n' +
                '<span>Hello User</span>\n\n</div>\n'
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
            document.body.innerHTML = "";
            this.clock.restore();
        });

        it('Mold index entry point triggered', function() {
            this.rootEl.innerHTML = (
                '<div data-nunja="repodono.nunja.testing.mold/itemlist"></div>'
            );
            this.engine.doOnLoad(document.body);
            this.clock.tick(500);

            // Show that the hook fired as model was set.
            var element = this.rootEl.querySelector('div');
            expect(element).to.equal(element.model.element);
        });

        it('Basic in-place rendering', function() {
            // Note that this is manual, so formatting is different to
            // final result.
            this.rootEl.innerHTML = (
                '<div data-nunja="repodono.nunja.testing.mold/itemlist">' +
                '<ul id="sample-list">\n' +
                '<li>Test Item</li>\n' +
                '</ul>\n' +
                '</div>'
            );
            this.engine.doOnLoad(document.body);
            this.clock.tick(500);

            // now invoke the assigned model to the element and trigger
            // the render
            this.rootEl.querySelector('div').model.render();
            // should be different to what we assigned originally.
            expect(this.rootEl.innerHTML).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold/itemlist">' +
                '<ul id="sample-list">\n' +
                '\n' +
                '  <li>Test Item</li>\n' +
                '</ul>\n' +
                '</div>'
            );

        });

        it('Pure JS in-place rendering', function() {
            // Server would have only provided just the skeleton tag
            this.rootEl.innerHTML = (
                '<div data-nunja="repodono.nunja.testing.mold/itemlist"></div>'
            );
            this.engine.doOnLoad(document.body);
            this.clock.tick(500);

            // The model would have been assigned; in alternative
            // implementations it could very well do the render in its
            // init, but here we trigger this manually to populate the
            // node with the empty list.
            this.rootEl.querySelector('div').model.render();
            expect(this.rootEl.innerHTML).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold/itemlist">' +
                '<ul id="">\n' +
                '\n' +
                '</ul>\n' +
                '</div>'
            );
        });

        it('Event hooking onto parent/siblings of nunja node', function() {
            this.rootEl.innerHTML = (
                '<button class="reset">Reset</button>\n' +
                '<div data-nunja="repodono.nunja.testing.mold/itemlist">' +
                '<ul id="sample">\n' +
                '</ul>\n' +
                '</div>'
            );
            this.engine.doOnLoad(document.body);
            this.clock.tick(500);
            this.rootEl.querySelector('div').model.items = [
                'Manual 1', 'Manual 2'];
            this.rootEl.querySelector('.reset').click();
            expect(this.rootEl.querySelector('#sample').innerHTML).to.equal(
                '\n\n' +
                '  <li>Manual 1</li>\n' +
                '  <li>Manual 2</li>\n'
            );
        });

        it('Event hooking and rehooking within nunja node', function() {
            this.rootEl.innerHTML = (
                '<button class="reset">Reset</button>\n' +
                '<div data-nunja="repodono.nunja.testing.mold/itemlist">' +
                '<ul id="sample">\n' +
                '<li>Item 1</li>\n' +
                '<li>Item 2</li>\n' +
                '<li>Item 3</li>\n' +
                '<li>Item 4</li>\n' +
                '<li>Item 5</li>\n' +
                '<li>Item 6</li>\n' +
                '</ul>\n' +
                '</div>'
            );
            this.engine.doOnLoad(document.body);
            this.clock.tick(500);

            var model = this.rootEl.querySelector('div').model;
            // remove first item
            this.rootEl.querySelectorAll('#sample li')[2].click();
            expect(this.rootEl.querySelector('#sample').innerHTML).to.equal(
                '\n' +
                '<li>Item 1</li>\n' +
                '<li>Item 2</li>\n' +
                '\n' +
                '<li>Item 4</li>\n' +
                '<li>Item 5</li>\n' +
                '<li>Item 6</li>\n'
            );
            expect(model.removeCount).to.equal(1);

            this.rootEl.querySelector('.reset').click();
            // restored to 6 elements and reset count be 1.
            expect(model.resetCount).to.equal(1);
            expect(this.rootEl.querySelectorAll('#sample li').length).to.equal(
                6);

            // event still hooked back into this re-rendered list.
            this.rootEl.querySelectorAll('#sample li')[4].click();
            // rendering now derived from template not hardcoded values.
            expect(this.rootEl.querySelector('#sample').innerHTML).to.equal(
                '\n\n' +
                '  <li>Item 1</li>\n' +
                '  <li>Item 2</li>\n' +
                '  <li>Item 3</li>\n' +
                '  <li>Item 4</li>\n' +
                '  \n' +
                '  <li>Item 6</li>\n'
            );

            // This should only increase by one, no double events.
            expect(model.removeCount).to.equal(2);

        });

    });

});
