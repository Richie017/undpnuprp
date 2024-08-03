from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Sohel'


@decorate(
    is_object_context,
    route(
        route='model-form-generator',
        display_name='Generate Model Form',
        group='Other Admin', module=ModuleEnum.Settings
    ))
class ModelFormGenerator(DomainEntity):
    class Meta:
        app_label = 'core'
