# ashlar


## Developing

**Ashlar is under heavy development in tandem with
[DRIVER](https://github.com/WorldBank-Transport/DRIVER); currently the best way to develop
on Ashlar is to set up a DRIVER VM and use that.**

Requires Vagrant 1.5+, Ansible 1.8+ and the following plugins:
  - `vagrant-hostmanager`

Install plugins before `vagrant up` via: `vagrant plugin install <plugin-name>`

App runs on host on port 7000.

A default django superuser will be created, but only on a development provision:
  - username: `admin`
  - password: `admin`

A default OAuth2 application will be created, but only on a development provision.
Navigate to http://localhost:7000/o/applications/ to retrieve the client id/secret after
logging in via http://localhost:70000/admin/


## Production

TODO: Notes on creating a production superuser and adding a production OAuth2 application


## Using OAuth2 / Getting tokens

Get a token:
```
curl -X POST -d "grant_type=password&username=<user_name>&password=<password>" -u"<client_id>:<client_secret>" http://localhost:7000/o/token/
```

Returns:
```
{
    "access_token": "<your_access_token>",
    "token_type": "Bearer",
    "expires_in": 36000,
    "refresh_token": "<your_refresh_token>",
    "scope": "read write groups"
}
```

Making requests with a token:
```
# GET
curl -H "Authorization: Bearer <your_access_token>" http://localhost:7000:/api/record/
curl -H "Authorization: Bearer <your_access_token>" http://localhost:7000:/api/recordschema/
```

Restricted access (disabled in development to allow access to the browsable API):

Add an additional `scope` parameter to token request:
```
curl -X POST -d "grant_type=password&username=<user_name>&password=<password>&scope=read" -u"<client_id>:<client_secret>" http://localhost:7000/o/token/
```

Now, this token will have read-only access to the API.


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
