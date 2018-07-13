# Grout 

[![Build Status](https://travis-ci.org/azavea/grout.svg?branch=develop)](https://travis-ci.org/azavea/grout)

## Developing

**Grout is under heavy development in tandem with
[DRIVER](https://github.com/WorldBank-Transport/DRIVER) and
[djsonb](https://github.com/azavea/djsonb); currently the best way
to develop on Grout is to set up a DRIVER VM and use that.**

## Testing

### Requirements

- [Docker](http://docs.docker.com/installation/ubuntulinux/)
- [docker-compose](https://docs.docker.com/compose/install/)

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
