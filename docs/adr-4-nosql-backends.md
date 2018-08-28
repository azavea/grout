# ADR 4: Supporting NoSQL backends

Jean Cochrane (Open Source Fellow, Summer 2018)

## Context

Grout is currently tightly coupled to a PostgreSQL dependency. Postgres is a powerful
database engine, but it's also difficult to deploy, and potentially a serious
barrier to adoption for Grout.

To make Grout even easier to use, we would like to [support NoSQL
backends](https://github.com/azavea/grout-2018-fellowship/issues/13). However,
for a NoSQL backend to be feasible, it must provide support for a few key
Grout functions:

1. Storing geospatial data
2. Querying geospatial data
3. Querying complex JSON data, including:
    - Nested search (e.g. find the value of `baz` in`{"foo": {"bar": {"baz": 1}}}`)
    - Compound rules (`foo AND bar OR baz`)
4. (Optional) JSONSchema support

In addition, NoSQL backends should be considered based on how much value they
bring to the project, including:

4. How easy the backend is to configure and deploy
5. How cheap it is to use, if not free 

In this document, I look at a few different options for [NoSQL
backends](#backends), including:

- MongoDB
- CouchDB
- Google Cloud Firestore
- AWS DynamoDB
- JSONBin

After eliminating options that cannot support the basic requirements of Grout,
I then evaluate [cloud providers](#providers). Finally, I [consider the
value](#value) that a NoSQL backend would bring to the project.

### Backends 

#### MongoDB

[MongoDB](https://www.mongodb.com/what-is-mongodb) is an open-source
nonrelational database that stores data in a JSON-like format. It translates
JSON objects into "documents," which are organized in "collections." 

Here's how it scores on the requirements:

1. Geospatial data ✔️
    - MongoDB can store [arbitrary
      GeoJSON](https://docs.mongodb.com/manual/geospatial-queries/#geospatial-data),
      meaning that points and polygons are supported.

2. Geospatial queries ✔️
    - MongoDB supports geospatial querying for [`intersection`, `within`, and
      `near` queries](https://docs.mongodb.com/manual/geospatial-queries/#id1).
    - Queries make use of GeoJSON objects for comparison operations.

3. Querying JSON ✔️
    - Run queries on [nested fields](https://docs.mongodb.com/manual/tutorial/query-embedded-documents/#query-on-nested-field).
    - Supports [AND conditions](https://docs.mongodb.com/manual/tutorial/query-embedded-documents/#specify-and-condition).
    - Supports [logical OR conditions](https://docs.mongodb.com/manual/reference/operator/query/or/).

4. JSONSchema support ✔️
    - As of v3.6, MongoDB supports JSONSchema for [validating `create` and `update`
      operations](https://docs.mongodb.com/manual/reference/operator/query/jsonSchema/).
    - Draft 4 is supported, but with "some limitations". The documentation
      doesn't describe what those limitations are, however.

#### CouchDB

[CouchDB](https://couchdb.apache.org/) is an open-source nonrelational 
database, similar to MongoDB. Its focus is on supporting highly-distributed
databases. All data is stored as JSON-like "documents" in the database, which is
queryable over a REST API.

1. Geospatial support ❓
    - Provided through an official plugin, [GeoCouch](https://github.com/couchbase/geocouch/)
    - Documentation is [not great](https://github.com/couchbase/geocouch/blob/master/gc-couchdb/README.md),
      only distributed through GitHub, no new tagged releases since 2013

2. Geospatial queries ❓
    - GeoCouch can [save points and return bounding box
      requests](https://github.com/couchbase/geocouch/blob/master/gc-couchdb/README.md)

3. Querying JSON ✔️
    - Query capability is powerful but [quite
      esoteric](http://docs.couchdb.org/en/2.1.2/query-server/protocol.html#map-doc)
    - A third-party JavaScript API, [PouchDB](https://pouchdb.com/), is
      available.

4. JSONSchema support ❌
    - External references are possible, and you can define validation functions
      for `create` and `update` operations, so we could [hack together our own
      schema solution](https://developer.ibm.com/dwblog/2012/schemas-in-couchdb/).
      But nothing comes out of the box.

#### Google Cloud Firestore

[Google Cloud Firestore](https://cloud.google.com/firestore/docs/) is
a proprietary nonrelational database service provided by Google. It uses a data model
very similar to MongoDB, where objects are stored as "documents" inside of
"collections." It is currently in beta.

1. Geospatial support ❓
    - Firestore has a type for [lat/lng
      coordinates](https://cloud.google.com/firestore/docs/concepts/data-types).
      Presumably they're stored as WebMercator, but there's not much
      information.
    - Firestore does not support polygons.

2. Querying geospatial data ❌
    - Seems to not be possible. I can't find any documentation or blog posts
      on the issue.

3. Querying JSON ❓
    - Firestore has a few [serious
      limitations](https://firebase.google.com/docs/firestore/query-data/queries#query_limitations):
        - Cannot query across multiple collections
        - Cannot support range filters on multiple fields
        - Cannot support logical `OR` queries (reccommends performing multiple
          queries and merging them client-side, but that may not work for all
          use cases)

4. JSONSchema support ❌
    - No results [in the
      search](https://cloud.google.com/s/results/?q=jsonschema&p=%2Ffirestore%2F)/
    - You can define validation patterns as [security
      rules](https://cloud.google.com/firestore/docs/manage-data/transactions?authuser=0&hl=ru#data_validation_for_atomic_operations),
      but you have to use Firestore's idiomatic security rule syntax.

#### AWS DynamoDB

[DynamoDB](https://aws.amazon.com/dynamodb/) is a proprietary nonrelational database
provided as a service by Amazon Web Services. It supports key-value- and
document-based data storage. Objects are stored as _items_ in _rows_, where they
are queried by a primary key. It is designed to easily integrate with other
AWS products.

1. Geospatial support ❓
    - DynamoDB supports [geohashes for point
      geometries](https://aws.amazon.com/about-aws/whats-new/2013/09/05/announcing-amazon-dynamodb-geospatial-indexing/).
    - No support for polygons.
    
2. Geospatial queries ❓
    - Relies on [a third-party Java library that is sparsely
      documented](https://blog.corkhounds.com/2017/06/19/geospatial-queries-on-aws-dynamodb/).
    - Allows searching for coordinates within a radius or a box. 

3. Querying JSON ❓
    - Some limitations:
        - Queries only search items attached to a primary key.
        - Queries can retrieve a maximum of 1MB of data, which raises a
          question for images.
    - True to AWS form, [the query docs are a slog to
      decipher](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.html).
      As a result, I'm not confident I fully understand the capability here.

4. JSONSchema support ❌
    - [No schema validation
      whatsoever](https://stackoverflow.com/questions/42563529/is-there-a-way-to-enforce-a-schema-constraint-on-an-aws-dynamodb-table).

#### JSONBin

JSONBin is a [JSON-store-as-a-service](https://jsonbin.org/) that allows
developers to easily store and retrieve JSON data over a REST API. In this
sense, it is most like a serverless JSON datastore. It requires
no configuration, and has a built-in permissions and token authentication
system. Its main focus is simplicity and ease-of-use.

1. Geospatial support ✔️
    - Since JSONBin stores documents as pure JSON, GeoJSON is inherently
      supported.

2. Geospatial queries ❌
    - Querying is [on the product roadmap](https://jsonbin.io/roadmap), but
      is not currently supported.

3. Querying JSON ❌
    - Querying is [on the product roadmap](https://jsonbin.io/roadmap), but
      is not currently supported.

4. JSONSchema support ❌
    - No mention of validation in the [API documentation](https://jsonbin.io/api-reference).

### Providers

Based my research summarized above, **MongoDB is the only backend I considered
that supports all project requirements.** As such, I only considered cloud
providers for MongoDB.

There are two main cloud providers for MongoDB: MongoDB Atlas, a hosting service
provided by MongoDB itself, and mLab, a third-party service.

#### mLab

To read an argument in favor of mLab, see [mLab's account of why it's better than MongoDB
Atlas](https://mlab.com/mlab-vs-atlas/)

- **Pros**:
    - Free, non-expiring [sandbox account](https://mlab.com/plans/pricing/#plan-type=sandbox).
        - Up to 500MB storage with shared hosting and variable RAM.
    - [Integrates with AWS](https://docs.mlab.com/), and is quick and easy
      to set up. 

- **Cons**:
    - Provided by a third-party.
    - Lags behind the current release of MongoDB.
        - However, 3.6 will be available for sandbox accounts as of July 20th.

#### MongoDB Atlas

To read an argument in favor of MongoDB Atlas, see [MongoDB Atlas' account of
why it's better than mLab](https://www.mongodb.com/cloud/atlas/compare). 

- **Pros**:
    - Provided by the MongoDB team.
    - [Integrates with AWS](https://docs.atlas.mongodb.com/getting-started/#for-cloud-provider-region-select-your-preferred-cloud-provider).
    - [Slightly complicated to set up](https://docs.atlas.mongodb.com/getting-started/),
      but still very easy relative to hosting your own database.
    - Integrates with [MongoDB Stitch](https://docs.mongodb.com/stitch/), a
      serverless backend-as-a-service for MongoDB applications.

- **Cons**:
    - The free tier comes with [some major
      limitations](https://docs.atlas.mongodb.com/reference/free-shared-limitations/):
        - "Idle instances" may be terminated.
        - No backups.
        - Max throughput of 100 writes/sec.
        - Data transfer limit of 10GB/week.

### Value

The two main goals of supporting a NoSQL backend include:

1. Making Grout easier to configure and deploy
2. Abstracting the data model such that it could be applied to more backends
   in the future

I'll look at each of these goals in detail.

#### Making Grout easier to configure and deploy

- **Pros**:
    - MongoDB is slightly easier to configure than Postgres. However, it
      still requires [some configuration](https://docs.mongodb.com/manual/reference/configuration-options/)
      from the developer.

- **Cons**:
    - A database server still must be deployed to interact with the database.
      This means that the developer must still deploy a database and a database
      server in addition to the frontend.
    - MongoDB offers a serverless framework, MongoDB Stitch, which exposes an API
      [that can be queried from the client 
      side](https://docs.mongodb.com/stitch/getting-started/configure-rules-based-access-to-mongodb/).
      Using a "serverless" pattern like this would be a substantial improvement on
      the existing development framework, but moving in this direction would
      require the Grout NoSQL backend to be tightly coupled to a certain provider
      (MongoDB Stitch), and would introduce another layer of integration that would
      slow the development process.

**Overall score**: Medium-low.

#### Abstracting the data model

- **Pros**:
    - Using MongoDB would let us represent the data model in JSONSchema
      and validate it on the backend. This would be a big win for
      generalizability.

- **Cons**:
    - JSONSchema is not widely supported among NoSQL providers, according to
      my research.

**Overall score**: Medium.

## Decision

Based on my research, I recommend that if we move forward with a NoSQL backend,
we should build it on top of **MongoDB**. While there is promising work being
done on many nonrelational databases, MongoDB is currently the only NoSQL database
that satisfies all project requirements.

While MongoDB satisifes the project requirements, however, I'm still uncertain
whether the value proposition is strong enough that we should prioritize this
work. It seems to me that MongoDB will only present a strong value proposition
if the backend component can be eliminated completely from the infrastructure
provisioning; otherwise, deploying a NoSQL database requires essentially the
same amount of work. With MongoDB, this is technically possible with the **Atlas and
Stitch serverless stack**; however, choosing this stack will require
integrating with two separate services, making the work much more complex and
introducing an undesirable coupling to the application.

## Status

In review.
