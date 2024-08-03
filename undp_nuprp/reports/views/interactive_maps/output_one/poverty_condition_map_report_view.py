from crequest.middleware import CrequestMiddleware
from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import GeographyLevel
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.utility import decorate, get_models_with_decorator
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from config.apps import INSTALLED_APPS
from undp_nuprp.reports.models import PovertyConditionMapReport
from undp_nuprp.reports.views.interactive_maps.interactive_map_report import GenericInteractiveMapReportView

__author__ = 'Kaikobud'


indicator_choices = (
    ('Condition of access roads','Condition of access roads'),
    ('Availability of drains','Availability of drains'),
    ('Electricity coverage','Electricity coverage'),
    ('Solid waste collection service','Solid waste collection service'),
    ('Access to piped water supply','Access to piped water supply'),
    ('Availability of hygienic toilet','Availability of hygienic toilet'),
    ('Street lighting','Street lighting'),('Attendance of children at school','Attendance of children at school'),
    ('Households with employment','Households with employment'),('Household income','Household income'),
    ('Social problems','Social problems'),('Land tenure security','Land tenure security'),
    ('Housing condition','Housing condition'),('Risk of eviction','Risk of eviction'),
    ('Land Ownership','Land Ownership'),
    ('Type of Occupancy','Type of Occupancy'),
    ('Total Score','Total Score')
)


@decorate(override_view(model=PovertyConditionMapReport, view=ViewActionEnum.Manage))
class PovertyConditionMapReportView(GenericInteractiveMapReportView):
    def get_template_names(self):
        return ['reports/interactive-map-poverty-conditions.html']

    def get_report_parameters(self, **kwargs):
        parameters = super(PovertyConditionMapReportView, self).get_report_parameters(**kwargs)

        city_level = GeographyLevel.objects.using(
            BWDatabaseRouter.get_read_database_name()
        ).filter(name__icontains='city').first()

        parameters['G1'] = self.get_wrapped_parameters((
            {
                'name': 'city',
                'field': GenericModelChoiceField(
                    queryset=Geography.get_role_based_queryset(
                        queryset=Geography.objects.using(
                            BWDatabaseRouter.get_read_database_name()
                        ).filter(level_id=city_level.pk)),
                    label='City/Town',
                    empty_label='Select One',
                    required=False,
                    widget=forms.Select(
                        attrs={
                            'class': 'select2',
                            'width': '220'
                        }
                    )
                )
            },
        ))
        parameters['G2'] = self.get_wrapped_parameters((
            {
                'name': 'indicator',
                'field': forms.ChoiceField(
                    label='Select Indicator',
                    choices=indicator_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    )
                )
            },
        ))
        return parameters

    def get_context_data(self, **kwargs):
        """
        This method is responsible to prepare context data for template
        :param kwargs:
        :return: context data as dictionary
        """
        context = super(PovertyConditionMapReportView, self).get_context_data(**kwargs)
        context['title'] = "Poverty conditions of the urban poor settlements"
        return context

    def get_json_response(self, content, **kwargs):
        city_id =self.extract_parameter('city')
        indicator = self.extract_parameter('indicator')
        if not city_id:
            cities = Geography.objects.filter(level__name='Pourashava/City Corporation').values('id')
            city_ids = [_city['id'] for _city in cities]
            city_ids.append(indicator)
        else:
            city_ids = [city_id, indicator]

        data_dict = dict()
        data_dict['title'] = "Poverty conditions of the urban poor settlements Location Map"
        data_dict['data'] = city_ids

        return super(PovertyConditionMapReportView, self).get_json_response(
            self.convert_context_to_json(data_dict), **kwargs)
