# -*- coding: utf-8 -*-
from setuptools import setup
from codecs import open # To use a consistent encoding
from os import path

# Get the long description from the relevant file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

# Get the version number
execfile('stellar/version.py')

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
	long_description=long_description,
	classifiers =[
		'Programming Language :: Python',
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Topic :: Software Development :: Libraries :: Python Modules'],
	install_requires=[
		"simplejson", "ed25519", "appdirs"
	],
)
