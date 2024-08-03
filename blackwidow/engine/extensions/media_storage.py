from storages.backends.s3boto3 import S3Boto3Storage

__author__ = 'Ziaul Haque'


class BWMediaStorage(S3Boto3Storage):
    location = 'media'
    file_overwrite = False
