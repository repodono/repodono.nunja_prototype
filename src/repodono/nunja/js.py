# -*- coding: utf-8 -*-
"""
This provides a JavaScript "toolchain".

When I have a hammer every problem starts to look like JavaScript.

Honestly, it's a bit easier to deal with JavaScript when one treats that
as a compilation target.

How this works?

1) Write raw JS code without any UMD wrappers, but treat everything in
the file as UMD.  Remember to import everything needed using ``require``
and declare the exported things by assigning it to ``exports``.
2) Leave that file somewhere in the src directory, along with Python
code.
3) Run compile.  They will be compiled into the corresponding thing that
correlates to the Pythonic namespace identifiers.

At least this is the idea, have to see whether this idea actually end up
being sane (it won't be sane, when the entire thing was insane to begin
with).
"""

import tempfile
import codecs
import json
import logging
import shutil
from os import makedirs
from os.path import join
from os.path import exists
from os.path import isfile
from os.path import isdir
from subprocess import call
from subprocess import Popen
from subprocess import PIPE

from repodono.nunja.registry import registry

logger = logging.getLogger(__name__)

base_requirejs_config = {
    'paths': {},
    'shim': {},

    'wrapShim': True,

    # other configuration options
    'optimize': "none",
    'generateSourceMaps': False,
    'normalizeDirDefines': "skip",
    'uglify': {
        'toplevel': True,
        'ascii_only': True,
        'beautify': True,
        'max_line_length': 1000,
        'defines': {
            'DEBUG': ['name', 'false']
        },
        'no_mangle': True
    },
    'uglify2': {
        'output': {
            'beautify': True
        },
        'compress': {
            'sequences': False,
            'global_defs': {
                'DEBUG': False
            }
        },
        'warnings': True,
        'mangle': False
    },
    'useStrict': True,
    'wrap': True,
    'logLevel': 0,
}


# Template for configurating requireJS.

UMD_REQUIREJS_HEADER = """\
(function() {
    'use strict';

    var requirejsOptions = (
"""

UMD_REQUIREJS_FOOTER = """
    )

    if (typeof exports !== 'undefined' && typeof module !== 'undefined') {
        module.exports = requirejsOptions;
    }
    if (typeof requirejs !== 'undefined' && requirejs.config) {
        requirejs.config(requirejsOptions);
    }

}());
"""

# CommonJS is basically incompatible with AMD as defined by requirejs.

UMD_COMMONJS_AMD_HEADER = """\
if (typeof exports === 'object' && typeof exports.nodeName !== 'string'
        && typeof define !== 'function') {
    var define = function (factory) {
        factory(require, exports, module);
    };
}

define(function (require, exports, module) {
"""

UMD_COMMONJS_AMD_FOOTER = """\
});
"""

# This mostly works, but certain plugins are basically broken.

UMD_NODE_AMD_HEADER = """\
(function(define) {
    define(function (require, exports, module) {
        var exports = {};
"""

UMD_NODE_AMD_FOOTER = """
        return exports;
    });

}(
    typeof module === 'object' &&
    module.exports &&
    typeof define !== 'function' ?
        function (factory) {
            module.exports = factory(require, exports, module);
        }
    :
        define
));
"""


def _transpile_generic_to_umd_compat_rjs(reader, writer):
    indent = ' ' * 8
    line = reader.readline()
    if line.strip() in ("'use strict';", '"use strict";'):
        header_lines = iter(UMD_NODE_AMD_HEADER.splitlines(True))
        writer.write(next(header_lines))
        writer.write(next(header_lines))
        writer.write(indent)
        writer.write(line)
        writer.write(next(header_lines))
    else:
        writer.write(UMD_NODE_AMD_HEADER)
        writer.write(indent)
        writer.write(line)

    while line:
        line = reader.readline()
        writer.write(indent)
        writer.write(line)

    writer.write(UMD_NODE_AMD_FOOTER)


def _opener(*a):
    return codecs.open(*a, encoding='utf-8')


class Toolchain(object):
    """
    For shared methods between all toolchains.
    """

    def __init__(self):
        self.build_dir = None
        self.bundle_export_path = None
        self.build_manifest_name = 'build.js'

    def compile(self, source, target):
        logger.info('Compiling %s to %s', source, target)
        with _opener(source, 'r') as reader, _opener(target, 'w') as writer:
            self.transpiler(reader, writer)

    def _gen_req_src_targets(self, d):
        # name = pythonic module name
        # reqold = the commonjs require format to the source
        # source = the source path
        # reqnew = the commonjs require format to the target
        # target = the target write path

        for name, reqold in d.items():
            source = reqold + '.js'
            reqnew = name
            target = reqnew + '.js'
            yield reqold, name, reqnew, source, target

    def compile_all(self):
        compiled_paths = {}
        bundled_paths = {}
        module_names = []

        for reqold, name, reqnew, source, target in self._gen_req_src_targets(
                self.transpile_source_map):
            compiled_paths[name] = reqnew
            module_names.append(name)
            self.compile(source, join(self.build_dir, target))

        for reqold, name, reqnew, source, target in self._gen_req_src_targets(
                self.bundled_source_map):
            bundled_paths[name] = reqnew
            if isfile(source):
                module_names.append(name)
                shutil.copy(source, join(self.build_dir, target))
            elif isdir(reqold):
                shutil.copytree(reqold, join(self.build_dir, reqnew))

        # return compiled targets for assembly
        return compiled_paths, bundled_paths, module_names

    def assemble(self, compiled_paths, bundled_paths, module_names):
        """
        Accept all compiled paths; should return the manifest.
        """

        raise NotImplementedError

    def link(self, manifest_path):
        """
        Should pass in the manifest path to the final JS linker, which
        is typically the bundler.
        """

        raise NotImplementedError

    def finalize(self):
        """
        Optional finalizing step, where further usage of the build_dir,
        scripts and/or results are needed.  This can be used to run some
        specific scripts through node's import system directly on the
        pre-linked assembled files, for instance.
        """

        pass

    def _calf(self):
        """
        The main call, assuming everything is prepared.
        """

        compiled_paths, bundled_paths, module_names = self.compile_all()
        manifest_path = self.assemble(
            compiled_paths, bundled_paths, module_names)
        self.link(manifest_path)
        self.finalize()

    def calf(self, filename):
        """
        Typical safe usage is this, which sets everything that could be
        problematic up.

        Requires the filename which everything will be produced to.
        """

        self.bundle_export_path = filename

        try:
            tempdir = tempfile.mkdtemp()
            self.build_dir = join(tempdir, 'build')
            makedirs(self.build_dir)
            self._calf()
        finally:
            shutil.rmtree(tempdir)

    def __call__(self, target):
        """
        Alias, also make this callable directly.
        """

        self.calf(target)


class RJSToolchain(Toolchain):
    """
    The toolchain that make use of r.js (from require.js).
    """

    def __init__(self):
        super(RJSToolchain, self).__init__()
        self.transpiler = _transpile_generic_to_umd_compat_rjs
        self.rjs = join('.', 'node_modules', 'requirejs', 'bin', 'r.js')

    def assemble(self, compiled_paths, bundled_paths, module_names):
        """
        Assemble the library by compiling everything and generate the
        required files for the final bundling.
        """

        config = {}
        # Set up the statically defined settings.
        config.update(base_requirejs_config)
        config['shim'].update(self.shim)
        config['out'] = self.bundle_export_path

        # Update paths with names pointing to built files in build_dir
        # and generate the list of included files into the final bundle.
        config['paths'].update(compiled_paths)
        config['paths'].update(bundled_paths)
        config['include'] = module_names

        build_manifest_path = join(self.build_dir, self.build_manifest_name)
        with open(build_manifest_path, 'w') as fd:
            fd.write('(\n')
            json.dump(config, fd, indent=4)
            fd.write('\n)')

        # with requirejs, it would be nice to also build a simple config
        # that can be used from within node with the stuff in just the
        # build directory - if this wasn't already defined for some
        # reason.
        requirejs_config_js = join(self.build_dir, 'config.js')

        node_config = {}
        node_config.update(config)
        node_config['baseUrl'] = self.build_dir

        with open(requirejs_config_js, 'w') as fd:
            fd.write(UMD_REQUIREJS_HEADER)
            json.dump(node_config, fd, indent=4)
            fd.write(UMD_REQUIREJS_FOOTER)

        return build_manifest_path

    def link(self, manifest_path):
        """
        Basically link everything up as a bundle, as if statically
        linking everything into "binary" file.
        """

        call([self.rjs, '-o', manifest_path])


class NunjaRJSToolchain(RJSToolchain):
    """
    Nunja specific toolchain.
    """

    def __init__(self):
        super(NunjaRJSToolchain, self).__init__()

        # XXX autogenerate this
        self.transpile_source_map = {
            'repodono.nunja.core': 'src/repodono/nunja/core',
            'repodono.nunja.engine': 'src/repodono/nunja/engine',
            'repodono.nunja.loader': 'src/repodono/nunja/loader',
            'repodono.nunja.registry': 'src/repodono/nunja/registry',
        }

        # XXX Derived these from a setting file
        self.bundled_source_map = {
            'nunjucks': 'node_modules/nunjucks/browser/nunjucks',
            'text': 'node_modules/requirejs-text/text',
            '_core_/_default_wrapper_':
                'src/repodono/nunja/_core_/_default_wrapper_',
        }
        self.shim = {
            'nunjucks': { 'exports': 'nunjucks' },
        }

    def finalize(self):
        # XXX this all could be done using the optimizer as node module
        # and thus this following script could be run from within a
        # customized link() definition to this class.

        script = """
        var nunjucks = require('nunjucks');
        var requirejs = require('requirejs');
        var config = require('%s');

        requirejs.config(config);
        requirejs.define('nunjucks', [], nunjucks);

        var core = requirejs('repodono.nunja.core');
        var tmpl = core.engine.env.getTemplate(
            '_core_/_default_wrapper_/template.jinja');
        var result = nunjucks.precompileString(tmpl.tmplStr, {
            env: core.engine.env,
            name: tmpl.path,
        })
        process.stdout.write(result);
        """
        
        compiled_script = script % (
            join(self.build_dir, 'config.js'),
        )

        # pass this into node

        nodejs = Popen(['node'], stdin=PIPE, stdout=PIPE)
        stdout, stderr = nodejs.communicate(compiled_script)
        with open(self.bundle_export_path, 'a') as fd:
            fd.write(stdout)
