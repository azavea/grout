#!/usr/bin/env python

from setuptools import setup, find_packages

tests_require = []


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='ashlar',
    version='1.0.0',
    author='Azavea, Inc.',
    author_email='info@azavea.com',
    description='A flexible schema framework for geospatial data.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/azavea/ashlar',
    license='MIT',
    keywords='gis jsonschema',
    packages=find_packages(exclude=['tests']),
    dependency_links=[
        'https://github.com/azavea/djsonb/tarball/develop#egg=djsonb-0.2.2'
    ],
    install_requires=[
        'Django ==1.8.6',
        'djangorestframework >=3.1.1, <3.5.0',
        'djangorestframework-gis >=0.8.1, <0.12.0',
        'django-filter >=0.9.2, <0.14.0',
        'djsonb >=0.2.2',
        'jsonschema >=2.4.0',
        'psycopg2 >=2.6',
        'django-extensions >=1.6.1',
        'python-dateutil >=2.4.2',
        'PyYAML >=3.11',
        'pytz >=2015.7',
        'requests >=2.8.1'
    ],
    extras_require={
        'dev': [],
        'test': tests_require
    },
    test_suite='tests',
    tests_require=tests_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
        'Topic :: Database :: Front-Ends',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Operating System :: OS Independent',
    ],
)
