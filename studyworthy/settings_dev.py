from .settings_default import *
DEBUG = True

SECRET_KEY = '0(#0qt5n$81v-gc)m^20(kb0wf#*-_%7ou(f5mwrho@=ste^0y'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]',
    '.studyworthty.xyz',
]

INSTALLED_APPS += ['behave_django']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
