import errno

from django.core import serializers

from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.dbmediabackup.utils.downloader import BWDownloader

__author__ = "Ziaul Haque"


def obj_serialize(instance):
    _obj = {
        'id': instance.pk,
        'code': instance.render_code,
        'name': instance.name,
        'status': instance.render_status,
        'db_size': instance.db_size,
        'start_time': instance.render_start_time,
        'completion_time': instance.render_completion_time,
        'extra_info': instance.extra_info
    }
    return _obj


class BWModelSerializer(object):
    storage_client = BWDownloader.storage_client()
    CONFIG_PARTIAL_PATH = storage_client.root_path + '/config/json_data/'

    @classmethod
    def serialize_to_json(cls, model):
        try:
            if hasattr(model, 'all_objects'):
                model_objects = model.all_objects.all()
                _filename = cls.CONFIG_PARTIAL_PATH + model._meta.model_name + '.json'

                cls.storage_client.client.put_file(
                    _filename,
                    serializers.serialize('json', model_objects),
                    overwrite=True
                )
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        except Exception as exp:
            ErrorLog.log(exp)

    @classmethod
    def deserialize_json(cls, model):
        try:
            response_file = cls.storage_client.client.get_file(
                cls.CONFIG_PARTIAL_PATH + model._meta.model_name + '.json'
            )
            obj_generator = serializers.deserialize('json', response_file.read())
            for obj in obj_generator:
                obj.save()

        except Exception as exp:
            ErrorLog.log(exp)
