define([
  'nunjucks',
  'text!repodono.nunja.testing.mold.basic/template.jinja'
], function(nunjucks, basic_template) {
  'use strict';

  window.mocha.setup('bdd');
  //$.fx.off = true;

  describe('Test template', function() {
    beforeEach(function() {
      nunjucks.configure({ autoescape: true });
    });

    afterEach(function() {
    });

    it('Dummy test', function() {
      var results = nunjucks.renderString(
          'Hello {{ username }}', { username: 'User' });
      expect(results).to.equal('Hello User');
    });

    it('Basic Template Rendering', function() {
      var results = nunjucks.renderString(basic_template, {
        'value': 'Hello World!',
        // note this is manually injected here for testing reasons.
        // XXX figure out how to compile this so _nunja_data_ is added
        '_nunja_data_': 'data-nunja="repodono.nunja.testing.mold.basic"'
      });
      expect(results).to.equal(
        '<div data-nunja="repodono.nunja.testing.mold.basic">\n' +
        '<span>Hello World!</span>\n</div>\n'
      )
    });

    it('Basic Template Rendering', function() {
      var results = nunjucks.renderString(basic_template, {
        'value': '<xss>',
        '_nunja_data_': 'data-nunja="repodono.nunja.testing.mold.basic"'
      });
      expect(results).to.equal(
        '<div data-nunja="repodono.nunja.testing.mold.basic">\n' +
        '<span>&lt;xss&gt;</span>\n</div>\n'
      )
    });

  });
});
