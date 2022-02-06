from enum import Enum

from django.db import models

from blackwidow.core.managers.modelmanager import DomainEntityModelManager
from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum


class DeletedEntityEnum(Enum):
    SoftDeleted = 0
    Restored = 1
    HardDeleted = 2

    def __str__(self):
        return self.value


class AuditLog(OrganizationDomainEntity):
    model_name = models.CharField(max_length=200)
    model_pk = models.BigIntegerField(default=0)

    @classmethod
    def log(cls, model=DomainEntity):
        try:
            _log = cls()
            _log.model_name = model.get_audit_log_model_name()
            _log.model_pk = model.pk
            _log.save()
        except:
            pass


class DeleteLog(AuditLog):
    deleted_status = models.IntegerField(default=DeletedEntityEnum.SoftDeleted.value)
    display_name = models.CharField(max_length=128, default='Unspecified')
    is_visible = models.BooleanField(default=True)

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def table_columns(cls):
        return 'code', 'model_pk', 'model_name', 'display_name', 'created_by', 'last_updated'

    @classmethod
    def log(cls, model=DomainEntity, name='Unspecified', is_visible=True):
        try:
            _log = cls()
            _log.model_name = model.get_audit_log_model_name()
            _log.model_pk = model.pk
            _log.display_name = name
            _log.is_visible = is_visible
            _log.save()
        except:
            pass

    @classmethod
    def get_routes(cls, **kwargs):
        return [ViewActionEnum.Details, ViewActionEnum.Delete, ViewActionEnum.Manage, ViewActionEnum.Restore]


class RestoreLog(AuditLog):
    display_name = models.CharField(max_length=128, default='Unspecified')
    is_visible = models.BooleanField(default=True)

    @classmethod
    def table_columns(cls):
        return 'code', 'model_pk', 'model_name', 'display_name', 'created_by', 'last_updated'

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

    @classmethod
    def log(cls, model=DomainEntity, name='Unspecified', is_visible=True):
        try:
            _log = cls()
            _log.model_name = model.get_audit_log_model_name()
            _log.model_pk = model.pk
            _log.display_name = name
            _log.is_visible = True
            _log.save()
        except:
            pass

    @classmethod
    def get_routes(cls, **kwargs):
        return [ViewActionEnum.Details, ViewActionEnum.Delete, ViewActionEnum.Manage]


class UpdateLog(AuditLog):
    class Meta:
        proxy = True


class CreateLog(AuditLog):
    class Meta:
        proxy = True


@decorate(is_object_context, route(route='delete-logs', group='Logs', display_name='Delete Log',
                                   module=ModuleEnum.Settings, group_order=3, item_order=1))
class VisibleDeleteLog(DeleteLog):
    objects = DomainEntityModelManager(filter={'is_visible': True})

    class Meta:
        proxy = True


@decorate(is_object_context, route(route='restore-logs', group='Logs', display_name='Restore Log',
                                   module=ModuleEnum.Settings, group_order=3, item_order=1))
class VisibleRestoreLog(RestoreLog):
    objects = DomainEntityModelManager(filter={'is_visible': True})

    class Meta:
        proxy = True
