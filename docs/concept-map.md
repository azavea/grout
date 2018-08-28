# Ashlar concept map

## Summary

In this document I outline my current understanding of Ashlar, its
capabilities, and its relationship to the DRIVER project. Based on my
understanding, I also outline some potential futures for the projects, and
propose next steps for development.

### A note on terminology

In this document, I use "Ashlar" to mean the ongoing open source project that
I'm working on this summer. When I want to refer specifically to the current
implementation of that project, I'll use `ashlar` instead, referencing the
current name of the repo. The distinction strikes me as relevant since it appears
that an important part of the Ashlar development process will involve deciding
what software functionality will precisely constitute "Ashlar," as well as determining
how that functionality should be organized and implemented in code.

## Current understanding of the components comprising Ashlar

As I see it, the Ashlar project is currently comprised of **five interesting 
components** that span three repos: `ashlar`, `DRIVER`, and `djsonb`.
These components include:

1. A schema editing web app, implemented as an AngularJS app in `DRIVER/schema_editor`,
   which exposes admin control over the active schema of `DRIVER` records

2. A dashboard web app, implemented as an AngularJS app in `DRIVER/web`, which
   allows users to browse, filter, and download geospatial data 

3. A standalone Django app, `ashlar`, which exposes a RESTful CRUD API
   for retrieving and updating both A) geospatial records and B) the schema
   composing those geospatial records

4. A standalone Django app, `djsonb`, which provides a Python API for
   performing queries against arbitrarily nested Postgres JSONB fields in
   Django

5. A data collection mobile app, implemented as an Android app in `DRIVER`,
   which produces forms for saving records based on the active schema of
   `DRIVER` records

In my understanding, components 1, 2, and 5 (the schema editor, dashboard, and
mobile app) interoperate through component 3 (`ashlar`) to update and retrieve
records and manage schema for those records. Component 4 (`djsonb`) provides the Python API
for filtering and querying those records, while `ashlar` provides a RESTful
version of this API. 

## Future directions

Based on the 5 components above, I can see a few possible futures for Ashlar,
all of which seem compelling but each of which involves moving the project in
a different direction:

1. Ashlar as an **integrated development toolkit for building apps with
   flexible schemas.** This future seems to be the closest thing to the
   direction that development is currently moving on Ashlar/DRIVER. In this
   future, Ashlar is likely still a Django app, although possibly with more
   backends than just Postgres; it provides an admin backend as well as
   automatic forms for managing schemas. It would be tightly integrated with its
   implementation, opinionated, and a relatively heavy lift to install/deploy,
   although at the same time it would offer the most features in one package.
   It may have an Android toolkit sitting on top of it, too.

1. Ashlar as a **lightweight, JSON-backed database server with dynamic schemas**.
   This future is further away from the present, and involves a slightly more
   abstracted version of Ashlar. In this future, Ashlar wouln't have have to be a 
   Django app; it would  simply be a database server that speaks JSON, both on the
   level of creating/updating records and also managing schema. It could be
   implemented in anything that can talk like a database server.

2. Ashlar as a **data model specification, with many possible implementations**.
   This future is the furthest away, and also the most abstract. Ashlar would be
   a specification for managing flexible schemas and records, and nothing more. 
   It could have implementations in a variety of different languages and frameworks.

In addition to these directions for Ashlar, I also see a few possibilities for
separate repos:

4. Some portion of djsonb as a **simple syntax for querying JSON over a REST API**. 
   Filtering and querying JSON with URL parameters seems like it should be
   a solved problem, but I'm having trouble finding anything good in this space.
   The current Ashlar/djsonb syntax is a bit rushed, but I could imagine putting
   more effort into this and designing a nice spec that could plug into a number
   of different backends, relational or not -- as long as it can store and query
   JSON.

5. Some portion of Ashlar/djsonb as an **automatic filter generator based on
   JSONSchema**. This component of Ashlar is pretty cool, and seems like it
   could be its own thing (possibly a part of or related to 4 above).

I'm curious to hear which of these futures seem the most useful. I'm also
curious whether there are any futures that I've missed.

## Next steps

The [fellowship website](https://fellowship.azavea.com/projects/ashlar) lists
three "phases" for developing Ashlar:

1. Create a data specification for Ashlar data modelling conventions
2. Evaluate a low-cost NoSQL provider to serve as a data layer
3. Create a proof-of-concept app on top of Ashlar, with some options to do
   either a static demo site or a data collection mobile app

Thinking forward, it would make sense to me to engage in rapid development cycles
of these three phases instead of treating them as linear and sequential. I could
imagine a development plan that would look like:

1. Build a quick demo app on top of existing implementation of Ashlar
2. Refine what we want Ashlar to be, including the spec and backend 
3. Develop Ashlar in that direction

Then repeat:

4. Build a second draft of the demo app using the new version of Ashlar
5. Test the app and get feedback
6. Refine Ashlar spec and develop based on feedback

Finally, time permitting:

7. Polish the demo app and build an Android version 
