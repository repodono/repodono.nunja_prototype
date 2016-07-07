# -*- coding: utf-8 -*-
import logging
import sys
import os
from os.path import join

from subprocess import call

logging.basicConfig(
    level='INFO',
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

NODE = 'node'
NPM = 'npm'

NODE_PATH = join('.', 'node_modules')
GRUNT = join(NODE_PATH, 'grunt-cli', 'bin', 'grunt')

# ./node_modules/grunt-cli/bin/grunt test   --gruntfile=Gruntfile.js

require_js_tmpl = """\
requirejs.config(%s
);
"""


def main():
    # Testing molds needed manual intervention.
    from repodono.nunja.registry import registry
    import repodono.nunja.testing
    registry.register_module(repodono.nunja.testing, subdir='mold')
    registry.init_entrypoints()

    with open('nunja.generated.js', 'w') as fd:
        fd.write(require_js_tmpl % registry.export_local_requirejs())

    os.environ['NODE_PATH'] = NODE_PATH
    call([GRUNT, '--gruntfile=Gruntfile.js'] + sys.argv[1:])


if __name__ == '__main__':
    main()
