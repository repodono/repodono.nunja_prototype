define([
    'nunjucks',
    'text!repodono.nunja.molds/table/template.jinja'
], function(nunjucks, basic_template) {
    'use strict';

    window.mocha.setup('bdd');

    describe('Core functionality sanity checks', function() {
        beforeEach(function() {
            nunjucks.configure({ autoescape: true });
        });

        afterEach(function() {
        });

        it('Null rendering', function() {
            var results = nunjucks.renderString(basic_template, {
                '_nunja_data_':
                    'data-nunja="repodono.nunja.molds/table"',

                'active_columns': [],
                'column_map': {},
                'data': [],
                'css': {},

            });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.molds/table">\n' +
                '<table class="">\n  <thead>\n' +
                '    <tr class="">\n' +
                '    \n' +
                '    </tr>\n' +
                '  </thead>\n' +
                '  <tbody>\n' +
                '    \n' +
                '  </tbody>\n' +
                '</table>\n' +
                '</div>\n'
            )
        });

        it('Basic data rendering', function() {
            var template = nunjucks.compile(basic_template);
            template.compile()
            var results = template.render({
                '_nunja_data_':
                    'data-nunja="repodono.nunja.molds/table"',

                'active_columns': ['id', 'name'],
                'column_map': {
                    'id': 'Id',
                    'name': 'Given Name',
                },
                'data': [
                    {'id': '1', 'name': 'John Smith'},
                    {'id': '2', 'name': 'Eve Adams'},
                ],
                'css': {},

            });
            expect(results).to.equal(
                '<div data-nunja="repodono.nunja.molds/table">\n' +
                '<table class="">\n' +
                '  <thead>\n' +
                '    <tr class="">\n' +
                '    <td>Id</td><td>Given Name</td>\n' +
                '    </tr>\n' +
                '  </thead>\n' +
                '  <tbody>\n' +
                '    <tr class="">\n' +
                '      <td>1</td><td>John Smith</td>\n' +
                '    </tr><tr class="">\n' +
                '      <td>2</td><td>Eve Adams</td>\n' +
                '    </tr>\n' +
                '  </tbody>\n' +
                '</table>\n' +
                '</div>\n'
            )
        });

    });
});
