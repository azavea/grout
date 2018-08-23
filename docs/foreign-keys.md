# ADR 3: Extending the `relationship` field to allow Record-to-Record references 

Jean Cochrane (Open Source Fellow, Summer 2018)

## Context

In [#32](https://github.com/azavea/grout-2018-fellowship/issues/32),
I introduced a proposal to extend the `relationship` field to allow references
to other Records in the datastore. This ADR investigates whether that feature
is possible, and proposes next steps for it.

### Background

The basic idea of a Record-to-Record reference is to permit one Record to
point to another. For example, imagine two RecordTypes that store data about
Events as well as the advertisements for those events, Posters:

- Poster
    - `image`: Image
    - `date`: DateTime
    - `location`: Coordinates

- Event
    - `title`: String
    - `date`: DateTime
    - `location`: Coordinates

A Record-to-Record reference would allow us to link Posters to the Events
that they represent:

- Poster
    - `image`: Image
    - `date`: DateTime
    - `location`: Coordinates
    - **`event`**: **UUID**

Then, Posters could be grouped, searched, and filtered according to the Event
that they reference.

#### Implementation description

Currently, references are implemented under the `localReference` data type in
the schema editor (titled `Relationships`) and only permit references to
fields contained within the referencing Record itself.

In the schema editor, Record-to-Record foreign keys could be represented in a new field, such as
`externalReference`, with a schema definition along these lines:

```json
"externalReference": {
    "allOf": [
        { "$ref": "#/definitions/abstractBaseField" },
        { "$ref": "#/definitions/abstractRequirableField" }
    ],
    "title": "Record-to-Record Relationship",
    "properties": {
        "fieldTitle": {
            "title": "Relationship Title",
            "type": "string",
            "minLength": 1
        },
        "recordType": {
            "allOf": [{
                "$ref": "https://<grout-server-hostname>/api/record-types/referents.json"
            }]
        }
        "fieldType": {
            "options": {
                "hidden": true
            },
            "type": "string",
            "enum": ["externalReference"]
        }
    }
}
```

The `/api/record-types/referents.json` endpoint would return a list of available
RecordTypes that the user can select from in order to choose a value for
the `recordType`. Output from the endpoint would look like this:

```json
{
    "title": "RecordType of the related Record",
    "type": "string",
    "format": "select",
    "enumSource": [{
        "source": [
            {
                "title": "<RecordType.title>",
                "value": "<RecordType.uuid>"
            },
            ...More RecordTypes from the API
        ]
    }]
}
```

Then, when saving out the final schema in `schemas-service.js`, the
RecordType UUID that the user had selected in the `recordType` field would be used to define
the available Record values for reference. Again, the schema would make use of the
`$ref` attribute to load valid Records dynamically through a Grout API endpoint
during validation:

```javascript
{
    "<propertyName>": {
        "allOf": [{
            "$ref": "https://<grout-server-hostname>/api/record-types/<UUID>/referents.json"
        }]
    }
}
```

In this case, the `/api/record-types/<UUID>/referents.json` endpoint would
resolve to a type definition listing available Records: 

```
{
    "type": "string",
    "format": "select",
    "enumSource": [{
        "source": [
            {
                "title": "<Digest for the Record>"
                "value": "<Record UUID>"
            },
            ...More records from the API
        ]
    }]
}
```

Some import considerations for this pattern:

- Unlike in [Derek's initial comment suggesting this
  pattern](https://github.com/azavea/grout-2018-fellowship/pull/34/files#r203071181),
  there would have to be changes to the schema editor (specifically
  `schemas-service.js`) in order to support the new fields. This is necessary
  because there has to be point in the process that takes the RecordType selected by the user
  and translates it into a `$ref` endpoint for validating Records. However,
  this approach still has the benefit of leveraging `$ref` to push all of
  the validation burden onto the JSON Schema, without having to write custom
  validators.

- It's not totally clear to us yet whether validation with external `$refs`
  will work in JSONSchema draft 4, which is the latest version supported by
  JSON Editor. See [this thread](https://github.com/azavea/grout-2018-fellowship/pull/34/files#r203071181)
  for some discussion. Reference validation needs to be confirmed before
  moving ahead with this pattern.

- Assuming Records are append-only, meaning they cannot be deleted from the
  database through the Grout API, this pattern should always validate properly
  as long as the `/api/record-types/<UUID>/referents.json` endpoint returns a
  list of all active Records as well as all archived Records. However, returning
  all Records for a RecordType regardless of whether or not they're active could
  potentially be confusing for an end user doing data collection work, both
  because it might be hard to tell which Records are active and because the
  endpoint may return overwhelmingly large lists of Records. Records
  returned from the API will have to be easily distinguishable based on whether
  or not they are active, and ideally the data collection UI should allow the
  Record to be filled out by an autocomplete search.

- In applications where the list of available Records can grow very large,
  performance of the `referents.json` endpoints could cause problems with
  client wait time and server memory. These endpoints should be profiled
  for performance.

- This pattern assumes that the `referents.json` endpoints are fully public,
  which could be a problem for applications with sensitive data. In an ideal
  world, an admin would be able to set the permissions for these endpoints.

#### Requirements

For Record-to-Record foreign keys to be workable, they need to permit three basic
operations:

1. **Filtering**: Foreign key relationships need to support nested search and
   filtering to match the rest of the Grout field types.
2. **Validation**: When an incoming record includes a foreign key, the validation function
   (`grout.models.SchemaModel.validate_schema`) needs to be able to check
   whether the referent exists in the database.
3. **Indexing**: Database lookups based on foreign keys must be performant.
   Without a way to index foreign key relationships, lookups may not be
   reasonable in large production systems. 

#### A brief note on null pointers

One operation that didn't make this list is **Resolution of null pointers**.
Null pointers are a classic problem with non-relational data stores: if document
A points to document B, and then document B is removed from the system, NoSQL
databases offer no system for automatically resolving the null reference
(whether by raising an error, setting a default, or simply storing a `NULL`
value for the foreign key). In the example given above, we could imagine a user
deleting an Event referenced by a Poster, and then the UUID stored in
`Poster.event` would not reference a coherent entity in the database.

Null pointers might appear to be an issue for Record-to-Record references --
however, the Grout data model provides an avenue for easily protecting against
the problem through the **`Record.archived` field**. When a user tries to delete
a Record from the schema editor UI, it sets the Record to `archived = True`
instead of deleting it; this behavior means that Grout is functionally an
append-only system. Because of this, references should always validate
correctly.

In spite of the append-only nature of the UI, there's still a chance that an
authorized user could delete a Record by issuing a `DELETE` command directly
to the API. To fully protect against null pointers, the Grout API should be
updated to either A) deny these requests or B) handle `DELETE` requests the
same way they're handled in the UI: by setting `archived = True`.

### Evaluating the requirements

#### Filtering 

Since Record-to-Record references would store UUIDs (as strings) for the
referent Record, simple filtering should be the same for Record-to-Record
references as for any other Grout JSON field. Namely, all of the same [Django
JSONField operations](https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/fields/#querying-jsonfield)
apply, including:

- Field lookups:

```python
Record.objects.filter(data__<reference_field>=uuid)
```

- Containment operations:

```python
Record.objects.filter(data__contains={'<reference_field>': uuid})
```

- Key lookups (equivalent to Postgres' `?` operator):

```python
Record.objects.filter(data__has_key='<reference_field>')
```

Some limitations to filtering JSONFields exist. In particular, since the parser
assumes the filter (like `data__<reference_field>`) is a nested JSON path,
[the standard set of field
operations](https://docs.djangoproject.com/en/2.0/topics/db/queries/#field-lookups)
is not available; JSONField is limited to the operations listed above. However,
SQL utilities like `Case`, `Where`, and aggregation functions work as expected,
assuming that the lookup follows the JSONField-specific format.

#### Validation

There are two approaches we could take to validation. The first is to extend
the [Python jsonschema package](https://python-jsonschema.readthedocs.io), which has
no built-in support for validating foreign keys but does expose
a `RefResolver` class that it uses in the `validate` function for [resolving external
references](https://python-jsonschema.readthedocs.io). One possibility would be
to  extend this resolver to validate references by pinging the Grout
API.

- Pros:
    - Easy integration with existing jsonschema validation
    - Minimal changes to the application code

- Cons:
    - Extending a third-party package risks introducing technical debt
    - Pushes core logic to a third-party package

Another approach would be to use the built-in `$ref` keyword to resolve
references as described
[in the implementation section above](#implementation-description). This would
require adding new endpoints to the Grout API for facilitating validation via
the JSONSchema `$ref` attribute.

- Pros:
    - Makes validation logic declarative and more explicit
    - Keeps validation tied to the schema, and so enforces separation of
      concerns
    - Abstracts validation away from the python-jsonschema implementation,
      meaning that any JSONSchema validator could validate it 
- Cons:
    - Still unclear whether external `$ref` references are supported in
      json-editor, and to what degree

#### Indexing

PostgreSQL [supports indexing on jsonb
fields](https://www.postgresql.org/docs/9.4/static/datatype-json.html#JSON-INDEXING)
using GIN indexes. There are even three different degrees of flexibility with
jsonb indexes:

- Key-value index on all keys and values (the default: most flexible, least performant)
- Key-value index with expression indexes, which will restrict the index to
  a certain set of pre-defined key-value pairs (medium flexible, medium performant)
- `jsonb_path_ops` indexes, which only support the containment operator `@>`
  but are much faster (least flexible, most performant)

Since we currently only use the containment operator in Grout anyway, we may
be able to use the most performant `jsonb_path_ops` GIN index type.

- Pros:
    - Seems like jsonb supports the kind of indexing we need out of the box

- Cons:
    - I don't understand indexing very well, and there's a chance that I'm
      reading the docs too optimistically
    - Hard to get a sense of actual performance without running tests

If performance is not an issue, as Derek has suggested may be the case, then

## Decision

Based on my research, I recommend moving forward with Record-to-Record
foreign keys in Grout by **leveraging the `$ref` keyword and Grout API
endpoints to support a new field type**.

To facilitate this work, we should prioritize [migrating
to Django's built-in jsonb type](https://github.com/azavea/grout-2018-fellowship/issues/12)
so that we are using the most up-to-date functionality. Next steps include:

1. Migrate to Django's built-in jsonb type ✔️
2. Do a proof-of-concept test to confirm that `$ref` references validate in
   json-editor
    - If the test succeeds:
        - Implement Grout API endpoints for serving `$ref` validations
    - Else:
        - Extend `RefResolver` in jsonschema to write a custom resolver for Record-to-Record
          references
3. Create an index on the `data` fields of the Record and RecordSchema data types
4. Update the schema editor data model to permit Record-to-Record references
5. Update the schema editor UI to expose Record-to-Record references

## Status

In review.

## Consequences

- A new feature in Grout that will likely take 3-4 days to implement
  and test properly.

- Updates to the schema editor to accommodate the new feature.
