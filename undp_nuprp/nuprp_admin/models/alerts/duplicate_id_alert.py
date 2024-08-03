from enum import Enum

from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.nuprp_admin.models.alert_base.nuprp_alert_base import NuprpAlertBaseConfig

__author__ = "Shama, Ziaul Haque"


class DuplicateIDAlertEnum(Enum):
    assigned_code = 'PG member ID'
    national_id = 'NID no'
    phone_number = 'Phone number'


@decorate(is_object_context,
          route(route='duplicate-id-alerts', group='PG Member Alerts', module=ModuleEnum.Alert,
                display_name='Duplicate PG Member Alert', group_order=2, item_order=1))
class DuplcateIdAlert(NuprpAlertBaseConfig):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @property
    def render_alert_type(self):
        if self.model_property == 'assigned_code':
            return "PG member ID"
        if self.model == 'phone_number.phone':
            return "Phone number"
        if self.model_property == "client_meta.national_id":
            return "ID no"
        return "N/A"

    @classmethod
    def order_by_alert_type(cls):
        return ['model_property']

    @property
    def render_enumerator(self):
        return self.created_by if self.created_by else 'N/A'

    @classmethod
    def search_enumerator(cls, queryset, value):
        return queryset.filter(created_by__name__icontains=value)

    @classmethod
    def order_by_enumerator(cls):
        return ['created_by__name']

    @property
    def render_city(self):
        if self.created_by:
            _address = self.created_by.addresses.first()
            if _address and _address.geography:
                return _address.geography.parent.name if _address.geography.parent else "N/A"
        else:
            return "N/A"

    @classmethod
    def search_city(cls, queryset, value):
        return queryset.filter(created_by__addresses__geography__parent__name__icontains=value)

    @classmethod
    def order_by_city(cls):
        return ['created_by__addresses__geography__parent__name']

    @property
    def render_survey_response(self):
        from undp_nuprp.survey.models.response.survey_response import SurveyResponse
        return SurveyResponse.objects.filter(respondent_client__id=self.object_id).first()

    @classmethod
    def table_columns(cls):
        return ['render_code', "render_city", "model_property:Alert Type", 'alert_for:PG Member',
                'render_survey_response', 'alert_detail:Reason', 'render_enumerator', 'alert_creation_time:Created On']

    @classmethod
    def sortable_columns(cls):
        return ['render_code', "render_city", "model_property", 'alert_for',
                'render_enumerator', 'alert_creation_time']

    @classmethod
    def exclude_search_fields(cls):
        return ["render_alert_type", "render_survey_response"]

    @classmethod
    def get_object_inline_buttons(cls):
        return []

    @property
    def render_code(self):
        return self.code
