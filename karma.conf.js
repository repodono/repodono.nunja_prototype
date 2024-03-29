module.exports = function(config) {
    config.set({

        // base path, that will be used to resolve files and exclude
        basePath: './',

        // frameworks to use
        frameworks: ['mocha', 'requirejs', 'chai', 'expect', 'sinon'],

        // list of files / patterns to load in the browser
        files: [

            /*
            * include initial framework (mocha and requirejs) with html5
            * shims/shams/polyfills
            */
            'node_modules/requirejs/require.js',
            'node_modules/mocha/mocha.js',
            'node_modules/karma-mocha/lib/adapter.js',
            'node_modules/karma-requirejs/lib/adapter.js',

            // The compiled JavaScript library for repodono.nunja
            'repodono.nunja.js',

            /*
            * include requirejs configuration
            */
            'tests/config.js',
            'nunja.generated.js',

            /* provide but not include */

            {pattern: 'node_modules/requirejs-text/text.js', included: false},
            {pattern: 'node_modules/nunjucks/browser/nunjucks.js', included: false},

            {pattern: 'tests/**/*.js', included: false},
            {pattern: 'src/repodono/nunja/molds/**', included: false},
            {pattern: 'src/repodono/nunja/_core_/**', included: false},
            {pattern: 'src/repodono/nunja/js/*.js', included: false},
            {pattern: 'src/repodono/nunja/testing/**/*', included: false},
        ],

        // list of files to exclude
        exclude: [
        ],

        // test results reporter to use
        reporters: ['spec', 'progress'],

        // web server port
        port: 9876,

        // enable / disable colors in the output (reporters and logs)
        colors: true,

        // level of logging
        logLevel: config.LOG_INFO,

        // Start these browsers
        browsers: ['PhantomJS'],

        // If browser does not capture in given timeout [ms], kill it
        captureTimeout: 60000,

        // Continuous Integration mode
        // if true, it capture browsers, run tests and exit
        singleRun: true,

        plugins: [
            'karma-mocha',
            'karma-chai',
            'karma-coverage',
            'karma-requirejs',
            'karma-expect',
            'karma-sauce-launcher',
            'karma-chrome-launcher',
            'karma-phantomjs-launcher',
            'karma-junit-reporter',
            'karma-spec-reporter',
            'karma-sinon',
        ],

        /*  Maybe figure out how to integrate external data provider
            sourced via reversed proxy for better integration tests.
        proxies: {
            '/mock': 'http://127.0.0.1/'
        },
        */

    });
};
