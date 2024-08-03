import os
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import transaction

from blackwidow.core.models.common.week_day import WeekDay
from blackwidow.core.models.roles.developer import Developer
from blackwidow.core.views.menu.menu_renderer_view import MenuRendererView
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from config.apps import INSTALLED_APPS
from settings import ORGANIZATION_NAME

get_model = apps.get_model
PROJECT_PATH = os.path.abspath(".")

__author__ = 'mahmudul'


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.requires_system_checks = True
        self.can_import_settings = True
        self.leave_locale_alone = False

    def validate(self, app=None, display_num_errors=False):
        return False

    def add_argument(self, parser):
        pass

    def load_nested_submodule(self, m_class, modules, parent, org, index):
        m = modules[0]
        _m, _r = m_class.objects.get_or_create(organization=org, name=m, parent=parent)
        if _r:
            self.stdout.write(('        ').rjust(index, ' ') + _m.name)
        if len(modules) > 1:
            self.load_nested_submodule(m_class, modules[1:], _m, org, index + 4)

    def load_modules(self, *args, **options):
        Organization = get_model('core', 'Organization')
        Module = get_model('core', 'BWModule')
        org = Organization.objects.filter(is_master=True)[0]
        self.stdout.write('searching for modules & submodules...')
        route_models = get_models_with_decorator('route', INSTALLED_APPS, include_class=True)
        self.stdout.write(str(len(route_models)) + ' routes found.\n')
        # self.stdout.write('Deleting modules...')
        # Module.objects.filter(~Q(parent=None)).delete()
        # Module.objects.filter(Q(parent=None)).delete()
        self.stdout.write('Importing modules...')
        for m in route_models:
            module = m.get_model_meta('route', 'module')
            if module is None:
                self.stdout.write('modules not found for model ... ' + m.__name__)
                continue
            group = m.get_model_meta('route', 'group')
            group_order = m.get_model_meta('route', 'group_order')

            result = False  # for existing module
            bw_module = Module.objects.filter(
                name=module.value['title'],
                organization=org,
                parent__isnull=True
            ).first()

            if bw_module is None:
                bw_module = Module(
                    name=module.value['title'],
                    organization=org,
                    parent=None
                )
                result = True  # for newly created module

            bw_module.module_url = module.value['route']
            bw_module.module_order = module.value['order']
            bw_module.icon = module.value['icon']
            bw_module.save()

            if result:
                self.stdout.write('module created ... ... ... ' + bw_module.name)

            if isinstance(group, (tuple, list)):
                self.load_nested_submodule(Module, group, bw_module, org, 30)
            else:
                result = False  # for existing sub module
                sub_module = Module.objects.filter(
                    name=group,
                    organization=org,
                    parent=bw_module
                ).first()

                if sub_module is None:
                    sub_module = Module(name=group, organization=org, parent=bw_module)
                    result = True  # for newly created submodule

                sub_module.module_order = 1000 if group_order is None else group_order
                sub_module.save()
                if result:
                    self.stdout.write(('        ').rjust(30, ' ') + sub_module.name)
        self.stdout.write('Modules imported.\n')

    def load_roles(self, *args, **options):
        Organization = get_model('core', 'Organization')
        org = Organization.objects.filter(is_master=True)[0]
        self.stdout.write('searching for roles...')
        role_models = get_models_with_decorator('is_role_context', INSTALLED_APPS, include_class=True)
        self.stdout.write(str(len(role_models)) + ' roles found.\n')
        self.stdout.write('Importing roles...')
        Role = get_model('core', 'Role')
        imported = 0
        reassigned = 0
        updated = 0
        for r in role_models:
            name = r.__name__
            display_name = r.get_model_meta('route', 'display_name') or name

            role_by_name = Role.objects.filter(name=name, organization=org).first()
            role_by_display = Role.objects.filter(name=display_name, organization=org).first()
            if role_by_name is None and role_by_display is None:
                role = Role()
                role.name = display_name
                role.organization = org
                role.is_implemented = True
                role.save()
                imported += 1
            elif role_by_name and role_by_display is None:
                role_by_name.name = display_name
                role_by_name.is_implemented = True
                role_by_name.save()
                reassigned += 1
            else:
                role_by_display.is_implemented = True
                role_by_display.save()
                updated += 1

        self.stdout.write(str(imported) + ' roles imported.')
        self.stdout.write(str(reassigned) + ' roles reassigned.')
        self.stdout.write(str(updated) + ' roles updated.')

    def load_permissions(self, *args, **kwargs):
        permission_models = get_models_with_decorator('is_object_context', INSTALLED_APPS, include_class=True)
        Role = get_model('core', 'Role')
        RolePermissionAssignment = get_model('core', 'RolePermissionAssignment')
        RolePermission = get_model('core', 'RolePermission')
        Module = get_model('core', 'BWModule')
        ModuleAssignment = get_model('core', 'ModulePermissionAssignment')
        all_roles = Role.objects.all()
        Organization = get_model('core', 'Organization')
        org = Organization.objects.filter(is_master=True)[0]

        self.stdout.write('removing unnecessary permissions.')
        RolePermission.objects.exclude(context__in=[model.__name__ for model in permission_models]).delete()
        self.stdout.write('.... Done')

        self.stdout.write('loading permissions...')
        for model in permission_models:
            perm, result = RolePermission.objects.get_or_create(context=model.__name__, organization=org)
            d_name = model.get_model_meta('route', 'display_name')
            perm.display_name = model.__name__ if d_name is None or d_name == '' else d_name
            g_name = model.get_model_meta('route', 'group')
            perm.group_name = model.__name__ if g_name is None or g_name == '' else g_name
            r_name = model.get_model_meta('route', 'route')
            perm.route_name = '' if r_name is None or r_name == '' else r_name
            item_order = model.get_model_meta('route', 'item_order')
            perm.item_order = 1000 if item_order is None else item_order

            top_module = model.get_model_meta('route', 'module')
            if top_module:
                tm_name = top_module.value['title']
                sub_module = Module.objects.filter(name=g_name, parent__name=tm_name, organization=org).first()
                if sub_module:
                    perm.group = sub_module  # assign sub module as group reference

            hide = model.get_model_meta('route', 'hide')
            perm.hide = False if hide is None else hide
            app_label = model._meta.app_label
            perm.app_label = '' if app_label is None else app_label
            perm.save()

        for role in all_roles:
            modules = Module.objects.all()
            for m in modules:
                mass = ModuleAssignment.objects.filter(
                    module=m, role=role,
                    organization=org
                ).first()
                if mass is None:
                    mass = ModuleAssignment()
                    mass.organization = org
                    mass.module = m
                    mass.role = role
                    mass.access = 1
                    mass.visibility = 0
                    mass.save()
            BWPermissionManager.get_module_permissions_by_role(role=role, overwrite=True)

            permissions = RolePermission.objects.all()
            for permission in permissions:
                if role.permissions.filter(context=permission.context).exists():
                    continue

                perm = RolePermissionAssignment()
                perm.permission = permission
                perm.role = role
                perm.organization = org
                perm.visibility = 0
                perm.access = 4 if role.name == 'Developer' else 1
                perm.save()
            BWPermissionManager.get_access_permissions_by_role(role=role, overwrite=True)
            self.stdout.write('permissions loaded for ...' + role.name)

        # checking js menu rendering is enable or not, if enabled then generate js menu config for roles
        if hasattr(settings, 'ENABLE_JS_MENU_RENDERING') and settings.ENABLE_JS_MENU_RENDERING:
            for _role in all_roles:
                MenuRendererView.save_role_menu_config(role=_role)

    def load_organizations(self, *args, **options):
        self.stdout.write('loading base organization...')
        Organization = get_model('core', 'Organization')
        org = Organization()
        if Organization.objects.filter(is_master=True).count() == 0:
            org.name = ORGANIZATION_NAME
            org.is_master = True
            org.save()
            self.stdout.write('1 organization added.')
        else:
            org = Organization.objects.filter(is_master=True).first()
            org.name = ORGANIZATION_NAME
            org.save()
            self.stdout.write('1 organization Updated.')

    def load_user(self, *args, **options):
        Organization = get_model('core', 'Organization')
        Role = get_model('core', 'Role')
        User = get_model('auth', 'User')

        org = Organization.objects.filter(is_master=True)[0]
        role = Role.objects.filter(name=Developer.get_model_meta('route', 'display_name') or Developer.__name__)[0]
        self.stdout.write('adding super user...')
        ConsoleUser = get_model('core', 'SystemAdmin')

        if ConsoleUser.objects.filter(role=role).count() == 0:
            user = ConsoleUser()
            if User.objects.filter(username='blackwidow').count() == 0:
                auth_user = User()
                auth_user.username = 'blackwidow'
                auth_user.save()
                auth_user.set_password('rAnd0mPA55')
                auth_user.save()
                self.stdout.write('auth user added...')
            else:
                auth_user = User.objects.filter(username='blackwidow').first()
                self.stdout.write('auth user already exists...skipping')
            user.user = auth_user
            user.is_super = True
            user.name = 'Super Admin'
            user.role = role
            user.organization = org
            user.save()
            self.stdout.write('super user added...')
        else:
            self.stdout.write('super user already exists...skipping')

    def load_initial_data(self, *args, **options):
        Organization = get_model('core', 'Organization')
        org = Organization.objects.filter(is_master=True)[0]
        init_models = get_models_with_decorator('loads_initial_data', INSTALLED_APPS, include_class=True)
        ConsoleUser = get_model('core', 'ConsoleUser')
        super_user = ConsoleUser.objects.filter(is_super=True)[0]
        for x in init_models:
            if x.objects.exists():
                self.stdout.write("objects already exists for .... " + x.__name__ + '.. skipping ')
                continue
            self.stdout.write("loading initial data for .... " + x.__name__)
            with transaction.atomic():
                pass
                # x.init_default_objects(user=super_user, organization=org)
                # m = x()
                # m.load_initial_data(user=super_user, org=org, index=n, date=Clock.timestamp(), timestamp=Clock.timestamp())
                # m.save()
            self.stdout.write(x.__name__ + "s added.")

    def load_weekdays(self, *args, **kwargs):
        days = [
            "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ]
        for day in days:
            weekday_objs = WeekDay.objects.filter(name=day)
            if not weekday_objs.exists():
                with transaction.atomic():
                    WeekDay(name=day).save()

    def load_domain_info(self, *args, **kwargs):
        self.stdout.write('loading base domain information...')
        from settings import SITE_NAME
        site_objects = Site.objects.filter(name=SITE_NAME)
        if site_objects.exists():
            site_obj = site_objects.first()
            site_obj.name = SITE_NAME
            site_obj.domain = SITE_NAME
            site_obj.save()
            self.stdout.write('domain information updated.')
        else:
            site_obj = Site()
            site_obj.name = SITE_NAME
            site_obj.domain = SITE_NAME
            site_obj.save()
            self.stdout.write('domain information added.')

    def apply_app_specific_initialize(self, *args, **kwargs):
        for app in INSTALLED_APPS:
            try:
                init_module = import_module(str(app) + '.management.initialize')
                if init_module:
                    print(">>> Initializing for: {}".format(app, ))
                    init_module.initialize(*args, **kwargs)
            except Exception as exp:
                pass

    def handle(self, *args, **options):
        actions = [self.load_weekdays, self.load_domain_info, self.load_organizations, self.load_roles,
                   self.load_modules,
                   self.load_permissions, self.load_user, self.load_initial_data, self.apply_app_specific_initialize]
        i = 1
        max = len(actions)
        for a in actions:
            self.stdout.write("step: " + str(i) + "/" + str(max))
            a(*args, **options)
            self.stdout.write('\n')
            i += 1
