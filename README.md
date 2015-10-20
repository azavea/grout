# ashlar

[![Build Status](https://travis-ci.org/azavea/ashlar.svg?branch=develop)](https://travis-ci.org/azavea/ashlar)

## Developing

**Ashlar is under heavy development in tandem with
[DRIVER](https://github.com/WorldBank-Transport/DRIVER) and
[djsonb](https://github.com/azavea/djsonb); currently the best way
to develop on Ashlar is to set up a DRIVER VM and use that.**


## Testing

1. Install [docker](http://docs.docker.com/installation/ubuntulinux/) and
   [docker-compose](https://docs.docker.com/compose/install/)
2. From the root project directory, run `docker-compose run test` (or `docker-compose
   up`). You may need to use sudo depending on how you've configured Docker.

You should expect to see duplicate key errors from the db container; these are generated
deliberately by the test suite and can be safely ignored.

If you encounter connection-refused errors, try re-running the test command;
docker-compose will launch the postgres container first, but sometimes postgres doesn't
become available quickly enough for Django to connect to it. Re-running will usually work.

If your tests crash and leave a `test_postgres` database lying around that prevents you
from running further tests, the simplest solution is to run `docker-compose rm db`, which
will delete the database container and refresh it from the base image. You may also be
able to run tests interactively by running `docker-compose run test python
/opt/ashlar/run_tests.py`, which would allow you to manually delete the database when
prompted.


## Testing on OSX

1. Install docker toolbox (https://www.docker.com/toolbox).
2. Run a terminal window through Docker Quickstart Terminal and create a docker machine for ashlar:
`docker-machine create ashlar -d virtualbox`
3. Start the virtualbox VM:
`docker-machine start ashlar`

If you see Started machines may have new IP addresses. You may need to re-run the docker-machine env command in the terminal: `eval "$(docker-machine env mub-monitor)"`
4. Finally, to run tests, `docker-compose run test`

