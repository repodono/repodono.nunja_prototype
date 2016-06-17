define([
    'nunjucks',
    'text!repodono.nunja.testing.mold.basic/template.jinja'
], function(nunjucks, basic_template) {
    'use strict';

    window.mocha.setup('bdd');

    describe('Core functionality sanity checks', function() {
        beforeEach(function() {
            nunjucks.configure({ autoescape: true });
        });

        afterEach(function() {
        });

        it('String rendering', function() {
            var results = nunjucks.renderString('Hello {{ username }}', {
                username: 'User'
            });
            expect(results).to.equal('Hello User');
        });

        it('Basic Template Rendering', function() {
            var results = nunjucks.renderString(basic_template, {
                'value': 'Hello World!',
                // note this is manually injected here for testing reasons.
                // XXX figure out how to compile this so _nunja_data_ is added
                '_nunja_data_':
                    'data-nunja="repodono.nunja.testing.mold.basic"'
            });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold.basic">\n' +
                '<span>Hello World!</span>\n</div>\n'
            )
        });

        it('Basic Template Rendering, XSS filtering', function() {
            var results = nunjucks.renderString(basic_template, {
                'value': '<xss>',
                '_nunja_data_':
                    'data-nunja="repodono.nunja.testing.mold.basic"'
            });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold.basic">\n' +
                '<span>&lt;xss&gt;</span>\n</div>\n'
            )
        });

        it('Template compiling', function() {
            var template = nunjucks.compile(basic_template);
            template.compile()
            var results = template.render({
                'value': 'parameters',
                '_nunja_data_':
                    'data-nunja="repodono.nunja.testing.mold.basic"'
            });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.testing.mold.basic">\n' +
                '<span>parameters</span>\n</div>\n'
            )
        });

    });
});
