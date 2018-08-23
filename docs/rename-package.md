# ADR 2: Choosing a new name for Ashlar 

Jean Cochrane (Open Source Fellow, Summer 2018)

## Context

The name `ashlar` [is already taken on PyPi](https://pypi.org/project/ashlar/).
Since PyPi requires unique names for packages, this means that if we want to
distribute our package on PyPi, we'll have to either:

1. Convince the owners of `ashlar` to give it to us
2. Name the PyPi package something similar to `ashlar` but slightly different,
   like `ashlar-core`
3. Come up with a new name for the project

Option 1 seems unlikely, given the maturity of the ashlar package on PyPi and
how recent the last release was (April 2018, less than four months ago). Number
2 is perfectly functional but frustrating from a branding and distribution perspective,
since it has the potential to introduce some confusion and/or competition with
the existing `ashlar` package.

Instead, I believe that the best course of action is to choose option 3 and rename the project.
This will require us to come up with a new name for Ashlar, a [notoriously
difficult decision](https://martinfowler.com/bliki/TwoHardThings.html).

Some options that I considered, all based on the idea of "flexible
construction materials":

- [Joist](https://en.wikipedia.org/wiki/Joist)
- [Lintel](https://en.wikipedia.org/wiki/Lintel)
- [Silicone](https://en.wikipedia.org/wiki/Silicone)
- [Grout](https://en.wikipedia.org/wiki/Grout)

## Decision

I propose that we rename the project to **Grout**. Among the options above,
"Grout" is the name that sounds the best to me, and it's the one that I believe
offers the closest allegory for the project.

Grout is a construction material widely known for its physical flexibility and its
practical versatility: a fluid concrete used to create waterproof seals in
masonry structures.

Some advantages of the name "Grout" include:

- "Grout" respects the origins of the project by referencing a masonry material,
  but unlike "Ashlar", the name "Grout" emphasizes the core features of the project
  -- its flexibility and versatility as a base material
  that can scaffold and tie together much more complex projects.

- "Grout" is one syllable (one fewer than "Ashlar") and the easiest word to
  pronounce among the options I considered.
  
- Perhaps most importantly, `grout` is [available on
  PyPi](https://pypi.org/project/grout).

## Status

Accepted.

## Consequences

- After changing the name, we'll have to take a number of steps to update the
  project:
    - Create a new repo for the project
    - Fork Ashlar and move the code over to Grout 
    - Update the code to refer to `grout` instead of `ashlar` internally in
    all imports and namespaces
    - Rename repos that reference the name "Ashlar", including;
        - `ashlar-2018-fellowship`
        - `ashlar-blueprint`

- Since "Ashlar" is a more esoteric name than "Grout", the package may lose SEO.

- We'll be able to distribute the project on PyPi with a short and memorable
  name.
