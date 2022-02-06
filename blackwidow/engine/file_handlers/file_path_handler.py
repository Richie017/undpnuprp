"""
    Written by tareq on 6/24/18
"""
import os

import boto3
from django.conf import settings

from config.aws_s3_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, MEDIA_DIRECTORY

__author__ = 'Tareq'


class FilePathHandler(object):
    @classmethod
    def get_absolute_path_from_file_path(cls, file_name, file_path):
        if settings.S3_STATIC_ENABLED:
            s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
            bucket = s3.Bucket(AWS_STORAGE_BUCKET_NAME)
            s3_file_path = file_name
            upload_dir = s3_file_path.rsplit("/", 1)[0]
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            bucket.download_file(MEDIA_DIRECTORY + s3_file_path, s3_file_path)
            return s3_file_path
        else:
            return os.path.abspath(file_path)

    @classmethod
    def get_absolute_path(cls, file):
        if settings.S3_STATIC_ENABLED:
            return cls.get_absolute_path_from_file_path(file.name, None)
        return cls.get_absolute_path_from_file_path(file.name, file.path)
