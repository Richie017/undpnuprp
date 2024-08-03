from enum import Enum

from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.file.fileobject import FileObject
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Mahmud'


class FileQueueEnum(Enum):
    SCHEDULED = 'Scheduled'
    COMPLETED = 'Completed'
    ERROR = 'Error'
    PROCESSING = 'Processing'

    @classmethod
    def render(cls, item):
        _icon = ""
        if item == 'FileQueueEnum.SCHEDULED':
            _class = 'warning'
            item = 'Scheduled'
        if item == 'FileQueueEnum.COMPLETED':
            _class = 'success'
            item = 'Completed'
        if item == 'FileQueueEnum.ERROR':
            _class = 'error'
            item = 'Error'
        if item == 'FileQueueEnum.PROCESSING':
            _class = 'info'
            item = 'Processing'
            _icon = "<i class='icon-spinner-live'></i>"
        return mark_safe("<span class='text-" + _class + "'>" + _icon + "<strong> " + item + "</strong></span>")


class FileQueue(OrganizationDomainEntity):
    file = models.ForeignKey(FileObject)
    model = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True)

    def get_choice_name(self):
        return str(self.file)

    def clean(self):
        self.type = self.__class__.__name__
        if self.pk is None:
            self.status = FileQueueEnum.SCHEDULED
        super().clean()

    @classmethod
    def table_columns(cls):
        return 'code', 'file', 'render_status'

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.RunImporter]

    @classmethod
    def get_routes(cls, **kwargs):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Details, ViewActionEnum.Delete,
                ViewActionEnum.Import, ViewActionEnum.Manage, ViewActionEnum.RunImporter]

    @property
    def render_status(self):
        return FileQueueEnum.render(self.status)

    def save(self, *args, **kwargs):
        # if self.status == FileQueueEnum.PROCESSING:
        #     raise EntityNotEditableException("You cannot edit a queue item while it is being processed")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # if self.status == FileQueueEnum.PROCESSING:
        #     raise EntityNotDeletableException("You cannot delete a queue item while it is being processed")
        super().delete(*args, **kwargs)
