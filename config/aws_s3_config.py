__author__ = 'Ziaul Haque'

AWS_ACCESS_KEY_ID = '<put your access key here>'
AWS_SECRET_ACCESS_KEY = '<put your secret access key here>'
AWS_STORAGE_BUCKET_NAME = '<put your storage bucket name here>'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_MODEL_JASON_DIR = AWS_LOCATION + '/model_data/'
AWS_STATIC_JS_DIR = AWS_LOCATION + '/js/constant/'
MEDIA_DIRECTORY = "media/"
STATIC_MEDIA_DIRECTORY = MEDIA_DIRECTORY + "static_media/"
STATIC_UPLOAD_MEDIA_DIRECTORY = STATIC_MEDIA_DIRECTORY + "uploads"
STATIC_EXPORT_MEDIA_DIRECTORY = STATIC_MEDIA_DIRECTORY + "exported-files"
STATIC_ICON_UPLOAD_DIRECTORY = STATIC_UPLOAD_MEDIA_DIRECTORY + "/" + "icons"
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

DEFAULT_FILE_STORAGE = 'blackwidow.engine.extensions.media_storage.BWMediaStorage'

AWS_FILE_WRITE_BUFFER_SIZE = 1000000
