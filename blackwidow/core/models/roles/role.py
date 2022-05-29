import hashlib

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.query_utils import Q
from rest_framework import serializers

from blackwidow.core.models.common.custom_field import CustomField
from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.modules.module import BWModule
from blackwidow.core.models.permissions.query_filter import QueryFilter
from blackwidow.core.models.permissions.rolepermission import RolePermission
from blackwidow.core.viewmodels.tabs_config import TabView, TabViewAction
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.route_partial_routes import route, partial_route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions.exceptions import EntityNotDeletableException, BWException
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'mahmudul'


@decorate(is_object_context, enable_export, enable_import,
          route(route='roles', display_name='User Role', group='Other Admin', module=ModuleEnum.Settings),
          partial_route(relation='normal', models=[RolePermission, QueryFilter, CustomField, BWModule]))
class Role(OrganizationDomainEntity):
    priority = models.IntegerField(default=0)
    name = models.CharField(max_length=254, default='', unique=True)
    landing_url = models.CharField(max_length=254, default='')
    permissions = models.ManyToManyField(RolePermission, through='core.RolePermissionAssignment')
    modules = models.ManyToManyField(BWModule, through='core.ModulePermissionAssignment')
    is_implemented = models.BooleanField(default=0)
    filters = models.ManyToManyField(QueryFilter)
    parent = models.ManyToManyField('self', symmetrical=False)
    custom_fields = models.ManyToManyField(CustomField)
    get_alert = models.BooleanField(default=0)

    @classmethod
    def system_admin(cls):
        return cls.objects.get(name='Developer')

    @classmethod
    def get_dependent_field_list(cls):
        return ['custom_fields']

    @property
    def get_rename(self):
        if self.name == 'ServicePerson':
            return 'Sales Officer'
        return self.name

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            custom_fields = CustomField.get_serializer()(many=True, required=False)
            name = serializers.CharField(max_length=254, default='')

            class Meta(ss.Meta):
                model = Role
                fields = ('id', 'name', 'custom_fields')
                read_only_fields = ss.Meta.read_only_fields + ('organization', 'created_by', 'last_updated_by')
                fields = ('id', 'code', 'priority', 'name', 'landing_url', 'custom_fields')

        return Serializer

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedExport,
                ViewActionEnum.AdvancedImport]

    @classmethod
    def get_button_title(cls, btn=ViewActionEnum.Details):
        if btn == ViewActionEnum.AdvancedExport:
            return 'Export'
        if btn == ViewActionEnum.AdvancedImport:
            return 'Import'
        return 'Action'

    @property
    def tabs_config(self):
        tabs = [
            TabView(
                title='User(s) in Role',
                access_key='users',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='core.ConsoleUser',
                queryset=None,
                queryset_filter=Q(**{'role__pk': self.pk})
            ),
            TabView(
                title='Custom Field(s)',
                access_key='custom_fields',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=CustomField,
                queryset=self.custom_fields.all(),
                queryset_filter=None,
                property=self.custom_fields,
                actions=[
                    TabViewAction(
                        title="Add",
                        action="action",
                        icon="icon-plus",
                        css_class='manage-action load-modal fis-plus-ico',
                        route_name=CustomField.get_route_name(action=ViewActionEnum.PartialCreate,
                                                              parent=self.__class__.__name__.lower())
                    ),
                    TabViewAction(
                        title="Delete",
                        action="close",
                        icon="icon-remove",
                        css_class='manage-action delete-item fis-remove-ico',
                        route_name=CustomField.get_route_name(action=ViewActionEnum.PartialDelete,
                                                              parent=self.__class__.__name__.lower())
                    )
                ]
            ),
            TabView(
                title='Top Menu Permission(s)',
                access_key='top_menus',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='core.ModulePermissionAssignment',
                child_tabs='modules,permissions',
                queryset=None,
                enable_inline_edit=True,
                queryset_filter=Q(**{'pk__in': self.get_parent_module_permission()})
            ),
            TabView(
                title='Module Permission(s)',
                access_key='modules',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='core.ModulePermissionAssignment',
                child_tabs='permissions',
                queryset=None,
                enable_inline_edit=True,
                queryset_filter=Q(**{'pk__in': self.get_child_module_permissions()})
            ),
            TabView(
                title='Object Permission(s)',
                access_key='permissions',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='core.RolePermissionAssignment',
                queryset=None,
                enable_inline_edit=True,
                queryset_filter=Q(**{'pk__in': self.get_object_permissions_names()})
            )
        ]
        return tabs

    def get_parent_module_permission(self):
        from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment

        parent_module_permissions = ModulePermissionAssignment.objects.filter(
            Q(module__parent=None) & Q(role_id=self.pk))
        module_permissions = parent_module_permissions.values_list('pk', flat=True)
        return module_permissions

    def get_child_module_permissions(self):
        from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment

        parent_module_permissions = ModulePermissionAssignment.objects.filter(
            Q(module__parent=None) & Q(role_id=self.pk) & Q(access__gt=0))
        parent_module_list = parent_module_permissions.values_list('module__pk', flat=True)
        child_module_permissions = ModulePermissionAssignment.objects.filter(
            ~Q(module__parent=None) & Q(role_id=self.pk))
        child_module_permissions = child_module_permissions.filter(
            Q(module__parent__id__in=parent_module_list))
        module_permissions = child_module_permissions.values_list('pk', flat=True)
        return module_permissions

    def get_object_permissions_names(self):
        from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
        from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment

        child_module_permissions = ModulePermissionAssignment.objects.using(
            BWDatabaseRouter.get_read_database_name()).filter(
            ~Q(module__parent=None) & Q(role_id=self.pk) & Q(access__gt=0))
        child_module_name_list = child_module_permissions.values_list('module__name', flat=True)
        object_permissions = RolePermissionAssignment.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            Q(role_id=self.pk))
        object_permissions_list = [8353]
        for object_permission in object_permissions:
            model_name = object_permission.permission.context
            model_objects = ContentType.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
                model=model_name.lower())
            
            for model_object in model_objects:
                model = apps.get_model(model_object.app_label, model_name)
                group = model.get_model_meta('route', 'group')
                if group in child_module_name_list:
                    object_permissions_list += [object_permission.pk]
                   
        object_permissions = object_permissions.filter(
            Q(pk__in=object_permissions_list)).values_list('pk', flat=True)
        return object_permissions

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = kwargs.get('user', None)
        if user:
            if user.role.id == self.id:
                raise EntityNotDeletableException("You cannot delete your own role.")

            if self.is_implemented:
                raise EntityNotDeletableException('This role is mandatory for running the system.'
                                                  ' Please contact system administrator to modify/delete this role.')
        else:
            raise BWException("You must provide user performing the operation as named parameter.")
        super().delete(*args, **kwargs)

    def get_choice_name(self):
        return self.name

    @classmethod
    def get_export_order_by(cls):
        return 'code'

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):
        for column in columns:
            workbook.cell(row=1, column=column.column + 1).value = column.column_name
        return workbook, row_number

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        columns = [
            ExporterColumnConfig(column=0, column_name='Code',
                                 property_name='code', ignore=False),
            ExporterColumnConfig(column=1, column_name='Name',
                                 property_name='name', ignore=False),
            ExporterColumnConfig(column=2, column_name='Module Name',
                                 property_name='module_get_name', ignore=False),
            ExporterColumnConfig(column=3, column_name='Permission Label',
                                 property_name='permission_get_app_label', ignore=False),
            ExporterColumnConfig(column=4, column_name='Permission Context',
                                 property_name='permission_get_context', ignore=False),
            ExporterColumnConfig(column=5, column_name='Access',
                                 property_name='get_access', ignore=False),
            ExporterColumnConfig(column=6, column_name='MD5 Hash',
                                 property_name='md5_hash', ignore=False)
        ]
        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
        from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment

        index = row_number
        for module_permission in ModulePermissionAssignment.objects.using(
                BWDatabaseRouter.get_export_database_name()).filter(role_id=self.pk):
            _hashable_text = ''
            for column in columns:
                module_prop = column.property_name.replace('module_', '')
                value = ''
                if hasattr(self, column.property_name):
                    value = getattr(self, column.property_name)
                    workbook.cell(row=index, column=column.column + 1).value = str(value) if value else ''
                elif hasattr(module_permission, module_prop):
                    value = getattr(module_permission, module_prop)
                    workbook.cell(row=index, column=column.column + 1).value = str(value) if value else ''
                if column.column == 6:
                    _hash = hashlib.md5(_hashable_text.encode('utf-8')).hexdigest()
                    workbook.cell(row=index, column=column.column + 1).value = _hash
                _hashable_text += str(value)
            index += 1
        for role_permission in RolePermissionAssignment.objects.using(BWDatabaseRouter.get_export_database_name()).filter(
                role_id=self.pk):
            _hashable_text = ''
            for column in columns:
                value = ''
                permission_prop = column.property_name.replace('permission_', '')
                if hasattr(self, column.property_name):
                    value = getattr(self, column.property_name)
                    workbook.cell(row=index, column=column.column + 1).value = str(value) if value else ''
                elif hasattr(role_permission, permission_prop):
                    value = getattr(role_permission, permission_prop)
                    workbook.cell(row=index, column=column.column + 1).value = str(value) if value else ''

                if column.column == 6:
                    _hash = hashlib.md5(_hashable_text.encode('utf-8')).hexdigest()
                    workbook.cell(row=index, column=column.column + 1).value = _hash
                _hashable_text += str(value)
            index += 1
        return self.pk, index

    @classmethod
    def finalize_export(cls, workbook=None, row_number=None, query_set=None, **kwargs):
        return workbook

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.save(**kwargs)
        columns = [
            ImporterColumnConfig(column=0, column_name='Code',
                                 property_name='code', ignore=False),
            ImporterColumnConfig(column=1, column_name='Name',
                                 property_name='name', ignore=False),
            ImporterColumnConfig(column=2, column_name='Module Name',
                                 property_name='module_get_name', ignore=False),
            ImporterColumnConfig(column=3, column_name='Permission Label',
                                 property_name='permission_get_app_label', ignore=False),
            ImporterColumnConfig(column=4, column_name='Permission Context',
                                 property_name='permission_get_context', ignore=False),
            ImporterColumnConfig(column=5, column_name='Access',
                                 property_name='get_access', ignore=False),
            ImporterColumnConfig(column=6, column_name='MD5 Hash',
                                 property_name='md5_hash', ignore=False)
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def run_post_processing_import(cls, items=[], user=None, organization=None, **kwargs):
        from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
        from blackwidow.core.models.permissions.rolepermission_assignment import RolePermissionAssignment
        for item in items:
            _role_code = item['0']
            _role_name = item['1']
            _module_name = item['2']
            _role_permission_app_label = item['3']
            _role_permission_context = item['4']
            _permission_access = item['5']
            _md5_hash = item['6']

            if any([not _role_code, not _role_name]):
                continue

            # check if the row is editable or not
            _hashable_text = ''
            _hashable_text += str(_role_code)
            _hashable_text += str(_role_name)
            _hashable_text += str(_module_name if _module_name else '')
            _hashable_text += str(_role_permission_app_label if _role_permission_app_label else '')
            _hashable_text += str(_role_permission_context if _role_permission_context else '')
            _hashable_text += str(_permission_access)

            _hash = hashlib.md5(_hashable_text.encode('utf-8')).hexdigest()

            if _hash == _md5_hash:
                continue

            # check row type(module permission row/ role permission row)
            is_module_permission_row = False
            if _module_name and not _role_permission_app_label and not _role_permission_context:
                is_module_permission_row = True

            role_objects = Role.objects.filter(name=_role_name)
            if role_objects.exists():
                role_obj = role_objects.first()
                if is_module_permission_row:
                    module_permissions = ModulePermissionAssignment.objects.filter(
                        role_id=role_obj.pk,
                        module__name=_module_name
                    )
                    if module_permissions.exists():
                        module_perm = module_permissions.first()
                        module_perm.access = 1 if _permission_access == 'Allow' else 0
                        module_perm.save()

                        # bulk update submodules access level of parent module
                        if not module_perm.module.parent and module_perm.access == 0:
                            submodule_names = module_perm.module.bwmodule_set.values_list('name', flat=True)
                            ModulePermissionAssignment.objects.filter(
                                role_id=role_obj.pk,
                                module__name__in=submodule_names
                            ).update(access=module_perm.access)
                else:
                    role_permissions = RolePermissionAssignment.objects.filter(
                        role_id=role_obj.pk,
                        permission__context=_role_permission_context,
                        permission__app_label=_role_permission_app_label
                    )
                    if role_permissions.exists():
                        role_perm = role_permissions.first()
                        if _permission_access == 'No Access':
                            role_perm.access = 0
                        elif _permission_access == 'View':
                            role_perm.access = 1
                        elif _permission_access == 'View/Edit':
                            role_perm.access = 2
                        elif _permission_access == 'View/Create/Edit':
                            role_perm.access = 3
                        elif _permission_access == 'View/Create/Edit/Delete':
                            role_perm.access = 4
                        role_perm.save()

    class Meta:
        app_label = 'core'
