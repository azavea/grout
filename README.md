# Grout 

[![Build Status](https://travis-ci.org/azavea/grout.svg?branch=develop)](https://travis-ci.org/azavea/grout)

Grout is a Django app providing a flexible-schema framework for geospatial data.

Grout combines the flexibility of NoSQL databases with the geospatial muscle of
[PostGIS](http://postgis.org/), allowing you to make migration-free edits to
your database schema while still having access to powerful geospatial queries.
Think NoSQL databases, but with schema validation and PostGIS support.

Grout will help you:

- **Define, edit, and validate schemas** for records in your application
- **Keep track of changes to schemas** using a built-in versioning system
- Perform **fast filtering of user-defined fields**
- Run **complex geospatial queries**, even on records stored with unstructured data

Grout is the core library of the _Grout suite_, a toolkit for easily building
flexible-schema apps on top of Grout. You can use Grout by installing it as an app
in a Django project, or you can deploy it as a [standalone API
server](https://github.com/azavea/grout-server) with an optional [admin
backend](https://github.com/azavea/grout-schema-editor).

For more information on the different ways to use Grout, see [Getting
started](#getting-started).

## Getting started

### Django

If you're developing a Django project, you can install Grout as a Django app and
use it in your project.

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

```bash
$ pip install grout
```

To use the bleeding-edge version of Grout, install it from GitHub.

```bash
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

Grout requires that the `GROUT` configuration variable be defined in your `settings.py` file
in order to work properly. The `GROUT` variable is a dictionary of configuration
directives for the app.

Currently, `'SRID'` is the only required key in the `GROUT` dictionary. `'SRID'` is an integer
corresponding to the [spatial reference
identifier](https://en.wikipedia.org/wiki/Spatial_reference_system#Identifier)
that Grout should use to store geometries. `4326` is the most common SRID, and
is a good default for projects.

Here's an example configuration for a development project:

```python
# settings.py

# The projection for geometries stored in Grout.
GROUT = { 'SRID': 4326 }
```

Note that Grout uses [Django REST Framework](http://www.django-rest-framework.org/)
under the hood to provide API endpoints. To configure DRF-specific settings like
authentication, see the [DRF docs](http://www.django-rest-framework.org/).

#### More examples

[Grout Server](https://github.com/azavea/grout-server) is a simple deployment
of a Grout API server designed to be used as a standalone app. It also serves
as a good example of how to incorporate Grout into a Django project, and
includes a preconfigured authentication module to boot. If you're
having trouble installing or configuring Grout in your project, Grout Server
is a good resource for troubleshooting.

### Standalone project

If you're not a Django developer, you can still use Grout as a standalone
API server using the [Grout Server](https://github.com/azavea/grout-server)
project. See the [Grout Server docs](https://github.com/azavea/grout-server)
for details on how to install a Grout Server instance.

## Concepts

### Data model

![The Grout data model centers around Records, each of which has an associated
RecordSchema and RecordType.](./docs/images/grout-data-model.png).

Grout is centered around _Records_, which are just **entities in your database**.
A Record can be any type of thing or event in the world, although Grout is most
useful when your Records have some geospatial and temporal component.

Every Record contains a reference to a _RecordSchema_, which catalogs the
**versioned schema** of the Record that points to it. This schema is stored as
[JSONSchema](http://json-schema.org/), a specification for describing data models in JSON.

Finally, each RecordSchema contains a reference to a _RecordType_, which is
a **simple container for organizing Records**. The RecordType exposes a way to
reliably access a set of Records that represent the same type of thing, even if
they have different schemas. As we’ll see shortly, RecordTypes are useful access
points to Records because RecordSchemas can change at any moment.

### Versioned schemas

In Grout, RecordSchemas are append-only, meaning that they cannot be deleted.
Instead, when you want to change the schema of a Record, you create a new
RecordSchema and update the version attribute.

For a quick example, say that we have a RecordSchema describing data stored on
a `cat` RecordType. The RecordSchema might look something like this:

```json
{
  "version": 1,
  "next_version": null,
  "schema": {
    "type": "object",
    "title": "Initial Schema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "properties": {
      "catDetails": {
        "$ref": "#/definitions/driverPosterDetails"
      },
    "definitions": {
      "catDetails": {
        "type": "object",
        "title": "Cat Details",
        "properties": {
          "Name": {
            "type": "string",
            "fieldType": "text",
            "isSearchable": true,
            "propertyOrder": 1
          },
          "Age": {
            "type": "integer",
            "fieldType": "integer",
            "minimum": 0,
            "maximum": 100
            "isSearchable": true,
            "propertyOrder": 2,
          },
          "Color": {
            "type": "string",
            "fieldType": "text",
            "isSearchable": true,
            "propertyOrder": 3
          },
          "Breed": {
            "type": "select",
            "fieldType": "selectlist",
            "enum": [
              "Tabby",
              "Bobtail",
              "Abyssinian"
            ],
            "isSearchable": true,
            "propertyOrder": 4
          }
        }
      }
    }
  }
}
```

A few things to note about this RecordSchema object:

- This is the first version of the schema (its `version` is `1`)
- There is no more recent version than this one (its `next_version` is `null`)
- The schema definition itself is stored as a JSONSchema object on the `schema`
  attribute
- All of the available fields are namespaced by the `catDetails` attribute, which
  we sometimes refer to as a _form_ or _related content_

Now say we want to change the `Age` field to a `Date of Birth` field. Instead of
changing the schema directly, we'll create a new schema. Grout will automatically
set `version: 2` and `next_version: null` for this updated schema:

```json
{
  "version": 2,
  "next_version": null,
  "schema": {
    "type": "object",
    "title": "Initial Schema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "properties": {
      "catDetails": {
        "$ref": "#/definitions/driverPosterDetails"
      },
    "definitions": {
      "catDetails": {
        "type": "object",
        "title": "Cat Details",
        "properties": {
          "Name": {
            "type": "string",
            "fieldType": "text",
            "isSearchable": true,
            "propertyOrder": 1
          },
          "Age": {
            "type": "integer",
            "fieldType": "integer",
            "minimum": 0,
            "maximum": 100
            "isSearchable": true,
            "propertyOrder": 2,
          },
          "Date of Birth: {
            "type": "string",
            "format": "datetime",
            "fieldType": "text",
            "isSearchable": true,
            "propertyOrder": 3,
          },
          "Color": {
            "type": "string",
            "fieldType": "text",
            "isSearchable": true,
            "propertyOrder": 4
          },
          "Breed": {
            "type": "select",
            "fieldType": "selectlist",
            "enum": [
              "Tabby",
              "Bobtail",
              "Abyssinian"
            ],
            "isSearchable": true,
            "propertyOrder": 5
          }
        }
      }
    }
  }
}
```

In addition, Grout will update the initial schema to set `next_version: 2`:

{
  "version": 1,
  "next_version": 2,
  "schema": {
    ...
  }
}

Now, when a user searches for Records in the `cat` RecordType, Grout can find
the most recent schema by looking for the RecordSchema where `next_version: null`.
This preserves a full audit trail of the RecordSchema, allowing us to
inspect how the schema has changed over time.

For a closer look at the data model, see the [`models.py` file in the Grout
library](https://github.com/azavea/grout/blob/develop/grout/models.py).

## Developing

These instructions will help you set up a development version of Grout and
contribute changes back upstream.

### Requirements

The Grout development environment is containerized with Docker to ensure similar
environments across platforms. In order to develop with Docker, you need the
following dependencies:

- [Docker CE Engine](https://docs.docker.com/install/) >= 1.13.0 (must be
  compatible with [Docker Compose file v3
  syntax](https://docs.docker.com/compose/compose-file/#compose-and-docker-compatibility-matrix))
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

Clone the repo with git.

```bash
$ git clone git@github.com:azavea/grout.git
$ cd grout
```

Run the `update` script to set up your development environment.

```bash
$ ./scripts/update
```

### Running tests

Once your environment is up to date, you can use the `scripts/test` script to
run the Grout unit test suite.

```bash
$ ./scripts/test
```

This command will run a matrix of tests for **every supported version of Python and
Django** in the project. If you're developing locally and you just want to run
a subset of the tests, you can specify the version of Python
that you want to use to run tests: 

```bash
# Only run tests for Python 2.7 (this will test Django 1.8).
$ ./scripts/test app py27

# Only run tests for Python 3.7 (this will test Django 2.0).
$ ./scripts/test app py37
```

For a list of available Python versions, see the `envlist` directive in the [`tox.ini`
file](./tox.ini). 

#### Cleaning up

Tox creates a new virtualenv for every combination of Python and Django versions
used by the test suite. In order to clean up stopped containers and
remove these virtualenvs, use the `clean` script:

```bash
$ ./scripts/clean
```

Note that `clean` will remove **all dangling images, stopped containers, and 
unused volumes** on your machine. If you don't want to remove these artifacts,
[view the `clean` script](./scripts/clean) and run only the command that
interests you.

### Making migrations

If you edit the data model in `grout/models.py`, you'll need to create a new
migration for the app. You can use the `django-admin` script in the `scripts`
directory to automatically generate the migration:

```bash
$ ./scripts/django-admin makemigrations
```

Make sure to register the new migrations file with Git:

```bash
$ git add grout/migrations
```

## Resources 

The following resources provide helpful tips for deploying and using Grout.

- [Grout Server](https://github.com/azavea/grout-server): An easily-deployable
  standalone instance of a Grout API server.
- [Grout Schema Editor](https://github.com/azavea/grout-schema-editor): A
  purely static app that can read and write flexible schemas from a Grout API.
- [Demo app](https://github.com/jeancochrane/philly-fliers/): A demo project
  providing an example of incorporating the Grout suite into a Vue.js app.

## Alternatives to Grout
