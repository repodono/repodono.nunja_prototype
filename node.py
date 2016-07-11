import os
from os.path import isdir
from os.path import join
from shutil import rmtree

from subprocess import check_output
from subprocess import call

NODE = 'node'
NPM = 'npm'
NODE_PATH = join('.', 'node_modules')


def _check_clean_recursive_symlink(path):
    # Used to delete any and all symlinks that links back to grandparent
    # path, which breaks setup.py
    if isdir(path):
        rmtree(path)


def main():
    os.environ['NODE_PATH'] = NODE_PATH
    node_version = tuple(int(i) for i in check_output(
        [NODE, '-v']).decode('ascii').strip()[1:].split('.'))

    # if node_version < (0, 11):
    #     call(NPM + ' link --prefix=.')

    call([NPM, 'link', '--prefix=.'])
    call([NPM, 'install'])

    # Kill all possible node_modules symlinks that point back to here
    # as we can't import using `require('repodono.nunja')` anyway as
    # node/npm is not very well defined as to when that can be done.
    # All I know is that it cannot be done from here even after doing
    # the installation as outlined here.  Yay for raw filesystem based
    # imports.
    _check_clean_recursive_symlink(join('.', 'lib', 'node_modules'))
    _check_clean_recursive_symlink(join('.', 'lib32', 'node_modules'))
    _check_clean_recursive_symlink(join('.', 'lib64', 'node_modules'))


if __name__ == '__main__':
    main()
