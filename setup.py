from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.install import install as InstallCommand

import os
import subprocess

lib_vedis = Extension(
    name='vedis.libvedis',
    define_macros=[('VEDIS_ENABLE_THREADS', '1')],
    sources=['vedis/src/vedis.c'])

class GenerateCtypesWrapper(build_py):
    def run(self):
        cur_dir = os.path.realpath(os.path.dirname(__file__))
        wrapper = os.path.join(cur_dir, 'vedis', '_vedis.py')
        subprocess.check_call([
            'python2',
            os.path.join('ctypesgen', 'ctypesgen.py'),
            os.path.join('vedis', 'src', 'vedis.h'),
            '-L',
            './',
            '-l',
            'vedis',
            '-o',
            wrapper])

        # Read content of generated file.
        with open(wrapper) as fh:
            content = fh.readlines()

        # Modify the add_library_path to use the current dir.
        with open(wrapper, 'w') as fh:
            for line in content:
                if line.startswith('add_library_search_dirs('):
                    fh.write('add_library_search_dirs(['
                             'os.path.realpath(os.path.dirname(__file__))'
                             '])\n')
                else:
                    fh.write(line)

        return build_py.run(self)

setup(
    name='vedis',
    version='0.1.7',
    description='Python bindings for Vedis, the embedded NoSQL database.',
    author='Charles Leifer',
    author_email='',
    packages=['vedis'] + find_packages(),
    package_data={
        'vedis': [
            'src/vedis.c',
            'src/vedis.h',
        ],
    },
    zip_safe=False,
    ext_modules=[lib_vedis],
    cmdclass={'build_py': GenerateCtypesWrapper},
)
