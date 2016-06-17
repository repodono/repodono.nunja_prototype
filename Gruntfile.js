module.exports = function(grunt) {
    'use strict';

    var fs = require('fs');
    var nunjaRequireJSOptions = require('./config');

    grunt.initConfig({
        karma: {
            test: {
                configFile: 'karma.conf.js'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-karma');
    grunt.registerTask('test', ['karma:test']);
}

