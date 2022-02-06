from datetime import datetime

from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.extensions.clock import Clock

__author__ = 'Tareq'


class InformationObject(OrganizationDomainEntity):
    name = models.CharField(max_length=500)
    recipient_roles = models.ManyToManyField(Role)
    recipient_users = models.ManyToManyField(ConsoleUser)
    start_time = models.BigIntegerField(null=True)
    end_time = models.BigIntegerField(null=True)
    details = models.TextField(max_length=8000)
    notification_medium = models.IntegerField(default=0)

    @classmethod
    def get_datetime_fields(cls):
        return ['date_created', 'last_updated', 'start_time', 'end_time']

    @classmethod
    def get_dependent_field_list(cls):
        return []

    def process(self):
        # c_date = Clock.now()
        if self.start_time is None:
            pass
        elif self.end_time is None or (self.start_time <= Clock.utcnow() <= self.end_time):
            pass

    @property
    def render_expired(self):
        current_time = datetime.now().timestamp() * 1000
        if current_time < self.end_time:
            return 'No'
        return 'Yes'

    @property
    def render_title(self):
        return mark_safe('<p class="ellipsis" style="max-width:13em;" data-toggle="tooltip" title="' + str(
            self.name) + '">' + self.name + '</p>')

    @classmethod
    def table_columns(cls):
        return 'code', 'render_title', 'start_time', 'end_time', 'render_expired', 'created_by', 'date_created:Created On'

    class Meta:
        abstract = True
