# Roadmap

This document describes our plans for the future development of Grout.

These plans should be considered tentative. There is
no specific release schedule for any of these features; rather, this document
provides a window into where we would like Grout to go in the coming months
and years, divided into near-term, medium-term, and long-term goals.

## Contents

- [Near-term](#near-term)
    - [Bug fixes in the schema editor](#bug-fixes-in-the-schema-editor)
    - [Expose new RecordTypes in the schema editor](#expose-new-recordtypes-in-the-schema-editor)

- [Medium-term](#medium-term)
    - [Full versioning of Records and RecordTypes](#full-versioning-of-records-and-recordtypes)
    - [Improved RecordSchema migration and validation](#improved-recordschema-migration-and-validation)
    - [Evaluate other NoSQL migration frameworks](#evaluate-other-nosql-migration-frameworks)
    - [Publish JavaScript bindings](#publish-javascript-bindings)

- [Long-term](#long-term)
    - [Distribute Android version of the data collector](#distribute-android-version-of-the-data-collector)
    - [Support alternate backends to PostgreSQL](#support-alternate-backends-to-postgresql)
    - [Refactor the schema editor with a modern framework](#refactor-the-schema-editor-with-a-modern-framework)

## Near-term

### Bug fixes in the schema editor

Splitting off the schema editor into its own app revealed a number of bugs,
cataloged on the [Grout Schema Editor issues
page](https://github.com/azavea/grout-schema-editor/issues?q=is%3Aissue+is%3Aopen+label%3Abug).
Clearing out these bugs is high-priority.

### Expose new RecordTypes in the schema editor

As of August 2018, Grout now supports a variety of different geometry types for Records,
in addition to non-temporal RecordTypes. These features are not yet exposed in
the schema editor, however. 

## Medium-term

### Full versioning of Records and RecordTypes

In theory Grout supports full versioning for Records and RecordTypes, but in
practice there is no prior art demonstrating how to implement it. Full
versioning is also not supported in the schema editor. We expect this to be
a fruitful avenue of further work, since full versioning of Records and
RecordTypes would allow for a fully immutable, fully auditable system.

See https://github.com/azavea/ashlar/issues/80 for further discussion.

### Improved RecordSchema migration and validation 

There are some interesting edge cases in validating and migrating Records
to new RecordSchemas, and these edge cases are still ambiguous.
In particular, it's not yet clear how to handle Records whose RecordSchema has
changed, and whether updating the referenced RecordSchema should happen in
the core library or in the schema editor.

See https://github.com/azavea/grout-2018-fellowship/issues/44 for further
discussion.

### Evaluate other NoSQL migration frameworks

Our [research into NoSQL backends](./nosql-backends.md) revealed that geospatial
support has improved in NoSQL databases since 2015. Since MongoDB can now
accomplish much of the work that PostGIS and JSONB fields were doing in Grout,
it seems that Grout's comparative advantages are schema versioning and
schema validation. To continue to build on these advantages, we would like to
put more thought into the migration framework behind Grout (how an end user
can update Records once a schema changes). The first task in this line of
inquiry is to evaluate the landscape and see how contemporary NoSQL backends
manage migrations.

### Publish JavaScript bindings

Grout now has at least two applications built on top of it
([DRIVER](https://github.com/azavea/grout-2018-fellowship/issues/44) and
[Now for Now](https://github.com/jeancochrane/philly-fliers/)), both of which
implement their own custom JavaScript bindings for interacting with the API.
At some point, we would like to formalize these bindings into a separate package
and distribute it on NPM. This would likely increase usability of the Grout
suite for application developers.

## Long-term

### Distribute Android version of the data collector

The initial application built on top of Grout was deployed with an Android app
for performing data collection in the field. This work is encapsulated in the
[`DRIVER-android`](https://github.com/WorldBank-Transport/DRIVER-android)
project, but it is still using a legacy version of Grout and it is
tightly coupled to the DRIVER application.

### Support alternate backends to PostgreSQL

Postgres is a hefty dependency
and a potential barrier to adoption for Grout. We chose it as the backend
for Grout back in 2015, when non-relational databases did not have 
the geospatial support that was necessary for bounding box queries and
arbitrary geometries. However, as our [NoSQL backend
research revealed](./nosql-backends.md), the landscape has changed since,
and it continues to improve: there is at least one alternate backend that could
work for Grout (MongoDB) and some early attempts at managed versions of those
backends (MongoDB Stitch). In 6-12 months, we plan to revisit this research
and decide whether the value proposition of alternative backends has improved.

### Refactor the schema editor with a modern framework

The schema editor runs on AngularJS, which is a JavaScript framework that
has been sunsetted in favor of its successor, Angular. The schema editor uses
AngularJS 1.7, which is an LTS version of AngularJS, so there is no immediate
need to move it to a new framework, but for the long-term health of the
application it would be better to refactor it with a framework that is being
actively developed.
