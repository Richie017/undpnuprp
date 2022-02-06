from django.db import models

from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.extensions.async_task import perform_async
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Rafi'


@decorate(is_object_context,
          route(route='field-device', group='Field Device', group_order=1, module=ModuleEnum.Settings,
                display_name="Field Device"))
class UserDevice(OrganizationDomainEntity):
    user = models.ForeignKey(ConsoleUser, null=True, on_delete=models.SET_NULL)
    imei_number = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=63, blank=True)
    model = models.CharField(max_length=63, blank=True)
    manufacturer = models.CharField(max_length=63, blank=True)
    os_version = models.CharField(max_length=63, blank=True)
    apk_version = models.CharField(max_length=63, blank=True)
    dpi = models.IntegerField(default=0)

    @classmethod
    def add_user_device(cls, request):
        """
        create device information object with user and device imei_number
        :param request: http request
        :return: None
        """
        from blackwidow.scheduler.tasks import update_user_device_logs

        meta_field_keys = ['HTTP_IMEI_NUMBER', 'HTTP_PHONE_NUMBER', 'HTTP_DEVICE_MODEL', 'HTTP_MANUFACTURER',
                           'HTTP_DEVICE_OS', 'HTTP_DEVICE_DPI', 'HTTP_APK_VERSION']
        request_meta = {}
        for k in meta_field_keys:
            if k in request.META.keys():
                request_meta[k] = request.META[k]

        perform_async(method=update_user_device_logs, args=(request.c_user, request_meta))

    @classmethod
    def initial_prefetch_objects(cls, *args, **kwargs):
        return {'user': 'user'}

    @classmethod
    def table_columns(cls, *args, **kwargs):
        return ['render_code', 'user', 'imei_number', 'apk_version', 'date_created', 'last_updated']

    @classmethod
    def details_view_fields(cls, instance=None, *args, **kwargs):
        return ['user', 'imei_number', 'apk_version', 'date_created', 'last_updated']

    @property
    def get_inline_manage_buttons(self):
        return [ViewActionEnum.Details, ViewActionEnum.Edit]

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.Deactivate]

    @classmethod
    def get_infrastructure_unit_related_field(cls, *args, **kwargs):
        return "user__assigned_to"

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Deactivate',
                action='deactivate',
                icon='fbx-rightnav-cancel',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Deactivate),
                classes='manage-action all-action confirm-action'
            ),
        ]
