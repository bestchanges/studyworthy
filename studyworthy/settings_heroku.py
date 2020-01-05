import dj_database_url

from .settings_default import *


def get_from_env(variable_name, default=None):
    if default is not None and variable_name not in os.environ:
        raise NameError(f'{variable_name} env is not defined')
    return os.environ.get(variable_name, default)


SECRET_KEY = get_from_env('SECRET_KEY')

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

# keep uploaded files in Amazon S3
WS_ACCESS_KEY_ID = get_from_env('WS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_from_env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = get_from_env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = get_from_env('AWS_S3_CUSTOM_DOMAIN')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
DEFAULT_FILE_STORAGE = 'lms.storage_backends.S3MediaStorage'

# for serving static files
MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
