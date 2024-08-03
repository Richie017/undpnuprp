import traceback

from crequest.middleware import CrequestMiddleware
from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Tareq'


class SystemLog(OrganizationDomainEntity):
    message = models.TextField(blank=True)
    path_url = models.CharField(max_length=500, blank=True)

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Delete]

    @classmethod
    def get_routes(cls, **kwargs):
        return [ViewActionEnum.Details, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.Manage]

    @classmethod
    def table_columns(cls):
        return 'code', 'message', 'date_created'

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
    def log(cls, exp, request=None, *args, **kwargs):
        log = cls()
        log.message = str(exp)
        log.organization = kwargs.get('organization', Organization.objects.get(is_master=True))
        log.error_code = ""
        log.stacktrace = "<hr/>".join(traceback.format_exc().splitlines()) if kwargs.get(
            "stacktrace") is None else kwargs.get("stacktrace")
        if request:
            log.path_url = request.get_full_path()
            log.created_by = request.c_user
            log.last_updated_by = request.c_user
        else:
            try:
                request = CrequestMiddleware.get_request()
                log.path_url = request.get_full_path()
            except:
                pass
        log.save(using=BWDatabaseRouter.get_default_database_name())

    class Meta:
        abstract = True
