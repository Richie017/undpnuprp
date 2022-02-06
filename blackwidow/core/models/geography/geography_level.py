from collections import OrderedDict

from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django.db import models
from django.db.models.query_utils import Q
from rest_framework import serializers

from blackwidow.core.models.contracts.configurabletype import ConfigurableType
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.modules.module import BWModule
from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment
from blackwidow.core.models.roles.role import Role
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.constants.cache_constants import GEOGRAPHY_HIERARCHY_CACHE_PREFIX, ONE_MONTH_TIMEOUT, \
    GEOGRAPHY_LEVEL_CACHE_PREFIX
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, save_audit_log
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_compress_name
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'Tareq'


@decorate(expose_api('geography-level'), is_object_context,
          save_audit_log,
          route(route='geography-level', group='Other Admin', group_order=1, item_order=1, module=ModuleEnum.Settings,
                display_name="Geography Level"))
class GeographyLevel(ConfigurableType):
    parent = models.ForeignKey('core.GeographyLevel', null=True)

    def save(self, *args, organization=None, **kwargs):
        super().save(*args, organization=organization, **kwargs)
        self.initialize_permission(organization=organization, *args, **kwargs)

    @classmethod
    def table_columns(cls):
        return 'render_code', 'name', 'parent', 'created_by', 'date_created:Created On', 'last_updated'

    @classmethod
    def get_cached_level_by_id(cls, level_id):
        cache_key = GEOGRAPHY_LEVEL_CACHE_PREFIX + str(level_id)
        level = CacheManager.get_from_cache_by_key(key=cache_key)
        if level is None:
            level = cls.objects.get(pk=level_id)
            CacheManager.set_cache_element_by_key(key=cache_key, value=level, timeout=ONE_MONTH_TIMEOUT)
        return level

    @property
    def get_hierarchy_level(self):
        cache_key = GEOGRAPHY_HIERARCHY_CACHE_PREFIX + str(self.pk)
        level = CacheManager.get_from_cache_by_key(key=cache_key)
        if level is None:
            if self.parent_id is None:
                level = 1
            else:
                level = 1 + self.parent.get_hierarchy_level
            CacheManager.set_cache_element_by_key(key=cache_key, value=level, timeout=ONE_MONTH_TIMEOUT)
        return level

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['parent'] = self.parent
        details['created_by'] = self.created_by
        details['created on'] = self.date_created
        details['last_updated_by'] = self.last_updated_by
        details['last_updated'] = self.last_updated
        return details

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Entries',
                access_key='entries',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='core.Geography',
                queryset=None,
                queryset_filter=Q(**{'level__pk': self.pk})
            ), ]

    @classmethod
    def get_serializer(cls):
        CTSerializer = ConfigurableType.get_serializer()

        class GeographyLevelSerializer(CTSerializer):
            level = serializers.SerializerMethodField()

            def get_level(self, obj):
                return obj.get_hierarchy_level

            class Meta:
                model = cls
                fields = 'id', 'code', 'level', 'name', 'parent', 'last_updated'

        return GeographyLevelSerializer

    def initialize_permission(self, organization=None, *args, **kwargs):
        from blackwidow.core.models.geography.geography import Geography
        try:
            if organization is None:
                if organization in kwargs:
                    organization = kwargs['organization']
                else:
                    organization = CrequestMiddleware.get_request().c_organization

            # Load Module
            Model = Geography
            module = Model.get_model_meta('route', 'module')
            bw_module, result = \
                BWModule.objects.get_or_create(name=module.value['title'], organization=organization)
            bw_module.module_url = module.value['route']
            bw_module.module_order = module.value['order']
            bw_module.parent = None
            bw_module.save()

            group = Model.get_model_meta('route', 'group')
            group_order = Model.get_model_meta('route', 'group_order')

            sub_module, result = \
                BWModule.objects.get_or_create(name=group, organization=organization)
            sub_module.parent = bw_module
            sub_module.module_order = 1000 if group_order is None else group_order
            sub_module.save()

            # Load Permission
            permission, result = RolePermission.objects.get_or_create(
                context=bw_compress_name(self.name),
                organization=organization
            )
            permission.display_name = self.name
            permission.group_name = group
            permission.route_name = Model.get_proxy_route_name(proxy_model_name=self.name)
            permission.item_order = self.get_hierarchy_level + 1
            permission.hide = False
            permission.app_label = Model._meta.app_label
            permission.save()

            for role in Role.objects.all():
                mass, created = ModulePermissionAssignment.objects.get_or_create(
                    organization=organization, module=bw_module, role=role
                )
                mass.access = 1
                mass.visibility = 0
                mass.save()

                mass, created = ModulePermissionAssignment.objects.get_or_create(
                    organization=organization, module=sub_module, role=role
                )
                mass.access = 1
                mass.visibility = 0
                mass.save()

                permission_assignment, created = RolePermissionAssignment.objects.get_or_create(
                    organization=organization, permission=permission, role=role
                )
                permission_assignment.visibility = 0
                permission_assignment.access = 4 if role.name == 'Developer' else 1
                permission_assignment.save()

                # generate role specific js menu config if JS_MENU_RENDERING is enabled
                if hasattr(settings, 'ENABLE_JS_MENU_RENDERING') and settings.ENABLE_JS_MENU_RENDERING:
                    from blackwidow.core.views.menu.menu_renderer_view import MenuRendererView
                    MenuRendererView.save_role_menu_config(role=role)
        except Exception as exp:
            ErrorLog.log(exp=exp)
