from collections import OrderedDict

from django.contrib.auth.models import User
from django.db.models.query_utils import Q

from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.log.activation_log import ActivationLog
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.constants.cache_constants import MODEL_CACHE_PREFIX, ONE_MONTH_TIMEOUT
from blackwidow.engine.decorators.activation_process import deactivatable_model, reactivatable_model
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context, is_role_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'Tareq'

from blackwidow.engine.routers.database_router import BWDatabaseRouter


@decorate(save_audit_log, is_object_context, expose_api('enumerator'), is_role_context, enable_export, enable_import,
          deactivatable_model, reactivatable_model,
          route(route='enumerator', group='Users', module=ModuleEnum.Settings,
                display_name='Enumerator', group_order=1, item_order=9))
class Enumerator(ConsoleUser):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    def activate(self, *args, **kwargs):
        if self.user and not self.user.is_active:
            _user = self.user
            _user.is_active = True
            _user.save()
            _name = self.code + ': ' + self.name
            ActivationLog.log(model=self, name=_name, action='Activate')

    def deactivate(self, *args, **kwargs):
        if self.user and self.user.is_active:
            _user = self.user
            _user.is_active = False
            _user.save()
            _name = self.code + ': ' + self.name
            ActivationLog.log(model=self, name=_name, action='De-activate')

    @property
    def render_mobile_no(self):
        return self.user.username

    @classmethod
    def search_mobile_no(cls, queryset, value):
        return queryset.filter(user__username__icontains=value)

    @classmethod
    def search_status(cls, queryset, value):
        if str(value).lower() in 'active' and str(value).lower() in 'disabled':
            return queryset
        if str(value).lower() in 'active':
            return queryset.filter(user__is_active=True)
        if str(value).lower() in 'disabled':
            return queryset.filter(user__is_active=False)
        return Enumerator.objects.none()

    @classmethod
    def search_assigned_ward(cls, queryset, value):
        if ' ' in value:
            city = value.split(' ')[0]
            ward = ' '.join(value.split(' ')[1:])
            return queryset.filter(addresses__geography__parent__name__icontains=city,
                                   addresses__geography__name__icontains=ward)
        return queryset.filter(Q(**{'addresses__geography__parent__name__icontains': value}) | Q(
            **{'addresses__geography__name__icontains': value}))

    @property
    def render_status(self):
        if self.user.is_active:
            return 'Active'
        return 'Disabled'

    @property
    def render_assigned_ward(self):
        try:
            city = self.addresses.first().geography.parent.name
            ward = self.addresses.first().geography.name
            return str(city) + ' ' + str(ward)
        except:
            return 'N/A'

    @classmethod
    def table_columns(cls):
        return 'render_code', 'name', 'render_mobile_no', 'render_assigned_ward', 'render_status', 'created_by', \
               'date_created', 'last_updated',

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedImport,
                ViewActionEnum.AdvancedExport]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import"

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['login'] = self.user.username
        details['household_code_prefix'] = self.assigned_code if self.assigned_code else 'N/A'
        details['address'] = self.addresses.first()
        details['created_by'] = self.created_by
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        return details

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Survey(s)',
                access_key='survey',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='survey.SurveyResponse',
                queryset_filter=Q(**{'created_by': self.pk})
            ),
            TabView(
                title='Household(s)',
                access_key='household',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='nuprp_admin.Household',
                queryset_filter=Q(**{'created_by': self.pk})
            ),
        ]

    @property
    def ward(self):
        ward_cache_key = MODEL_CACHE_PREFIX + 'enumerator_ward_' + str(self.pk)
        cached_ward = CacheManager.get_from_cache_by_key(key=ward_cache_key)
        if cached_ward is None:
            cached_ward = self.addresses.first().geography_id
            CacheManager.set_cache_element_by_key(key=ward_cache_key, value=cached_ward, timeout=ONE_MONTH_TIMEOUT)
        return cached_ward

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        columns = [
            ExporterColumnConfig(column=0, column_name='City',
                                 property_name='city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Ward',
                                 property_name='ward', ignore=False),
            ExporterColumnConfig(column=2, column_name='Name',
                                 property_name='name', ignore=False),
            ExporterColumnConfig(column=3, column_name='Email',
                                 property_name='email', ignore=False),
            ExporterColumnConfig(column=4, column_name='Phone No',
                                 property_name='phone_no', ignore=False)
        ]
        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        return self.pk, row_number + 1

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, query_set=None, **kwargs):
        row = 1
        column = 1
        workbook.cell(row=row, column=column).value = 'City'
        workbook.cell(row=row, column=column + 1).value = 'Ward'
        workbook.cell(row=row, column=column + 2).value = 'Name'
        workbook.cell(row=row, column=column + 3).value = 'Email'
        workbook.cell(row=row, column=column + 4).value = 'Phone'
        row += 1
        enumerator_queryset = Enumerator.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).values(
            'name', 'addresses__geography__parent__name',
            'addresses__geography__name', 'phones__phone', 'emails__email'
        )
        for entry in enumerator_queryset:
            column = 1
            workbook.cell(row=row, column=column).value = entry['addresses__geography__parent__name']
            workbook.cell(row=row, column=column + 1).value = entry['addresses__geography__name']
            workbook.cell(row=row, column=column + 2).value = entry['name']
            workbook.cell(row=row, column=column + 3).value = entry['emails__email']
            workbook.cell(row=row, column=column + 4).value = entry['phones__phone']
            row += 1
        return workbook, row

    @classmethod
    def finalize_export(cls, workbook=None, row_count=None, **kwargs):
        file_name = '%s_%s' % (cls.__name__, Clock.timestamp())
        return workbook, file_name

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)
        columns = [
            ImporterColumnConfig(column=0, column_name='City',
                                 property_name='city', ignore=False),
            ImporterColumnConfig(column=1, column_name='Ward',
                                 property_name='ward', ignore=False),
            ImporterColumnConfig(column=2, column_name='Name',
                                 property_name='name', ignore=False),
            ImporterColumnConfig(column=3, column_name='Email',
                                 property_name='email', ignore=False),
            ImporterColumnConfig(column=4, column_name='Phone No',
                                 property_name='phone_no', ignore=False)
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        _role_name = cls.get_model_meta('route', 'display_name') or cls.__name__
        role = Role.objects.filter(name=_role_name).first()
        for item in items:
            try:
                city = str(item[str(0)])
                ward = str(item[str(1)])
                name = str(item[str(2)])
                email = item[str(3)]
                phone_no = item[str(4)]

                if phone_no is None or phone_no == '':
                    continue

                if phone_no:
                    phone_no = str(phone_no)
                    django_user, created = User.objects.get_or_create(username=phone_no)
                    django_user.set_password('1234')
                    django_user.save()

                    enumerator = cls.objects.filter(user=django_user, organization=organization, role=role).first()
                    if enumerator is None:
                        enumerator, created = cls.objects.get_or_create(
                            user=django_user, organization=organization, role=role
                        )
                        enumerator.name = name
                        enumerator.created_by = user
                        enumerator.save()

                    ward = Geography.objects.filter(name=ward, parent__name=city, level__name='Ward').first()
                    if ward:
                        address = ContactAddress.objects.create(geography_id=ward.pk)
                        enumerator.addresses.clear()
                        enumerator.addresses.add(address)

                        # Create assigned code
                        city = ward.parent
                        index = cls.all_objects.filter(addresses__geography__parent_id=city.pk).count()
                        ward_name = ward.name
                        if len(ward.name) < 2:
                            ward_name = '0' + ward.name
                        elif len(ward.name) > 2:
                            ward_name = ward.name[:2]
                        city_name = city.short_code
                        if not enumerator.assigned_code:
                            enumerator.assigned_code = '%2s%2s%03d' % (city_name, ward_name, index)
                        enumerator.save()
                    if email:
                        email_address = EmailAddress.objects.create(email=email)
                        enumerator.emails.add(email_address)

                    phone = PhoneNumber.objects.create(phone=phone_no)
                    enumerator.phones.add(phone)
            except Exception as exp:
                ErrorLog.log(exp=exp)

    @classmethod
    def get_serializer(cls):
        CUSerializer = ConsoleUser.get_serializer()

        class EnumeratorSerializer(CUSerializer):
            class Meta:
                model = cls
                fields = ('id', 'code', 'name', 'ward', 'last_updated')

        return EnumeratorSerializer
