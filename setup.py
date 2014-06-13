from setuptools import setup, Extension
from setuptools.command.install import install as InstallCommand

import glob
import os
import subprocess
import sys
import traceback

lib_vedis = Extension(
    name='vedis.vedis',
    define_macros=[('VEDIS_ENABLE_THREADS', '1')],
    sources=['vedis/src/vedis.c'])

class VedisInstallCommand(InstallCommand):
    def run(self):
        import ipdb; ipdb.set_trace()
        cur_dir = os.path.dirname(__file__)
        src = lambda s: os.path.join(cur_dir, 'vedis', 'src', s)

        # Compile vedis source.
        #subprocess.check_call(['make', 'build_vedis'])
        InstallCommand.run(self)
        subprocess.check_call([
            'ctypesgen.py',
            src('vedis.h'),
            #'-L',
            #'./',
            '-l',
            'vedis',
            '-o',
            os.path.join(cur_dir, 'vedis', '_vedis.py')])


setup(
    name='vedis',
    version='0.1.0',
    description='Python bindings for Vedis, the embedded NoSQL database.',
    author='Charles Leifer',
    author_email='',
    packages=['vedis'],
    package_data={
        'vedis': [
            'src/vedis.c',
            'src/vedis.h',
        ],
    },
    zip_safe=False,
    install_requires=['ctypesgen==0.r125'],
    ext_modules=[lib_vedis],
    cmdclass={
        'install': VedisInstallCommand},
)
