# Django settings for blackwidow project.
import os

from django.conf.global_settings import AUTHENTICATION_BACKENDS
from django.conf.urls import url, include
from django.utils.translation import ugettext_lazy as _
from config.apps import INSTALLED_APPS as BW_APPS
# from config.apps import INSTALLED_APPS as BW_APPS
from config.celery_config import *
from config.database import DATABASES
from config.database import READ_DATABASE_NAME, EXPORT_DATABASE_NAME, WRITE_DATABASE_NAME, MC_WRITE_DATABAE_NAME, SLAVE_DATABASES
from config.email_config import *
from config.rest_framework_config import REST_FRAMEWORK, API_LOGIN_URL
from config.session import SESSION_ENGINE
from config.test_settings import TEST_RUNNER
from config.theme import *


DEBUG = True
IMEI_AUTHENTICATION_ENABLED = False
CACHE_ENABLED = False
CELERY_ENABLED = True
S3_STATIC_ENABLED = False
CACHE_LOGS = False
LOG_GET_API_CALLS = False

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ADMINS = ()
MANAGERS = ADMINS

ALLOWED_HOSTS = ['*','127.0.0.1']
INTERNAL_IPS = ['127.0.0.1']



APPEND_SLASH = True

TIME_ZONE = 'Asia/Dhaka'
TIME_ZONE_DEFAULT_OFFSET = -360  # 6 hours defference with UTC

SITE_ID = 1
SITE_NAME = 'nuprp.info'
SITE_ROOT = 'https://nuprp.info/'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATABASE_ROUTERS = ['blackwidow.engine.routers.database_router.BWDatabaseRouter']



MEDIA_ROOT = PROJECT_PATH
if S3_STATIC_ENABLED:
    MEDIA_URL = 'static_media/'
else:
    MEDIA_URL = ''
MEDIA_DIR_NAME = 'static_media'

ORGANIZATION_NAME = 'UNDP NUPRP'

SUB_SITE = ''
LOGIN_URL = '/account/login'
z_URL = '/static/'
STATICFILES_DIRS = (os.path.join(PROJECT_PATH, "static/"),)

STATIC_ROOT = os.path.join(PROJECT_PATH, 'static_media/')

# STATIC_UPLOAD_ROOT = os.path.join(STATIC_ROOT, 'uploads/')
STATIC_UPLOAD_ROOT = 'static_media/uploads'

if S3_STATIC_ENABLED:
    from config.aws_s3_config import *

    S3_BASE_URL = 'https://%s/' % (AWS_S3_CUSTOM_DOMAIN)
    STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
    STATIC_UPLOAD_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, STATIC_UPLOAD_MEDIA_DIRECTORY)
    STATIC_EXPORT_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, STATIC_EXPORT_MEDIA_DIRECTORY)
else:
    STATIC_URL = '/static/'
    STATIC_UPLOAD_URL = '/static_media/uploads/'
    STATIC_EXPORT_URL = '/static_media/exported-files/'

STATIC_UPLOAD_TO_PATH = MEDIA_DIR_NAME + os.sep + 'uploads'
EXPORT_FILE_ROOT = os.path.join(PROJECT_PATH, STATIC_ROOT, 'exported-files')
IMAGE_UPLOAD_ROOT = os.path.join(PROJECT_PATH, STATIC_ROOT, 'images')
APK_UPLOAD_ROOT = os.path.join(STATIC_ROOT, 'fieldbuzz_applications/')
APK_UPLOAD_TO_PATH = MEDIA_DIR_NAME + os.sep + 'fieldbuzz_applications'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# from config.template_config import *
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_PATH,
            os.path.join(PROJECT_PATH, 'templates'),
            os.path.join(PROJECT_PATH, 'blackwidow', 'bwroles', 'templates/'),
            os.path.join(PROJECT_PATH, 'blackwidow', 'filemanager', 'templates/'),
            os.path.join(PROJECT_PATH, 'blackwidow', 'dbmediabackup', 'templates/'),
            os.path.join(PROJECT_PATH, 'blackwidow', 'undp_nuprp/reports', 'templates/'),
            os.path.join(PROJECT_PATH, 'dynamic_survey', 'templates/'),

        ],
        # 'APP_DIRS': True,
        # 'TEMPLATE_DEBUG': DEBUG,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'debug': DEBUG
        },
    },
]

SECRET_KEY = 'xyY`:D%;EAeytq?oBph0N?.mRDe)zF_irznkTO`Bt~?J#6,@<T'

MIDDLEWARE_CLASSES = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'silk.middleware.SilkyMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'blackwidow.core.middlewares.ProtectedFormPostMiddleWare',
    'blackwidow.core.middlewares.MasterSlaveDBMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    # 'simple_history.middleware.HistoryRequestMiddleware',
    'crequest.middleware.CrequestMiddleware',
)

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    # 'cachalot.panels.CachalotPanel',
]

AUTHENTICATION_BACKENDS += (
    "allauth.account.auth_backends.AuthenticationBackend",
)

AUTH_PROFILE_MODULE = 'core.ConsoleUser'

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'modeltranslation',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'widget_tweaks',
    'django_tables2',
    'djcelery',
    'kombu.transport.django',
    'extra_views',
    'rest_framework',
    'rest_framework.authtoken',
    'blackwidow.scheduler',
    'crequest',
    'taggit',
    'debug_toolbar',
    # 'django.contrib.gis',
    # 'cachalot',
    # 'silk',
)

INSTALLED_APPS += BW_APPS

FILE_UPLOAD_HANDLER = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

LANGUAGE_CODE = 'en'
gettext = lambda s: s
LANGUAGES = (
    ('en', gettext('English')),
    ('bd', gettext('Bangla')),
)
SECONDARY_LANGUAGE = 'bangla'
MODELTRANSLATION_LANGUAGES = ('en', 'bd')
MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'

RENDER_SORT_ENABLED = False

SYSTEM_USER_USERNAME = 'blackwidow'

# specify app to generate model and forms for all roles under this app directory
ROLES_APP = 'blackwidow.bwroles'

if CACHE_ENABLED:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    from config.cache_config import *

    # from cachalot.api import invalidate
    # from cachalot.signals import post_invalidation
    # from django.dispatch import receiver
    #
    #
    # @receiver(post_invalidation)
    # def invalidate_replica(sender, **kwargs):
    #     if kwargs['db_alias'] == 'default':
    #         invalidate(sender, db_alias='replica')
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# import db backup restore configurations:
from config.dbbackup_restore_config import *
from config.map_config import *
from config.menu_config import *
from config.model_json_cache import *

# POSTGIS_TEMPLATE = 'bw_nuprp'

# DATABASES['default'] = dj_database_url.config()
# DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'

# django_heroku.settings(locals())
