define([
  'expect',
  'nunjucks',
], function(expect, nunjucks) {
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

  });
});
