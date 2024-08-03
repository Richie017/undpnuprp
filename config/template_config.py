import os

from config.debug_config import *
from config.path_config import PROJECT_PATH

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_PATH,
            os.path.join(PROJECT_PATH, 'blackwidow', 'core', 'templates/'),
            os.path.join(PROJECT_PATH, 'blackwidow', 'bwroles', 'templates/'),
            os.path.join(PROJECT_PATH, 'blackwidow', 'dbmediabackup', 'templates/'),
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