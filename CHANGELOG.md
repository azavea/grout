# Changelog

## 2.0dev

Changes we're making en route to version 2.0. When we cut a release, this
section will form the changelog for v2.0.

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
