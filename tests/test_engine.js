define([
    'repodono.nunja.core',
], function(core) {
    'use strict';

    window.mocha.setup('bdd');

    describe('Test template rendering', function() {
        beforeEach(function() {
            this.clock = sinon.useFakeTimers();
            this.engine = core.engine;
        });

        afterEach(function() {
            this.clock.restore();
            document.body.innerHTML = "";
        });

        it('Core engine test', function() {
            document.body.innerHTML = (
                '<div data-nunja="repodono.nunja.testing.mold.basic"></div>');
            this.engine.doOnLoad(document.body);

            this.clock.tick(500);

            var results = this.engine.render(
                'repodono.nunja.testing.mold.basic', { value: 'Hello User' });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold.basic">\n' +
                '<span>Hello User</span>\n</div>\n'
            )
        });

    });
});
