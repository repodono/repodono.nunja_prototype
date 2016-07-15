# -*- coding: utf-8 -*-
import logging
import sys
import os
from os.path import join
from os.path import dirname
from os.path import realpath

from subprocess import call

logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

NODE = 'node'
NPM = 'npm'

NODE_PATH = join('.', 'node_modules')
GRUNT = join(NODE_PATH, 'grunt-cli', 'bin', 'grunt')


def main():
    # XXX this needs big testing.
    from repodono.nunja.js import NunjaRJSToolchain
    # Testing molds needed manual intervention.
    from repodono.nunja.registry import registry
    from repodono.nunja import exporters
    import repodono.nunja.testing
    registry.register_module(repodono.nunja.testing, subdir='mold')
    registry.init_entrypoints()

    bundle_target = realpath('repodono.nunja.js')

    compiler = NunjaRJSToolchain()
    compiler(bundle_target)

    with open('nunja.generated.js', 'w') as fd:
        fd.write(exporters.export_umd_requirejs())

    with open('nunja_id.exported.js', 'w') as fd:
        fd.write(exporters.export_umd_generic_json(
            registry.export_jinja_template_paths()))

    os.environ['NODE_PATH'] = NODE_PATH
    call([GRUNT, '--gruntfile=Gruntfile.js'] + sys.argv[1:])


if __name__ == '__main__':
    main()
