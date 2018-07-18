"""
Sample Django settings for generating migrations for the grout project.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

# You won't deploy this app to production alone, so don't worry about the
# secret key.
SECRET_KEY = 'super duper secret'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grout',
]

# Default database variables correspond to the development database set up
# in docker-compose.yml
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PASSWORD': '',
        'PORT': '5432'
    }
}

# Grout-specific variables
GROUT = {
    'SRID': 4326
}
DEVELOP = True
