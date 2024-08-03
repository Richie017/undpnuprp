from settings import SITE_NAME

# db backup configurations:

# custom dropbox storage config start
DBBACKUP_STORAGE = 'blackwidow.dbmediabackup.utils.storages.dropbox.BWDropBoxStorage'
DBBACKUP_STORAGE_OPTIONS = {
    'oauth2_access_token': '<PUT YOUR DROPBOX KEY HERE>',
    'root_path': '/fieldbuzz/' + SITE_NAME + '/'
}
# custom dropbox storage config end

COMPRESS_CLEANUP_OPTIONS = {
    'compress': False,
    'clean': False
}

DBBACKUP_CONNECTORS = {
    'default': {
        'CONNECTOR': 'blackwidow.dbmediabackup.db.postgresql.BWPgDumpBinaryConnector'
    },
}

DBBACKUP_CLEANUP_KEEP = 30
DBBACKUP_CLEANUP_KEEP_MEDIA = 30
DBBACKUP_FILENAME_TEMPLATE = '{databasename}-{servername}-{datetime}.{extension}'
MEDIA_FILENAME_TEMPLATE = '{servername}-{datetime}.{extension}'
DBBACKUP_TMP_FILE_MAX_SIZE = 10*1024*1024 # default is 10 MB, please update if necessary

DBBACKUP_MEDIA_PATH = 'static_media'
DBBACKUP_HOSTNAME = SITE_NAME