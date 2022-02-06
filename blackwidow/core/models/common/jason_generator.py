from django.db import models

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'shamil'


@decorate(
    is_object_context,
    route(route='model-to-json', display_name='Data to Json', group='Other Admin',
          module=ModuleEnum.Settings, group_order=2, item_order=10)
)
class ModelDataToJson(DomainEntity):
    app_label = models.CharField(max_length=256, null=False, default=None)
    model_name = models.CharField(max_length=512, null=False, default=None)

    @staticmethod
    def get_version(app_label='', model_name='', save=False):
        model_json, created = ModelDataToJson.objects.get_or_create(
            app_label=app_label,
            model_name=model_name
        )
        if model_json:
            if save:
                model_json.save()
            return str(model_json.last_updated)
        return '0'

    class Meta:
        app_label = 'core'
