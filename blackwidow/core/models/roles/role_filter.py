import os

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.roles.role import Role
from blackwidow.core.viewmodels.tabs_config import TabView, TabViewAction
from blackwidow.engine.decorators.route_partial_routes import route, partial_route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.scheduler.celery import app

__author__ = 'Machine II'

'''
    The concept of RoleFilter is to apply filtering based on user role during run-time
    The target of class RoleFilter is to automate role filtering and reduce developer's load of writing all the filters
    manually.

    Functionality: RoleFilter models refer a Role for which the filters are created. filters are of RoleFilterEntity type
            RoleFilters are written to app_directory/models/users/filters/<RoleName>_filter.py by calling write_filters_to_file()

            RoleFilterEntity are individual filters expressed in the following way:
                format: (<Target_Model>, Q(**{'<query_str>': self_ref.<value> }))
                implementation example: target_model -> VisitUser
                                        query_str -> 'created_by__assigned_to__parent__id'
                                        value -> 'assigned_to.pk'
                    (VisitUser, Q(**{'created_by__assigned_to__parent__id': self.assigned_to.pk}))

        When create/edit RoleFilter, there is an option to inherit another RoleFilter with query_suffix and value_prefix
        with the idea that, one role consists many filters with minimal change of another role.
            example: if a RoleFilter inherits the above example with value prefix 'prefix', and query_suffix 'suffix',
                    the new RoleFilter will have a RoleFilterEntity like:
                    
                    (VisitUser, Q(**{'created_by__suffix__assigned_to__parent__id': self.prefix.assigned_to.pk}))
'''


class RoleFilterEntity(OrganizationDomainEntity):
    target_model = models.CharField(max_length=128, blank=True)
    target_model_app = models.CharField(max_length=128, blank=True)
    query_str = models.CharField(max_length=512, blank=True)
    value = models.CharField(max_length=512, blank=True)

    @classmethod
    def table_columns(cls):
        return ['code', 'target_model', 'query_str', 'value']

    def __str__(self):
        return '%s.%s: %s = %s' % (self.target_model_app, self.target_model_name, self.query_str, self.value)

    class Meta:
        app_label = 'core'


@decorate(is_object_context,
          route(route='role-filters', display_name='Role Filters', group='Other Admin',
                module=ModuleEnum.Settings),
          partial_route(relation='normal', models=[RoleFilterEntity]))
class RoleFilter(OrganizationDomainEntity):
    role = models.ForeignKey(Role, null=True)
    filters = models.ManyToManyField(RoleFilterEntity)

    def get_choice_name(self):
        return self.__str__()

    def __str__(self):
        return self.role.__str__()

    @classmethod
    def table_columns(cls):
        return ['code', 'role']

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Write Out',
                action='approve',
                icon='fbx-rightnav-tick',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Approve)
            )
        ]

    @property
    def tabs_config(self):
        tabs = [
            TabView(
                title='Filters',
                access_key='filters',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=RoleFilterEntity,
                queryset=self.filters.all(),
                queryset_filter=None,
                property=self.filters,
                actions=[
                    TabViewAction(
                        title="Add",
                        action="action",
                        icon="icon-plus",
                        css_class='manage-action load-modal fis-plus-ico',
                        route_name=RoleFilterEntity.get_route_name(action=ViewActionEnum.PartialCreate,
                                                                   parent=self.__class__.__name__.lower())
                    ),
                    TabViewAction(
                        title="Delete",
                        action="close",
                        icon="icon-remove",
                        css_class='manage-action delete-item fis-remove-ico',
                        route_name=RoleFilterEntity.get_route_name(action=ViewActionEnum.PartialDelete,
                                                                   parent=self.__class__.__name__.lower())
                    )
                ]
            )
        ]
        return tabs

    def final_approval_action(self, action, *args, **kwargs):
        self.write_filter_to_file()
        return self

    def write_filter_to_file(self):
        role_name = self.role.name
        model_entity = ContentType.objects.filter(model=role_name.lower()).values('app_label')
        if len(model_entity):
            app_label = model_entity[0]['app_label']
        else:
            app_label = 'gdfl'  # change in future
        path = str(app_label) + '.models.users.filters'
        f_name = str(self.role.name.lower()) + '_filter.py'
        path = os.path.join(path.replace('.', os.sep), f_name)

        file = open(path, 'w+')
        file.write('from django.db.models.query_utils import Q\n'
                   'from blackwidow.engine.extensions.model_descriptor import get_model_by_name\n\n'
                   '__author__ = "auto generated"\n\n'
                   'def get_filters(model_object):\n'
                   '\tfilters = [\n')
        for entity in self.filters.all():
            app = str(entity.target_model_app)
            mdl = str(entity.target_model)
            try:
                Model = apps.get_model(app, mdl)
                file.write("\t\t(get_model_by_name('" + Model.__name__ + "'), Q(**{'" + str(entity.query_str) +
                           "': model_object."
                           + str(entity.value) + " })),\n")
            except:
                continue
        file.write('\t]'
                   '\n\n\treturn filters')
        file.close()

    class Meta:
        app_label = 'core'

    @classmethod
    @app.task
    def write_filters(cls):
        print('process started')
        filters = RoleFilter.objects.all()
        for filter in filters:
            print('writing filter to file')
            filter.write_filter_to_file()
        print('finishing process')
