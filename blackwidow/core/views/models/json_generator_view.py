import json
import os
import threading

from django.conf import settings
from django.http.response import JsonResponse

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.models import ErrorLog
from blackwidow.core.models.common.jason_generator import ModelDataToJson
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.decorators.utility import decorate, get_models_with_decorator
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.model_descriptor import get_model_by_name
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from config.apps import INSTALLED_APPS
from config.aws_s3_config import AWS_MODEL_JASON_DIR, AWS_STATIC_JS_DIR
from config.model_json_cache import MODEL_JASON_DIR
from settings import STATIC_ROOT

__author__ = 'Shamil on 09-Mar-16 1:22 PM'
__organization__ = 'FIS'


class JSONGeneratorThread(threading.Thread):
    def __init__(self, model=None):
        self.model = model
        threading.Thread.__init__(self)

    def run(self):
        try:
            model_cache_query = self.model.get_model_data_query()
            data = [ob.to_model_data() for ob in self.model.objects.filter(model_cache_query)]

            # If using s3 as static file server, need to write the JS file in s3 bucket
            if getattr(settings, 'S3_STATIC_ENABLED', False):
                file_dir = AWS_MODEL_JASON_DIR
                file_name = file_dir + self.model._meta.model_name + '.js'
                file_content = json.dumps(data, ensure_ascii=True)
                AWSFileWriter.upload_file_with_content(file_name=file_name, content=file_content)
            else:
                os.makedirs(MODEL_JASON_DIR, exist_ok=True)
                with open(MODEL_JASON_DIR + self.model._meta.model_name + '.js', 'w') as f:
                    json.dump(data, f, ensure_ascii=True)

            filter_roles = get_models_with_decorator(
                decorator_name='has_data_filter',
                apps=INSTALLED_APPS,
                include_class=False
            )
            filter_users = ConsoleUser.objects.filter(type__in=filter_roles)

            for user in filter_users:
                data = [ob.to_model_data() for ob in
                        self.model.get_role_based_queryset(queryset=self.model.objects.filter(model_cache_query),
                                                           user=user)]

                # If using s3 as static file server, need to write the JS file in s3 bucket
                if getattr(settings, 'S3_STATIC_ENABLED', False):
                    file_dir = AWS_MODEL_JASON_DIR
                    file_name = file_dir + self.model._meta.model_name + '_' + str(user.pk) + '.js'
                    file_content = json.dumps(data, ensure_ascii=True)
                    AWSFileWriter.upload_file_with_content(file_name=file_name, content=file_content)
                else:
                    os.makedirs(MODEL_JASON_DIR, exist_ok=True)
                    with open(MODEL_JASON_DIR + self.model._meta.model_name + '_' + str(user.pk) + '.js', 'w') as f:
                        json.dump(data, f, ensure_ascii=True)

            relational_data = self.model.get_relational_data_configs()
            for relation in relational_data:
                # If using s3 as static file server, need to write the JS file in s3 bucket
                if getattr(settings, 'S3_STATIC_ENABLED', False):
                    file_dir = AWS_MODEL_JASON_DIR
                    file_name = file_dir + relation['name'] + '.js'
                    file_content = json.dumps(data, ensure_ascii=True)
                    AWSFileWriter.upload_file_with_content(file_name=file_name, content=file_content)
                else:
                    os.makedirs(MODEL_JASON_DIR, exist_ok=True)
                    with open(MODEL_JASON_DIR + relation['name'] + '.js', 'w') as f:
                        json.dump(relation['data'], f, ensure_ascii=True)

            self.update_version_in_js(
                version=ModelDataToJson.get_version(
                    app_label=self.model._meta.app_label,
                    model_name=self.model.__name__,
                    save=True
                )
            )
        except Exception as err:
            # print(err)
            pass

    @classmethod
    def update_version_in_js(cls, version=''):
        try:
            # If using s3 as static file server, need to write the JS file in s3 bucket
            if getattr(settings, 'S3_STATIC_ENABLED', False):
                file_dir = AWS_STATIC_JS_DIR
                file_name = file_dir + "static.js"
                file_content = 'var cache_config = {version: "' + version + '"};'
                AWSFileWriter.upload_file_with_content(file_name=file_name, content=file_content)
            else:
                filename = os.path.join(STATIC_ROOT, 'js/constant/static.js')
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'w') as f:
                    f.write('var cache_config = {version: "' + version + '"};')
                    f.close()
        except Exception as exp:
            ErrorLog.log(exp=exp)


@decorate(override_view(model=ModelDataToJson, view=ViewActionEnum.Manage))
class ModelDataToJsonView(GenericListView):
    def get_template_names(self):
        return ['common/data_to_json/_list.html']

    def get(self, request, *args, **kwargs):
        try:
            if request.GET.get('action', 'false') == 'true':
                model_name = request.GET.get('model_name', None)
                app_label = request.GET.get('app_label', None)
                if model_name is not None and app_label is not None:
                    model = get_model_by_name(model_name=model_name, app_label=app_label)
                    if model is not None:
                        self.convert_data_to_json(model)
                        return JsonResponse({
                            'success': True
                        })
            else:
                return super(ModelDataToJsonView, self).get(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': e
            })

    def get_context_data(self, **kwargs):
        context_data = super(ModelDataToJsonView, self).get_context_data(**kwargs)

        json_enabled_models = get_models_with_decorator(
            decorator_name='enable_caching',
            apps=INSTALLED_APPS,
            include_class=True
        )
        jsoned_models = []
        for model in json_enabled_models:
            if hasattr(model, '__hidden_in_cache_list') and not getattr(model, '__hidden_in_cache_list', True):
                jsoned_models.append({
                    'name': bw_titleize(model._meta.model_name),
                    'model_name': model.__name__,
                    'app_label': model._meta.app_label
                })
        context_data['jsoned_models'] = jsoned_models
        return context_data

    @classmethod
    def convert_data_to_json(cls, model):
        try:
            JSONGeneratorThread(
                model=model
            ).start()
        except Exception as error:
            pass
