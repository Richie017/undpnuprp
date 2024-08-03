from collections import OrderedDict

from django.db.models.query_utils import Q

from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = "Shama"


@decorate(is_object_context,
          route(route='cdc-cluster', group='Social Mobilization and Community Capacity Building',
                module=ModuleEnum.Analysis,
                display_name='CDC Cluster', group_order=2, item_order=10))
class CDCCluster(InfrastructureUnit):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @property
    def render_city_corporation(self):
        return self.address.geography.name if self.address else None

    @property
    def render_number_of_CDC(self):
        return self.infrastructureunit_set.all().count()

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(address__geography__name__icontains=value)

    @classmethod
    def table_columns(cls):
        return ["render_code", "name", "render_city_corporation", "render_number_of_CDC",
                "last_updated:Last Updated On"]

    @property
    def general_information(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['type'] = self.remarks
        details['CDC_cluster_ID'] = self.assigned_code if self.assigned_code else 'N/A'
        details['formation_date'] = self.date_of_formation
        details['city_corporation'] = self.render_city_corporation
        return details

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        details['general_information'] = self.general_information
        details['other_information'] = self.other_information
        return details

    @property
    def tabs_config(self):
        return [
            TabView(
                title='CDC(s)',
                access_key='cdc',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='nuprp_admin.CDC',
                queryset_filter=Q(**{'pk__in': self.infrastructureunit_set.values_list('pk', flat=True)})
            )
        ]
