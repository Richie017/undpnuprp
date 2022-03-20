__author__ = 'activehigh'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bw_nuprp_new',
        'USER': 'postgres',
        'PASSWORD': 'undpadmin4axiz',
        'HOST': 'localhost',
        'PORT': '5432',
        },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bw_nuprp_new',
        'USER': 'postgres',
        'PASSWORD': 'undpadmin4axiz',
        'HOST': 'localhost',
        'PORT': '5432',
        }
}

READ_DATABASE_NAME = 'default'
WRITE_DATABASE_NAME = 'default'
EXPORT_DATABASE_NAME = 'default'
MC_WRITE_DATABAE_NAME = 'default'
SLAVE_DATABASES = ['replica']