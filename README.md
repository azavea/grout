# Grout 

[![Build Status](https://travis-ci.org/azavea/grout.svg?branch=develop)](https://travis-ci.org/azavea/grout)

Grout is a Django app providing a **flexible-schema framework for geospatial data**.

Grout combines the flexibility of NoSQL databases with the geospatial muscle of
[PostGIS](http://postgis.org/), allowing you to make migration-free edits to
your database schema while still having access to powerful geospatial queries.
Think **NoSQL databases, but with schema validation and PostGIS support**.

Grout will help you:

- **Define, edit, and validate schemas** for records in your application
- **Keep track of changes to schemas** using a built-in versioning system
- Perform **fast filtering of user-defined fields**
- Run **complex geospatial queries**, even on records stored with unstructured data

Grout is the core library of the **Grout suite**, a toolkit for easily building
flexible-schema apps on top of Grout. You can use Grout by installing it as an app
in a Django project, or you can deploy it as a [standalone API
server](https://github.com/azavea/grout-server) with an optional [admin
backend](https://github.com/azavea/grout-schema-editor).

For more information on the different ways to use Grout, see [Getting
started](#getting-started).

## Getting started

### Django

If you're developing a Django project, you can easily install Grout as a
Django app and use it in your project.

#### Requirements

Grout supports the following versions of Python and Django:

- **Python**: 2.7, 3.4, 3.5, 3.6, 3.7
- **Django**: 1.11, 2.0

Certain versions of Django only support certain versions of Python. To ensure
that your Python and Django versions work together, see the Django FAQ: [What
Python version can I use with
Django?](https://docs.djangoproject.com/en/2.1/faq/install/#what-python-version-can-i-use-with-django)

#### Installation

Install the Grout library from PyPi using `pip`.

```
$ pip install grout
```

To use the bleeding-edge version of Grout, install it from GitHub.

```
$ git clone git@github.com:azavea/grout.git
```

Make sure Grout is included in `INSTALLED_APPS` in your project's `settings.py`.

```python
# settings.py

INSTALLED_APPS = (
    ...
    'grout',
)
```

To use Grout as an API server, you need to incorporate the API views into your
`urls.py` file. The following example will include Grout views under the
`/grout` endpoint. 

```python
# urls.py

urlpatterns = [
    url(r'^grout/', include('grout.urls'))
]
```

Note that Grout automatically nests views under the `/api/` endpoint, meaning
that the setting above would create URLs like `hostname.com/grout/api/records`.
If you'd prefer Grout views to live under a top-level `/api/` endpoint (like
`hostname.com/api/records`), you can import the Grout `urlpatterns` directly.

```python
# urls.py

from grout import urlpatterns as grout_urlpatterns

urlpatterns = grout_urlpatterns
```

#### Configuration

Here's a sample setup for a development project:

```python
# settings.py

# The projection for geometries stored in Grout.
GROUT = { 'SRID': 4326 }

# Default admin credentials for development.
DEFAULT_ADMIN_EMAIL = 'grout@azavea.com'
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin'

# Names of the different authentication groups. These are used primari
USER_GROUPS = {
    'READ_ONLY': 'public',
    'READ_WRITE': 'staff',
    'ADMIN': 'admin'
}
```

Note that Grout uses [Django REST Framework](http://www.django-rest-framework.org/)
under the hood to provide RESTful API endpoints. To configure DRF settings like
authentication, see the [DRF docs](http://www.django-rest-framework.org/).

### Standalone project

## Useful links

- [Grout Server](https://github.com/azavea/grout-server), an easily-deployable
  standalone instance of a Grout API server
- [Grout Schema Editor](https://github.com/azavea/grout-schema-editor), a
  purely static app that can read and write flexible schemas from a Grout API
- [Demo app](https://github.com/jeancochrane/philly-fliers/) showing how to
  incorporate the Grout suite into your application

## Usage

### Installation



## Developing

These instructions will help you set up a development version of Grout and
contribute changes back upstream.

### Installation



### Making migrations

If you edit the data model in `grout/models.py`, you'll need to create a new
migration for the app. You can use the `django-admin` script in the `scripts`
directory to automatically generate the migrations:

```bash
./scripts/django-admin makemigrations
```

Make sure to register the new migrations file with Git:

```bash
git add grout/migrations
```

### Testing

### Requirements

- [Docker](http://docs.docker.com/installation/ubuntulinux/)
- [docker-compose](https://docs.docker.com/compose/install/) > 2.0

### Running tests

Use the `scripts/test` script to run tests:

```
./scripts/test
```

This will run a matrix of tests for **every supported version of Python and
Django**. If you're developing locally and you just want to run tests once, you
can specify the version you want to run: 

```
# Only run tests for Python 2.7 and Django 1.8
./scripts/test app py27-django18
```

For a list of available versions, see the `envlist` directive in the [`tox.ini`
file](./tox.ini). 

To clean up stopped containers and virtualenvs, use the `clean` script:

```
./scripts/clean
```

### Notes on test execution

- You might see duplicate key errors from the db container; these are generated
deliberately by the test suite and can be safely ignored.

- If your tests crash and leave a `test_postgres` database lying around that prevents you
from running further tests, the simplest solution is to run `docker-compose rm db`, which
will delete the database container and refresh it from the base image. You can
also delete the database container in a shell prompt when running
`./scripts/test` again after a crash.


## How it works 
