from collections import OrderedDict

from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context, has_status_data
from blackwidow.engine.enums.modules_enum import ModuleEnum

__author__ = 'Tareq'


@decorate(save_audit_log, is_object_context, expose_api('household'), has_status_data,
          route(route='household', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                display_name='Household', group_order=3, item_order=19))
class Household(InfrastructureUnit):
    @classmethod
    def get_status_data(cls, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return: Key value pair for status API response
        """
        return {
            'household_prefix': None,
            'last_household_id': 0
        }

    @property
    def render_poor_settlement(self):
        if self.address:
            return self.address.geography if self.address.geography else 'N/A'
        return 'N/A'

    @property
    def render_mahalla(self):
        if self.render_poor_settlement != 'N/A':
            return self.render_poor_settlement.parent if self.render_poor_settlement.parent else 'N/A'
        return 'N/A'

    @property
    def render_ward(self):
        if self.render_mahalla != 'N/A':
            return self.render_mahalla.parent if self.render_mahalla.parent else 'N/A'
        return 'N/A'

    @property
    def render_pourashava___or___city_corporation(self):
        if self.render_ward != 'N/A':
            return self.render_ward.parent if self.render_ward.parent else 'N/A'
        return 'N/A'

    @property
    def render_division(self):
        if self.render_pourashava___or___city_corporation != 'N/A':
            return self.render_pourashava___or___city_corporation.parent \
                if self.render_pourashava___or___city_corporation.parent else 'N/A'
        return 'N/A'

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'assigned_code:Household ID', 'name', 'render_poor_settlement', 'render_mahalla',
            'render_ward', 'render_pourashava___or___city_corporation', 'render_division', 'created_by', 'last_updated')

    @classmethod
    def sortable_columns(cls):
        return [
            'render_code', 'name', 'render_poor_settlement', 'render_mahalla', 'render_ward',
            'render_pourashava___or___city_corporation', 'render_division', 'created_by', 'last_updated'
        ]

    @classmethod
    def search_poor_settlement(cls, queryset, value):
        return queryset.filter(address__geography__name__icontains=value)

    @classmethod
    def search_mahalla(cls, queryset, value):
        return queryset.filter(address__geography__parent__name__icontains=value)

    @classmethod
    def search_ward(cls, queryset, value):
        return queryset.filter(address__geography__parent__parent__name__icontains=value)

    @classmethod
    def search_pourashava___or___city_corporation(cls, queryset, value):
        return queryset.filter(address__geography__parent__parent__parent__name__icontains=value)

    @classmethod
    def search_division(cls, queryset, value):
        return queryset.filter(address__geography__parent__parent__parent__parent__name__icontains=value)

    @classmethod
    def order_by_poor_settlement(cls):
        return ['address__geography__name']

    @classmethod
    def order_by_mahalla(cl):
        return ['address__geography__parent__name']

    @classmethod
    def order_by_ward(cls):
        return ['address__geography__parent__parent__name']

    @classmethod
    def order_by_pourashava___or___city_corporation(cls):
        return ['address__geography__parent__parent__parent__name']

    @classmethod
    def order_by_division(cls):
        return ['address__geography__parent__parent__parent__parent__name']

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['household_id'] = self.assigned_code
        details['name'] = self.name
        details['household head'] = Household.objects.filter(assigned_to_id=self.pk).first()
        if not details['household head']:
            details['household head'] = 'N/A'
        details['poor_settlement'] = self.render_poor_settlement
        details['mahalla'] = self.render_mahalla
        details['ward'] = self.render_ward
        details['pourashava / city_corporation'] = self.render_pourashava___or___city_corporation
        details['division'] = self.render_division
        details['created_by'] = self.created_by
        details['created_on'] = self.render_timestamp(self.date_created)
        details['last_updated_by'] = self.last_updated_by
        details['last_updated_on'] = self.render_timestamp(self.last_updated)
        return details

    @classmethod
    def get_serializer(cls):
        IUSerializer = InfrastructureUnit.get_serializer()

        class HouseholdSerializer(IUSerializer):
            address = ContactAddress.get_serializer()

            class Meta:
                model = cls
                fields = 'name', 'address'

        return HouseholdSerializer

    class Meta:
        app_label = 'nuprp_admin'
        proxy = True
