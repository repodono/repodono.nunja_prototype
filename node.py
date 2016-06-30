import os
from os.path import join
from shutil import rmtree

from subprocess import check_output
from subprocess import call

NODE = 'node'
NPM = 'npm'
NODE_PATH = join('.', 'node_modules')


def main():
    os.environ['NODE_PATH'] = NODE_PATH
    node_version = tuple(int(i) for i in check_output(
        [NODE, '-v']).decode('ascii').strip()[1:].split('.'))

    # if node_version < (0, 11):
    #     call(NPM + ' link --prefix=.')

    call([NPM, 'link', '--prefix=.'])
    call([NPM, 'install'])
    try:
        # die.  The grandparent symlink in there will break setup.py
        rmtree(join('.', 'lib', 'node_modules'))
    except:
        # Well, I guess it wasn't there, I don't care then.
        pass


if __name__ == '__main__':
    main()
