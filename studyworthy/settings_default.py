"""
Common settings which applies to all environments.
"""

import os

import dj_database_url
import dotenv
import sentry_sdk
from django.utils import timezone
import moneyed

dotenv.load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

if 'SENTRY_DSN' in os.environ:
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import ignore_logger

    sentry_sdk.init(
        dsn=os.environ['SENTRY_DSN'],
        integrations=[DjangoIntegration()],
        send_default_pii=True,
    )
    ignore_logger('django.security.DisallowedHost')

ENVIRONMENT = os.getenv('ENVIRONMENT', 'dev')

if ENVIRONMENT == 'dev':
    SECRET_KEY = os.getenv('SECRET_KEY', '(ok6j_&er=^gsxy8$zia4eqk+%0ucj8n4=s&6k$#jyrmgv(f3s')
    DEBUG = True
else:
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# can be overriden in settings_*.py
DJANGO_DEBUG_TOOLBAR = False

ALLOWED_HOSTS = []
HOSTNAME = os.getenv('HOSTNAME')
if HOSTNAME:
    ALLOWED_HOSTS += [HOSTNAME]

INSTALLED_APPS = [
    'djangocms_admin_style',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'cms',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'easy_thumbnails',
    'djangocms_bootstrap4',

    'djangocms_picture',
    'djangocms_bootstrap4.contrib.bootstrap4_picture',

    'djangocms_file',
    # 'djangocms_icon',
    # 'djangocms_link',
    # 'djangocms_video',

    'crispy_forms',
    'storages',
    'zappa_django_utils',
    'cms_bootstrap',
    # 'timezone_field',
    # 'widget_tweaks',

    'djmoney',
    'djangoapps.erp',
    'djangoapps.lms',
    'djangoapps.lms_cms',
    'djangoapps.crm',
    'djangoapps.campus',
    'djangoapps.siteroot',
]

MIDDLEWARE = [
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
]

AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')

# serving media files
if AWS_STORAGE_BUCKET_NAME:
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.eu-central-1.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # used by S3Boto3Storage as root location
    AWS_LOCATION = os.getenv('MEDIA_LOCATION', 'media')
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.tz',
                'sekizai.context_processors.sekizai',
                'django.template.context_processors.static',
                'cms.context_processors.cms_settings'
            ],
        },
    },
]

ROOT_URLCONF = 'djangoapps.siteroot.urls'
WSGI_APPLICATION = 'studyworthy.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

AUTHENTICATION_BACKENDS = [
    'djangoapps.siteroot.auth.CaseInsensitiveModelBackend'
]

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_TZ = True
USE_I18N = True
USE_L10N = True
LANGUAGES = (
    ('ru', 'ru'),
)

CMS_TOOLBAR_ANONYMOUS_ON = False

CMS_LANGUAGES = {
    ## Customize this
    1: [
        {
            'code': 'ru',
            'name': 'ru',
        },
    ],
    'default': {
        'fallbacks': ['ru'],
        'redirect_on_fallback': False,
        'public': True,
        'hide_untranslated': False,
    },
}

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

PERIODIC_PERIOD_TIMEDELTA = timezone.timedelta(hours=24)

DEFAULT_CURRENCY = moneyed.RUB

APPEND_SLASH = True
SITE_ID = 1

# For bootstrap
CMSPLUGIN_CASCADE_PLUGINS = []

CRISPY_TEMPLATE_PACK = 'bootstrap4'

CMS_TEMPLATES = (
    ('fullwidth.html', 'Fullwidth'),
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

# from here: https://devcenter.heroku.com/articles/heroku-postgresql
db_config = dj_database_url.config(default=None, conn_max_age=60, ssl_require=False)
if db_config:
    DATABASES = {
        'default': db_config
    }
else:
    if ENVIRONMENT not in ['dev', 'test']:
        raise NotImplemented('You cannot run QA/PROD environment with SQLite. Please provide DATABASE_URL')
    DATABASES = {
        'default': {
            'CONN_MAX_AGE': 0,
            'ENGINE': 'django.db.backends.sqlite3',
            'HOST': 'localhost',
            'NAME': 'db.sqlite3',
            'PASSWORD': '',
            'PORT': '',
            'USER': '',
            'TEST': {
                'NAME': 'db-tests.sqlite3',
            }
        },
    }

if ENVIRONMENT == 'dev':
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'root@localhost')
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    DEFAULT_FROM_EMAIL = os.environ['DEFAULT_FROM_EMAIL']
    EMAIL_HOST = os.environ['EMAIL_HOST']
    EMAIL_PORT = os.getenv('EMAIL_PORT', '25')
    EMAIL_HOST_USER = os.environ['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = os.environ['EMAIL_HOST_PASSWORD']
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS')
    EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL')
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
