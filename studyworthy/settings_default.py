"""
Common settings which applies to all environments.
"""

import os

import dotenv
import sentry_sdk
from django.utils import timezone
import moneyed
from sentry_sdk.integrations.django import DjangoIntegration

dotenv.load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if 'SENTRY_DSN' in os.environ:
    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration()]
    )

FIXTURE_DIRS = (
)

INSTALLED_APPS = [
    'djmoney',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'social_django',
    'bootstrapform',
    'djangoapps.common',
    'djangoapps.lms',
    'djangoapps.crm',
    'djangoapps.campus',
    'djangoapps.siteroot',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'studyworthy.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'studyworthy.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'djangoapps.lms.auth.BearerTokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
SOCIAL_AUTH_AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
SOCIAL_AUTH_AUTH0_KEY =  os.environ.get('AUTH0_CLIENT_ID')
SOCIAL_AUTH_AUTH0_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')

SOCIAL_AUTH_AUTH0_SCOPE = [
    'openid',
    'profile',
    'email'
]

AUTHENTICATION_BACKENDS = [
    'djangoapps.siteroot.auth0backend.Auth0',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/login/auth0'
LOGIN_REDIRECT_URL = '/dashboard'

AUTH_USER_MODEL = 'siteroot.SiteUser'

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_TZ = True

USE_I18N = True
USE_L10N = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

PERIODIC_PERIOD_TIMEDELTA = timezone.timedelta(hours=24)

DEFAULT_CURRENCY = moneyed.RUB
