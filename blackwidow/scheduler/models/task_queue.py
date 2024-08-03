from enum import Enum

from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Ziaul Haque'


class SchedulerTaskQueueEnum(Enum):
    SCHEDULED = 'Scheduled'
    PROCESSING = 'Processing'
    COMPLETED = 'Completed'
    ERROR = 'Error'

    @classmethod
    def render(cls, item):
        _icon = ""
        _class = ""
        if item == SchedulerTaskQueueEnum.SCHEDULED.value:
            _class = 'warning'
            item = 'Scheduled'
        if item == SchedulerTaskQueueEnum.COMPLETED.value:
            _class = 'success'
            item = 'Completed'
        if item == SchedulerTaskQueueEnum.ERROR.value:
            _class = 'error'
            item = 'Error'
        if item == SchedulerTaskQueueEnum.PROCESSING.value:
            _class = 'info'
            item = 'Processing'
            _icon = "<i class='icon-spinner-live'></i>"
        return mark_safe("<span class='text-" + _class + "'>" + _icon + "<strong> " + item + "</strong></span>")


class SchedulerTaskQueue(OrganizationDomainEntity):
    name = models.CharField(max_length=256, null=True)
    model = models.CharField(max_length=255, null=True)
    status = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def clean(self):
        self.type = self.__class__.__name__
        if self.pk is None:
            self.status = SchedulerTaskQueueEnum.SCHEDULED.value
        super().clean()

    @classmethod
    def table_columns(cls):
        return 'code', 'render_status'

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete]

    @property
    def render_status(self):
        return SchedulerTaskQueueEnum.render(self.status)
