from collections import OrderedDict
from datetime import datetime

from blackwidow.core.models.information.information_object import InformationObject
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.core.viewmodels.tabs_config import TabView, TabViewAction
from blackwidow.engine.decorators.route_partial_routes import route, partial_route, is_profile_content
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Tareq'


@decorate(is_profile_content, is_object_context,
          route(route='news', display_name='News & Announcement', group='News & Notifications',
                group_order=1, module=ModuleEnum.Alert),
          partial_route(relation='normal', models=[Role, ConsoleUser]))
class News(InformationObject):
    @classmethod
    def exclude_search_fields(cls):
        return [
            "code", "render_title", "start_time", "end_time", "render_expired"
        ]

    @classmethod
    def get_api_filters(cls):
        now = datetime.now().timestamp() * 1000
        return {
            'end_time__gte': now
        }

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['start_time'] = self.render_timestamp(self.start_time)
        details['end_time'] = self.render_timestamp(self.end_time)
        details['expired'] = self.render_expired
        details['created_by'] = self.created_by
        details['created_on'] = self.render_timestamp(self.date_created)
        details['last_updated_by'] = self.last_updated_by
        details['last_updated_on'] = self.render_timestamp(self.last_updated)
        return details

    @classmethod
    def get_serializer(cls):
        InformationObjectSerializer = InformationObject.get_serializer()

        class NewsSerializer(InformationObjectSerializer):
            class Meta:
                model = cls
                fields = ('id', 'name', 'details', 'start_time', 'end_time', 'last_updated')

        return NewsSerializer

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Recipient Role(s)',
                access_key='recipient_roles',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=Role,
                queryset=self.recipient_roles.all(),
                queryset_filter=None,
                property=self.recipient_roles,
                add_more_queryset=Role.objects.filter().exclude(
                    pk__in=self.recipient_roles.values_list('id', flat=True)),
                actions=[
                    TabViewAction(
                        title='Add',
                        action='add',
                        icon='icon-plus',
                        route_name=Role.get_route_name(action=ViewActionEnum.PartialBulkAdd,
                                                       parent=self.__class__.__name__.lower()),
                        css_class='manage-action load-modal fis-plus-ico',

                    ),
                    TabViewAction(
                        title='Remove',
                        action='partial-remove',
                        icon='icon-remove',
                        route_name=Role.get_route_name(action=ViewActionEnum.PartialBulkRemove,
                                                       parent=self.__class__.__name__.lower()),
                        css_class='manage-action delete-item fis-remove-ico'
                    )

                ]
            ),
            TabView(
                title='Recipient User(s)',
                access_key='users',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                property=self.recipient_users,
                add_more_queryset=ConsoleUser.objects.filter(
                    role_id__in=self.recipient_roles.values_list('id', flat=True)
                ).exclude(pk__in=self.recipient_users.values_list('id', flat=True)),
                related_model=ConsoleUser,
                queryset=self.recipient_users.all(),
                queryset_filter=None,
                actions=[
                    TabViewAction(
                        title='Add',
                        action='add',
                        icon='icon-plus',
                        route_name=ConsoleUser.get_route_name(action=ViewActionEnum.PartialBulkAdd,
                                                              parent=self.__class__.__name__.lower()),
                        css_class='manage-action load-modal fis-plus-ico',

                    ),
                    TabViewAction(
                        title='Remove',
                        action='partial-remove',
                        icon='icon-remove',
                        route_name=ConsoleUser.get_route_name(action=ViewActionEnum.PartialBulkRemove,
                                                              parent=self.__class__.__name__.lower()),
                        css_class='manage-action delete-item fis-remove-ico'
                    )
                ]
            )
        ]

    def remove_child_item(self, **kwargs):
        super(News, self).remove_child_item(**kwargs)
        tab = [x for x in self.tabs_config if x.access_key == kwargs['tab']][0]
        if tab.access_key == 'recipient_roles':
            console_user_set = ConsoleUser.objects.filter(
                role_id__in=[_pk for _pk in kwargs['ids'].split(',')])
            self.recipient_users.remove(*console_user_set)

    def add_child_item(self, **kwargs):
        super(News, self).add_child_item(**kwargs)
        tab = [x for x in self.tabs_config if x.access_key == kwargs['tab']][0]
        if tab.access_key == 'recipient_roles':
            console_user_set = ConsoleUser.objects.filter(
                role_id__in=[_pk for _pk in kwargs['ids'].split(',')])
            self.recipient_users.add(*console_user_set)
