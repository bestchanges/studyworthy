import dj_database_url

from .settings_default import *

if not 'SECRET_KEY' in os.environ:
    raise NameError('SECRET_KEY not found')
SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = [
    '.herokuapp.com',
    'studyworthy.herokuapp.com',
    '.studyworthty.xyz',
]

# from here: https://devcenter.heroku.com/articles/heroku-postgresql
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}
