define([
  'nunjucks',
  'text!repodono.nunja.testing.mold.basic/template.jinja'
], function(nunjucks, basic_template) {
  'use strict';

  window.mocha.setup('bdd');
  //$.fx.off = true;

  describe('Test template', function() {
    beforeEach(function() {
    });

    afterEach(function() {
    });

    it('Dummy test', function() {
      nunjucks.configure({ autoescape: true });
      var results = nunjucks.renderString(
          'Hello {{ username }}', { username: 'User' });
      expect(results).to.equal('Hello User');
    });

    it('Basic Template Rendering', function() {
      // XXX figure out how to compile this so _nunja_data_ is added
      nunjucks.configure({ autoescape: false });
      var results = nunjucks.renderString(basic_template, {
        'value': 'Hello World!',
        // note this is manually injected here for testing reasons.
        '_nunja_data_': 'data-nunja="repodono.nunja.testing.mold.basic"'
      });
      expect(results).to.equal(
        '<div data-nunja="repodono.nunja.testing.mold.basic">\n' +
        '<span>Hello World!</span>\n</div>\n'
      )
    });

  });
});
