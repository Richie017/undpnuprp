from django.db import models

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Ziaul'


@decorate(is_object_context,
          route(route='action-logs', group='Logs', display_name='Action Log', module=ModuleEnum.Settings, hide=True))
class ActionLog(OrganizationDomainEntity):
    action_name = models.CharField(max_length=200)
    action_flag = models.IntegerField(null=True)
    object_model = models.CharField(max_length=200)
    object_id = models.BigIntegerField(null=True)
    message = models.CharField(max_length=500)

    @classmethod
    def table_columns(cls):
        return 'code', 'action_name', 'object_model:Model Name', 'object_id', 'message', 'created_by', 'last_updated'

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Delete]

    @property
    def get_inline_manage_buttons(self):
        return [dict(
            name='Details',
            action='view',
            title="Click to view this item",
            icon='icon-eye',
            ajax='0',
            url_name=self.__class__.get_route_name(action=ViewActionEnum.Details),
            classes='all-action ',
            parent=None
        )]

    def details_link_config(self, **kwargs):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    @classmethod
    def log(cls, *args, model=DomainEntity, action_name='', model_obj=None, message='', **kwargs):
        _log = cls()
        _log.object_model = model.__name__
        if model_obj is not None:
            _log.object_id = model_obj.pk
        _log.action_name = action_name
        _log.organization = kwargs.get('organization', Organization.objects.get(is_master=True))
        _log.message = message
        _log.save()
