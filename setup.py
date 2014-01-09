#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='pybuilder-contrib',
    version='0.1.0',
    description='Unofficial storing place for extra tasks, plugins, etc.',
    long_description=readme + '\n\n' + history,
    author='Brent Hoover',
    author_email='brent@hoover.net',
    url='https://github.com/zenweasel/pybuilder-contrib',
    packages=[
        'pybuilder-contrib',
    ],
    package_dir={'pybuilder-contrib': 'pybuilder-contrib'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='pybuilder-contrib',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)