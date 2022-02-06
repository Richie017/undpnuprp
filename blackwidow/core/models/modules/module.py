from django.db import models
from django.db.models.query_utils import Q

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from config.menu_config import MODULE_TITLES

__author__ = 'Mahmud'


@decorate(is_object_context)
class BWModule(OrganizationDomainEntity):
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=120, default='fbx-admin')
    parent = models.ForeignKey('self', null=True)
    module_url = models.CharField(max_length=128, default='')
    module_order = models.IntegerField(default=0)

    def get_choice_name(self):
        if self.parent is not None:
            return self.parent.name + ' -> ' + self.name
        return self.name

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def default_order_by(cls):
        return 'name'

    def __str__(self):
        return self.render_name

    @property
    def render_name(self):
        if self.parent_id is not None:
            return self.parent.render_name + ' -> ' + self.name
        return MODULE_TITLES.get(self.name, self.name)

    @classmethod
    def table_columns(cls):
        return 'code', 'render_name', 'parent'

    @property
    def tabs_config(self):
        tabs = [
            TabView(
                title='Sub Modules',
                access_key='submodules',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='blackwidow_core.BWModule',
                property=self.recipient_users,
                queryset_filter=Q(**{'parent__id': self.pk})
            )
        ]
        return tabs
