#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import dynamic_preferences

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = dynamic_preferences.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-dynamic-preferences',
    version=version,
    description="""Dynamic global and instance settings for your django project""",
    long_description=readme + '\n\n' + history,
    author='Eliot Berriot',
    author_email='contact@eliotberriot.com',
    url='https://github.com/EliotBerriot/django-dynamic-preferences',
    packages=[
        'dynamic_preferences',
    ],
    include_package_data=True,
    install_requires=[
        'django>=1.8',
        'six',
        'persisting_theory==0.2.1',
    ],
    license="BSD",
    zip_safe=False,
    keywords='django-dynamic-preferences',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
