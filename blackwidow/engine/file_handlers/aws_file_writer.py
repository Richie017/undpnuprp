"""
    Written by tareq on 6/6/18
"""
import boto3

from config.aws_s3_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, \
    AWS_FILE_WRITE_BUFFER_SIZE

__author__ = 'Tareq'


class AWSFileWriter(object):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    @classmethod
    def get_file_pointer(cls, file_name):
        multipart_upload = cls.s3.create_multipart_upload(
            ACL='public-read',
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=file_name
        )
        return multipart_upload

    @classmethod
    def upload_file_with_content(cls, file_name, content):
        file_pointer = cls.get_file_pointer(file_name=file_name)
        part_info_dict = {'Parts': []}
        part_index = 1

        file_offset = 0
        buffer_size = AWS_FILE_WRITE_BUFFER_SIZE

        while file_offset < len(content):
            upto = file_offset + buffer_size
            if upto < len(content):
                upto = len(content)
            buffer = content[file_offset: upto]
            file_offset += upto

            part = cls.s3.upload_part(
                Bucket=AWS_STORAGE_BUCKET_NAME,
                Key=file_name,
                # PartNumber's need to be in order and unique
                PartNumber=part_index,
                # This 'UploadId' is part of the dict returned in multi_part_upload
                UploadId=file_pointer['UploadId'],
                # The chunk of the file we're streaming.
                Body=buffer,
            )
            # PartNumber and ETag are needed
            part_info_dict['Parts'].append({
                'PartNumber': part_index,
                # You can get this from the return of the uploaded part that we stored earlier
                'ETag': part['ETag']
            })
            part_index += 1

        # This what AWS needs to finish the multipart upload process
        completed_ctx = {
            'Bucket': AWS_STORAGE_BUCKET_NAME,
            'Key': file_name,
            'UploadId': file_pointer['UploadId'],
            'MultipartUpload': part_info_dict
        }

        try:
            # Complete the upload. This triggers Amazon S3 to rebuild the file for you.
            # No need to manually unzip all of the parts ourselves!
            return cls.s3.complete_multipart_upload(**completed_ctx)
        except Exception as exp:
            print(file_name)
            raise exp

    @classmethod
    def get_file_meta(cls, file_name):
        s3_resource = boto3.resource(
            's3', aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        bucket = s3_resource.Bucket(AWS_STORAGE_BUCKET_NAME)
        return bucket.Object(file_name)
