from collections import OrderedDict

from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.core.viewmodels.tabs_config import TabView, TabViewAction
from blackwidow.engine.decorators.route_partial_routes import route, partial_route
from blackwidow.engine.decorators.utility import decorate, is_object_context, is_role_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models import CDC

__author__ = "Shama, Ziaul Haque"


@decorate(is_object_context, is_role_context,
          route(route='community-facilitator', group='Users', module=ModuleEnum.Settings,
                display_name='Community Facilitator', group_order=1, item_order=8),
          partial_route(relation='normal', models=[CDC, ]))
class CommunityFacilitator(ConsoleUser):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @property
    def render_email_address(self):
        try:
            return self.emails.first().email
        except:
            return 'N/A'

    @property
    def render_city(self):
        try:
            return self.addresses.first().geography.parent.name
        except AttributeError:
            return 'N/A'

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'name', 'render_email_address', 'render_city',
            'created_by', 'date_created', 'last_updated'
        )

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete]

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['login'] = self.user.username
        details['email_address'] = self.render_email_address
        details['address'] = self.addresses.first()
        details['created_by'] = self.created_by
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        return details

    @property
    def tabs_config(self):
        _city_obj = None
        if self.addresses.exists():
            _address = self.addresses.first()
            if _address:
                _city_obj = self.addresses.first().geography.parent
        tabs = [
            TabView(
                title='CDC(s)',
                access_key='cdcs',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                property=self.infrastructureunit_set,
                related_model=CDC,
                queryset=self.infrastructureunit_set.all(),
                add_more_queryset=CDC.objects.filter(address__geography__parent=_city_obj).exclude(
                    pk__in=self.infrastructureunit_set.values_list('pk', flat=True)),
                actions=[
                    TabViewAction(
                        title='Add',
                        action='add',
                        icon='icon-plus',
                        route_name=CDC.get_route_name(
                            action=ViewActionEnum.PartialBulkAdd, parent=self.__class__.__name__.lower()),
                        css_class='manage-action load-modal fis-link-ico',
                        enable_wide_popup=True
                    ),
                    TabViewAction(
                        title='Remove',
                        action='partial-remove',
                        icon='icon-remove',
                        route_name=CDC.get_route_name(
                            action=ViewActionEnum.PartialBulkRemove, parent=self.__class__.__name__.lower()),
                        css_class='manage-action delete-item fis-remove-ico'
                    )
                ]
            ),
        ]
        return tabs
