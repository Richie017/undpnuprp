from django.forms.forms import Form

from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.color_code_generator import ColorCode
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.reports.models.maps.household_map_location import HouseholdLocationReport
from undp_nuprp.reports.views.base.base_report import GenericReportView
from undp_nuprp.nuprp_admin.models.infrastructure_units.household import Household

__author__ = 'Ziaul Haque'


@decorate(override_view(model=HouseholdLocationReport, view=ViewActionEnum.Manage))
class HouseholdMapLocationView(GenericReportView):
    def get_template_names(self):
        return ['reports/map_household_location.html']

    def get_wrapped_parameters(self, parameters):
        class DynamicForm(Form):
            pass

        form = DynamicForm()
        for p in parameters:
            form.fields[p['name']] = p['field']
        return form

    def get_report_parameters(self, **kwargs):
        parameters = dict()
        parameters['G1'] = self.get_wrapped_parameters(())
        parameters['G2'] = self.get_wrapped_parameters(())
        parameters['G3'] = self.get_wrapped_parameters(())
        return parameters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Household Location Map"
        context['enable_map'] = True
        context['parameters'] = self.get_report_parameters(**kwargs)
        legend_colors = ColorCode.get_spaced_colors(1)
        context['legend_items'] = [{
            'id': Household.__name__,
            'color': '#' + legend_colors[0],
            'name': Household.__name__

        }]
        return context

    def get_json_response(self, content, **kwargs):
        all_locations = []

        all_households = Household.objects.using(BWDatabaseRouter.get_read_database_name()).values(
            'name', 'address__location__latitude', 'address__location__longitude',
            'address__geography__name', 'address__geography__level__name', 'type')
        for household in all_households:
            all_locations.append({
                'client_type': household['type'],
                'name': household['name'],
                'address_label': household['address__geography__level__name'],
                'address_name': household['address__geography__name'],
                'latitude': household['address__location__latitude'],
                'longitude': household['address__location__longitude']
            })

        data_dict = dict()
        data_dict['title'] = "Household Location Map"
        data_dict['items'] = all_locations
        return super().get_json_response(self.convert_context_to_json(data_dict), **kwargs)
