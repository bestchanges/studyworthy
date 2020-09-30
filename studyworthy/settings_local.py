from .settings_default import *

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '[::1]',
]

INSTALLED_APPS += ['behave_django']

DJANGO_DEBUG_TOOLBAR = os.environ.get('DJANGO_DEBUG_TOOLBAR', False)
if DJANGO_DEBUG_TOOLBAR:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

    INTERNAL_IPS = ('127.0.0.1',)
