from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock


@decorate(is_object_context,
          route(route='delete-surveys', group='Other Admin', module=ModuleEnum.Administration,
                display_name='Delete Surveys', group_order=2, item_order=8))
class DeleteTestSurvey(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True)
    from_date = models.DateTimeField(null=True, blank=True)
    to_date = models.DateTimeField(null=True, blank=True)
    date_of_deletion = models.BigIntegerField(null=True, blank=True)
    number_of_deleted_surveys = models.IntegerField(default=0)
    status = models.CharField(max_length=20)

    @property
    def render_from_date(self):
        return self.from_date.date().strftime('%d-%m-%Y') if self.from_date else None

    @property
    def render_to_date(self):
        return self.to_date.date().strftime('%d-%m-%Y') if self.to_date else None

    @property
    def render_date_of_deletion(self):
        return Clock.convert_timestamp_to_datetime_str(self.date_of_deletion)

    @classmethod
    def table_columns(cls):
        return 'city', 'render_from_date', 'render_to_date', 'render_date_of_deletion', 'number_of_deleted_surveys', \
               'status', 'created_by', 'date_created'

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create]
