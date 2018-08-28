# Grout 

[![Build Status](https://travis-ci.org/azavea/grout.svg?branch=develop)](https://travis-ci.org/azavea/grout)

Grout is a flexible-schema framework for geospatial data, powered by Django and PostgreSQL. Think: NoSQL database server, but with schema validation and PostGIS support.

## Contents

- [**Introduction**](#introduction)
- [**Getting started**](#getting-started)
    - [Django](#django)
        - [Requirements](#requirements)
        - [Installation](#installation)
        - [Configuration](#configuration)
        - [More examples](#more-examples)
    - [Non-Django applications](#non-django-applications)
- [**Concepts**](#concepts)
    - [Data model](#data-model)
    - [Versioned schemas](#versioned-schemas)
- [**API documentation**](#api-documentation)
    - [Request and response formats](#request-and-response-formats)
    - [Pagination](#pagination)
    - [Resources](#resources)
        - [RecordTypes](#recordtypes)
        - [RecordSchemas](#recordschemas)
        - [Records](#records)
        - [Boundaries](#boundaries)
        - [BoundaryPolygons](#boundarypolygons)
- [**Developing**](#developing)
    - [Requirements](#requirements-1)
    - [Installation](#installation-1)
    - [Running tests](#running-tests)
        - [Cleaning up](#cleaning-up)
    - [Making migrations](#making-migrations)
- [**Resources**](#resources)
    - [Grout suite](#grout-suite)
    - [Historical documents](#historical-documents)
    - [Roadmap](#roadmap)

## Introduction

Grout combines the flexibility of NoSQL databases with the geospatial muscle of
[PostGIS](http://postgis.org/), allowing you to make migration-free edits to
your database schema while still having access to powerful geospatial queries.

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

Ready for more? To get started using Grout with Django, see [Getting
started](#getting-started). To get started using Grout with another
stack, see [Non-Django applications](#non-django-applications). For more
background on how Grout works, see [Concepts](#concepts).

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

To use the development version of Grout, install it from GitHub.

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
having trouble installing or configuring Grout in your project, [Grout
Server](https://github.com/azavea/grout-server)
is a good resource for troubleshooting.

### Non-Django applications

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
RecordSchema and update the `version` attribute.

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
            "maximum": 100,
            "isSearchable": true,
            "propertyOrder": 2
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
              "maximum": 100,
              "isSearchable": true,
              "propertyOrder": 2
            },
            "Date of Birth": {
              "type": "string",
              "format": "datetime",
              "fieldType": "text",
              "isSearchable": true,
              "propertyOrder": 3
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
}
```

In addition, Grout will update the initial schema to set `next_version: 2`:

```
{
  "version": 1,
  "next_version": 2,
  "schema": {
    ...
  }
}
```

Now, when a user searches for Records in the `cat` RecordType, Grout can find
the most recent schema by looking for the RecordSchema where `next_version: null`.
This preserves a full audit trail of the RecordSchema, allowing us to
inspect how the schema has changed over time.

For a closer look at the Grout data model, see the [`models.py` file in the Grout
library](https://github.com/azavea/grout/blob/develop/grout/models.py).

## API documentation

### Request and response formats

Communication with the API generally follows the principles of RESTful API design.
API paths correspond to resources, `GET` requests are used to retrieve objects, `POST`
requests are used to create new objects, and `PATCH` requests are used to update
existing objects. This pattern is followed in nearly all cases; any exceptions
will be noted in the documentation.

Responses from the API are exclusively JSON.

Endpoint behavior can be configured using query parameters for `GET` requests,
while `POST` requests require a payload in JSON format.

### Pagination

All API endpoints that return lists of resources are paginated. The pagination takes the following format:

```
{
    "count": 57624,
    "next": "http://localhost:8000/api/records/?offset=20",
    "previous": "http://localhost:7000/api/records/",
    "results": [
        ...
    ]
}
```

In a real response, the domain and port for the `next` and `previous` fields
will be that of the server responding to the request.

This format applies to the API endpoints below and will not be repeated in the
documentation for each individual endpoint.

### Resources

#### RecordTypes

Because the RecordSchema for a set of Records can change at any time, the RecordType API
endpoint provides a consistent access point for retrieving a set of Records.
Use the RecordType endpoints to discover the most recent RecordSchema for the Records
you are interested in before performing further queries.

Paths:

* List: `/api/recordtypes/`
* Detail: `/api/recordtypes/{uuid}/`

Query parameters:

* `active`: Boolean
    * Filter for only RecordTypes with an `active` value of True.
      Generally, you will want to limit yourself to active RecordTypes.

Results fields:

| Field name | Type | Description |
| ---------- | ---- | ----------- |
| `uuid` | UUID | Unique identifier for this RecordType. |
| `current_schema` | UUID | The most recent RecordSchema for this RecordType. |
| `created` | Timestamp | The date and time when this RecordType was created. |
| `modified` | Timestamp | The date and time when this RecordType was last modified. |
| `label` | String | The name of this RecordType. |
| `plural_label` | String | The plural version of the name of this RecordType. |
| `description` | String | A short description of this RecordType. |
| `active` | Boolean | Whether or not this RecordType is active. This field allows RecordTypes to be deactivated rather than deleted. |
| `geometry_type` | String | The geometry type supported for Records of this RecordType. One of `point`, `polygon`, `multipolygon`, `linestring`, or `none`. | 
| `temporal` | Boolean | Whether or not Records of this RecordType should store datetime data in the `occurred_from` and `occurred_to` fields. |

#### RecordSchemas

The RecordSchema API endpoint can help you discover the fields that
should be available on a given Record. This can be useful for automatically generating filters
based on a Record's fields, or for running custom validation on a Record's
schema.

Paths:

* List: `/api/recordschemas/`
* Detail: `/api/recordschemas/{uuid}/`

Results fields:

| Field name | Type | Description |
| ---------- | ---- | ----------- |
| `uuid` | UUID | Unique identifier for this RecordSchema. |
| `created` | Timestamp | The date and time when this RecordSchema was created. |
| `modified` | Timestamp | The date and time when this RecordSchema was last modified. |
| `version` | Integer | A sequential number indicating what version of the RecordType's schema this is. Starts at 1. |
| `next_version` | UUID | Unique identifier of the RecordSchema with the next-highest version number for this schema's RecordType. If this is the most recent version of the schema, this field will be `null`. |
| `record_type` | UUID | Unique identifier of the RecordType that this RecordSchema refers to. |
| `schema` | Object | A [JSONSchema](http://json-schema.org/) object that should validate Records that refer to this RecordSchema. |

#### Records

Records are the heart of a Grout project: the entities in your database. The
Records API endpoint provides a way of retrieving these objects for analysis
or display to an end user.

Paths:

* List: `/api/records/`
* Detail: `/api/records/{uuid}/`

Query Parameters:

* `archived`: Boolean
    * Records can be "archived" to denote that they are no longer current, as an
      alternative to deletion. Pass `True` (case-sensitive) to this parameter to return archived
      Records only, and pass `False` (case-sensitive) to return current Records only.
      Omitting this parameter returns both types.

* `details_only`: Boolean
    * In the [Grout Schema Editor](https://github.com/azavea/grout-schema-editor),
      every Record is automatically generated with a `<record_type>Details`
      form which is intended to contain a basic summary of information about the Record.
      Passing `True` (case-sensitive) to this parameter will omit any other
      forms which may exist on the Record. This is useful for limiting the size
      of the payload returned when only a summary view is needed.

* `record_type`: UUID
    * Limit the response to Records matching the passed RecordType UUID.
      This is optional in theory, but for most applications it is a good idea
      to include this parameter by default. It is considered rare that it will
      be useful to return two different types of Records in a single request.
      It is usually a better idea to make a separate request for each RecordType.

* `jsonb`: Object
    * Query the data fields of the object and filter on the result.
    * Keys in this object mimic the search paths to filter on a particular object
      field. However, in place of values, a filter rule definition is used. Example:
`{ "accidentDetails": {
    "Main+cause": {
        "_rule_type": "containment",
        "contains": [
            "Vehicle+defect",
            "Road+defect",
            ["Vehicle+defect"],
            ["Road+defect"]
        ]
    },
    "Num+driver+casualties": {
        "_rule_type": "intrange",
        "min": 1,
        "max": 3
    }
}}`. This query defines the following two filters:
        * `accidentDetails -> "Main cause" == "Vehicle defect" OR accidentDetails -> "Main cause" == "Road defect"`
        * `accidentDetails -> "Num driver casualties" >= 1 AND accidentDetails -> "Num driver casualties" <= 3`
    * There is a third filter rule type available: `containment_multiple`.
      This is used when searching a form of which there can be several on a single Record.
      Here's an example:
`{"person":{"Injury":{"_rule_type":"containment_multiple","contains":["Fatal"]}}}`

* `occurred_min`: Timestamp
    * Filter to Records occurring after this date.

* `occurred_max`: Timestamp
    * Filter to Records occurring before this date.

* `polygon_id`: UUID
    * Filter to Records which occurred within the Polygon identified by the
      UUID. The value must refer to a [Boundary](#boundaries) in the database.

* `polygon`: GeoJSON
    * Filter to Records which occurred within the bounds of a valid GeoJSON
      object.

Results fields:

| Field name | Type | Description |
| ---------- | ---- | ----------- |
| `uuid` | UUID | Unique identifier for this Record. |
| `created` | Timestamp | The date and time when this Record was created. |
| `modified` | Timestamp | The date and time when this Record was last modified. |
| `occurred_from` | Timestamp | The earliest time at which this Record might have occurred. |
| `occurred_to` | Timestamp | The latest time at which this Record might have occurred. Note that this field is mandatory for temporal Records: if a Record only occurred at one moment in time, the `occurred_from` field and the `occurred_to` field will have the same value.  |
| `geom` | GeoJSON | Geometry representing the location associated with this Record. |
| `location_text` | String | A description of the location where this Record occurred, typically an address. |
| `archived` | Boolean | A way of hiding records without deleting them completely. `True` indicates the Record is archived. |
| `schema` | UUID | References the RecordSchema which was used to create this Record. |
| `data` | Object | A JSON object representing the flexible data fields associated with this Record. It is always true that the object stored in `data` conforms to the RecordSchema referenced by the `schema` UUID. |

#### Boundaries

Boundaries provide a quick way of storing Shapefile data in Grout without
having to create separate RecordTypes. Using a Boundary, you can upload
and retrieve Shapefile data for things like administrative borders and focus
areas in your application.

Paths:

* List: `/api/boundaries/`
* Detail: `/api/boundaries/{uuid}/`

Results fields:

| Field name | Type | Description |
| ---------- | ---- | ----------- |
| `uuid` | UUID | Unique identifier for this Boundary. |
| `created` | Timestamp | The date and time when this Boundary was created. |
| `modified` | Timestamp | The date and time when this Boundary was last modified. |
| `label` | String | Label of this Boundary, for display. |
| `color` | String | Color preference to use for rendering this Boundary. |
| `display_field` | String | Which field of the imported Shapefile to use for display. |
| `data_fields` | Array | List of the names of the fields contained in the imported Shapefile. |
| `errors` | Array | A possible list of errors raised when importing the Shapefile. |
| `status` | String | Import status of the Shapefile. |
| `source_file` | String | URI of the Shapefile that was originally used to generate this Boundary. |

Notes:

Creating a new Boundary and its [BoundaryPolygon](#boundarypolygon) correctly is a two-step process.

1. `POST` to `/api/boundaries/` with a zipped Shapefile attached; you will need
   to include the label as form data. You should receive a 201 response which
   contains a fully-fledged Boundary object, including a list of available
   data fields in `data_fields`.

2. The response from the previous request will have a blank `display_field`.
   Select one of the fields in `data_fields` and make a `PATCH` request to
   `/api/boundaries/{uuid}/` with that value in `display_field`.
   You are now ready to use this Boundary and its associated BoundaryPolygon.

#### BoundaryPolygons

BoundaryPolygons store the Shapefile data associated with a [Boundary](#boundaries),
including geometry and metadata.

Paths:

* List: `/api/boundarypolygons/`
* Detail: `/api/boundarypolygons/{uuid}/`

Query Parameters:

* `boundary`: UUID
    * Filter to Polygons associated with this parent Boundary.

* `nogeom`: Boolean
    * When passed with any value, causes the geometry field to be replaced with
      a bbox field. This reduces the response size and is sufficient for many purposes.

Results fields:

| Field name | Type | Description |
| ---------- | ---- | ----------- |
| `uuid` | UUID | Unique identifier for this BoundaryPolygon. |
| `created` | Timestamp | The date and time when this BoundaryPolygon was created. |
| `modified` | Timestamp | The date and time when this BoundaryPolygon was last modified. |
| `data` | Object | Each key in this Object will correspond to one of the `data_fields` in the parent Boundary, and will store the value for that field for this Polygon. |
| `boundary` | UUID | Unique identifier of the parent Boundary for this BoundaryPolygon. |
| `bbox` | Array | Minimum bounding box containing this Polygon's geometry, as an Array of lat/lon points. This field is optional -- see the `nogeom` parameter above for more details. |
| `geometry` | GeoJSON | GeoJSON representation of this Polygon. This field is optional -- see the `nogeom` parameter above for more details. |

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

### Grout suite

- [Grout Server](https://github.com/azavea/grout-server): An easily-deployable
  standalone instance of a Grout API server.
- [Grout Schema Editor](https://github.com/azavea/grout-schema-editor): A
  purely static app that can read and write flexible schemas from a Grout API.
- [Demo app](https://github.com/jeancochrane/philly-fliers/): A demo project
  providing an example of incorporating the Grout suite into a Vue.js app.

### Historical documents

- [Concept map](./docs/concept-map.md): An early description of the Grout suite
  (formerly known as Ashlar) from an Open Source Fellow working on it during the summer
  of 2018. Describes the conceptual architecture of the suite, and summarizes
  ideas for future directions.

- [Renaming the package to Grout](./docs/rename-package.md): An ADR documenting
  the decision to rename the package from "Ashlar" to "Grout".

- [Evaluating Record-to-Record references](./docs/foreign-keys.md): An ADR
  documenting the reasons and requirements for implementing a Record-to-Record
  foreign key field. See also [the pull request
  thread](https://github.com/azavea/grout-2018-fellowship/pull/34) for further
  discussion.

- [Evaluating alternate backends](./docs/nosql-backends.md): An ADR presenting
  research into possible NoSQL backends and service providers for Grout.

- [Grout 2018 Fellowship](https://github.com/azavea/grout-2018-fellowship): A
  project management repo for working on Grout during Azavea's Summer 2018
  [Open Source Fellowship](https://fellowship.azavea.com). Useful for
  documentation around the motivation and trajectory of the project.

### Roadmap

Want to know where Grout is headed? See the [Roadmap](./docs/roadmap.md) to
get a picture of future development.
