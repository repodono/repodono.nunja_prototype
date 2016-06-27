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
    #     rmtree('lib', 'node_module')

    call([NPM, 'link', '--prefix=.'])
    call([NPM, 'install'])


if __name__ == '__main__':
    main()
