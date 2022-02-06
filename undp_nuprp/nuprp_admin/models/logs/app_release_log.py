"""
    Created by tareq on 9/1/19
"""
from django.db import models

from blackwidow.core.models import SystemLog
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import save_audit_log
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.enums.app_release_enum import AppReleaseUpdateTypeEnum

__author__ = "Tareq"


@decorate(is_object_context, save_audit_log, expose_api('app-release-log'),
          route(route='app-release-log', group='Logs', display_name='App Release Log', module=ModuleEnum.Settings,
                item_order=1))
class AppReleaseLog(OrganizationDomainEntity):
    message = models.TextField(blank=True)
    translated_message = models.TextField(blank=True)
    version_code = models.IntegerField(default=0)
    version_name = models.CharField(max_length=127, blank=True)
    publish_date = models.BigIntegerField(default=0)
    comment = models.TextField(blank=True)
    app_download_url = models.URLField(blank=True, max_length=255)
    update_type = models.SmallIntegerField(default=AppReleaseUpdateTypeEnum.NotMandatory.value)

    class Meta:
        app_label = 'nuprp_admin'

    @property
    def render_update_type(self):
        return AppReleaseUpdateTypeEnum.get_name_from_value(self.update_type)

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Edit',
                action='edit',
                icon='fbx-rightnav-edit',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit)
            ),
            dict(
                name='Delete',
                action='delete',
                icon='fbx-rightnav-delete',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            )
        ]

    @property
    def details_view_title(self):
        return self.version_name if self.version_name else self.version_code

    @classmethod
    def get_routes(cls, **kwargs):
        return [ViewActionEnum.Details, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.Manage,
                ViewActionEnum.Create, ViewActionEnum.Tab]

    @classmethod
    def get_datetime_fields(cls):
        return list(SystemLog.get_datetime_fields()) + ['publish_date']

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit,]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Edit, ViewActionEnum.Details]

    @property
    def render_publish_date(self):
        return self.render_timestamp(self.publish_date)

    @classmethod
    def table_columns(cls, *args, **kwargs):
        return ['render_code', 'version_code', 'version_name', 'render_publish_date', 'render_update_type',
                'created_by', 'date_created']

    @classmethod
    def details_view_fields(cls, instance=None, *args, **kwargs):
        return [
            'code', 'version_code', 'version_name', 'render_publish_date', 'comment', 'message:message_for_user',
            'translated_message', 'render_update_type', 'app_download_url', 'created_by', 'date_created',
            'last_updated_by', 'last_updated'
        ]

    @classmethod
    def get_serializer(cls):
        ODESerializer = OrganizationDomainEntity.get_serializer()

        class AppReleaseLogSerializer(ODESerializer):
            class Meta(ODESerializer.Meta):
                model = cls
                fields = [
                    'id', 'version_code', 'version_name', 'message', 'translated_message', 'app_download_url',
                    'comment', 'update_type', 'publish_date', 'last_updated'
                ]

        return AppReleaseLogSerializer
