__author__ = 'mahmudul'

CACHES = {
    # 'default': {
    #     'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
    #     'LOCATION': 'django_cache',
    # }
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}