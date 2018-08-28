#!/usr/bin/env python

from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='grout',
    version='2.0.0',
    author='Azavea, Inc.',
    author_email='info@azavea.com',
    description='A flexible schema framework for geospatial data.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/azavea/grout',
    license='MIT',
    keywords='gis jsonschema',
    packages=find_packages(exclude=['tests']),
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        'Django >=1.11, <=2.1',
        'djangorestframework >=3.8.0',
        'djangorestframework-gis >=0.8.1',
        'django-filter >=1.1.0,<2.0.0',
        'django-extensions >=1.6.1',
        'jsonschema >=2.4.0',
        'psycopg2-binary >=2.6',
        'python-dateutil >=2.4.2',
        'PyYAML >=3.11',
        'pytz >=2015.7',
        'requests >=2.8.1',
        'six >= 1.1.0'
    ],
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Operating System :: OS Independent',
    ],
)
