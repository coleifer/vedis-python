import os
import warnings

from setuptools import setup
from setuptools.extension import Extension
try:
    from Cython.Build import cythonize
except ImportError:
    cython_installed = False
    warnings.warn('Cython not installed, using pre-generated C source file.')
else:
    cython_installed = True


if cython_installed:
    python_source = 'vedis.pyx'
else:
    python_source = 'vedis.c'
    cythonize = lambda obj: obj

library_source = 'src/vedis.c'
vedis_extension = Extension(
    'vedis',
    sources=[python_source, library_source])

setup(
    name='vedis',
    version='0.7.1',
    description='Fast Python bindings for the Vedis embedded NoSQL database.',
    author='Charles Leifer',
    author_email='',
    setup_requires=['cython'],
    install_requires=['cython'],
    ext_modules=cythonize([vedis_extension]),
)
