from .settings_default import *

# TODO: read from secrets
SECRET_KEY = '0(#0qt5n$81v-gc)m^20(kb0wf#*-_%7ou(f5mwrho@=ste^0y'

DEBUG = False

ALLOWED_HOSTS = [
    '.herokuapp.com',
    'studyworthy.herokuapp.com',
    '.studyworthty.xyz',
]

# import django_heroku
# TODO: load like here  django_heroku.settings(locals())
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        'TEST_NAME': os.path.join(BASE_DIR, 'db-test.sqlite3'),
    }
}
