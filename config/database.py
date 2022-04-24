__author__ = 'activehigh'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nuprp_local_new',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
        },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nuprp_local_new',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
        }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         # 'ENGINE': 'django.db.backends.postgresql',
#         # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'bw_nuprp',
#         'USER': 'postgres',
#         'PASSWORD': '5Up5PNBU55',
#         #'PASSWORD': 'undpadmin4axiz',
#         #'HOST': 'localhost',
#         'HOST': 'nuprpdb.cvxkbdbtuooz.ap-southeast-1.rds.amazonaws.com',
#         'PORT': '5432',
#         },
#     'replica': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         # 'ENGINE': 'django.db.backends.postgresql',
#         # 'ENGINE': 'django.contrib.gis.db.backends.postgis',
#         'NAME': 'bw_nuprp',
#         'USER': 'postgres',
#         #'PASSWORD': 'undpadmin4axiz',
#         'PASSWORD': '5Up5PNBU55',
#         'HOST': 'nuprpdb.cvxkbdbtuooz.ap-southeast-1.rds.amazonaws.com',
#         #'HOST': 'localhost',
#         'PORT': '5432',
#         }
# }

READ_DATABASE_NAME = 'default'
WRITE_DATABASE_NAME = 'default'
EXPORT_DATABASE_NAME = 'default'
MC_WRITE_DATABAE_NAME = 'default'
SLAVE_DATABASES = ['replica']