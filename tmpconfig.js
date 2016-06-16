requirejs.config({
  // Karma serves files from '/base'
  baseUrl: '/base',

  // ask Require.js to load these files (all our tests)
  deps: tests,

  paths: {
    'repodono.nunja.testing.mold.basic': 'src/repodono/nunja/testing/mold/basic'
  }

});

window.DEBUG = true;
