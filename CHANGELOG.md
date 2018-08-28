# Changelog

## develop

## 2.0

- Added a validation step to `Record.clean()` method checking whether the `data`
  field of an incoming Record matches its schema [#11](https://github.com/azavea/grout/pull/11)
- Added `geom_intersects` query parameter as an alias to the existing `polygon`
  query parameter for `Record` queries ([#9](https://github.com/azavea/grout/pull/9))
- Changed the date range filters `occurred_min` and `occurred_max` to return
  Records where any part of the date range overlaps the filter range
  ([#9](https://github.com/azavea/grout/pull/9))
- Added validation to ensure that the `occurred_min` query parameter is never later
  than the `occurred_max` query parameter ([#9](https://github.com/azavea/grout/pull/9))
- Added two new fields to the `RecordType` model to support new types of
  Records ([#9](https://github.com/azavea/grout/pull/9)). New fields include:
    1. `temporal`: BooleanField Indicating whether the `Record` has datetime information. If
       this field is `True`, then the `occurred_from` and `occurred_to` fields
       will both be mandatory when creating a new Record. Otherwise, neither
       temporal field will be permitted.
    2. `geometry_type`: ChoiceField offering a selection of different types of
       geometries that can be stored in the Record's `geom` field. The geometry
       of a new Record will be validated based on the value of this field when the Record is
       created. Available options include:
          - Point
          - Polygon
          - MultiPolygon
          - LineString
          - None (no geospatial data)
- Changed the `Record.geom` field to `GeometryField` from `PointField` in order
  to support different types of geometries ([#9](https://github.com/azavea/grout/pull/9))
- Added support for Django 2.0 ([#8](https://github.com/azavea/grout/pull/8))
- Removed external `djsonb` dependency and moved its lookup logic into
  Grout core ([#7](https://github.com/azavea/grout/pull/7)
    - This change involved adjusting imports in old migrations in order to
      remove all references to `djsonb`. Migrating a database initialized under
      the Ashlar project may not work seamlessly.
- Removed extraneous location fields from the `Record` data model (
  [#5](https://github.com/azavea/grout/pull/5)), including:
    - `city`
    - `city_district`
    - `county`
    - `neighborhood`
    - `road`
    - `state`
- Removed the deprecated GeoManager fields on the `Record` and `BoundaryPolygon`
  data models ([#5](https://github.com/azavea/grout/pull/5)). These fields were
  no-ops in Django >1.9, so this change should require no migrations.
- Removed `weather` and `light` fields from the `Record` data model
  ([#85](https://github.com/azavea/ashlar/pull/85))

## 1.0 

Initial release of Grout.
