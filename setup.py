# -*- coding: utf-8 -*-
from distutils.core import setup
from stellar import __version__

setup(
    name='stellar-py',
    version=__version__,
    author='Johan Stén',
    author_email='johan.sten@gmail.com',
    packages=['stellar'],
    scripts=['bin/stellar_keygen.py','bin/stellar_send.py'],
    url='https://github.com/johansten/stellar-py',
    license='LICENSE.txt',
    description='Python client library for Stellar',
    long_description=open('README.md').read(),
    classifiers =[
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=[
        "simplejson", "ed25519"
    ],
)
