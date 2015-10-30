#!/usr/bin/env python

from setuptools import setup, find_packages

tests_require = []

setup(
    name='ashlar',
    version='0.0.2',
    description='Define and validate schemas for metadata for geotemporal event records',
    author='Azavea, Inc.',
    author_email='info@azavea.com',
    keywords='gis jsonschema',
    packages=find_packages(exclude=['tests']),
    dependency_links=[
        'https://github.com/azavea/djsonb/tarball/develop#egg=djsonb-0.1.2'
    ],
    install_requires=[
        'Django >=1.8',
        'djangorestframework >=3.1.1',
        'djangorestframework-gis >=0.8.1',
        'django-filter >=0.9.2',
        'djsonb >=0.1.2',
        'jsonschema >=2.4.0',
        'psycopg2 >=2.6',
        'django-extensions >=1.5.2',
        'python-dateutil >=2.4.2',
        'PyYAML >=3.11'
    ],
    extras_require={
        'dev': [],
        'test': tests_require
    },
    test_suite='tests',
    tests_require=tests_require,
)
