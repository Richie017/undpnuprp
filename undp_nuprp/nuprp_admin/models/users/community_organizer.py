from collections import OrderedDict

from django.contrib.auth.models import User

from blackwidow.core.models import ExporterConfig, ExporterColumnConfig, EmailAddress, PhoneNumber, ErrorLog, Role, \
    ImporterConfig, ImporterColumnConfig, Geography, ContactAddress
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.core.viewmodels.tabs_config import TabViewAction, TabView
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.route_partial_routes import route, partial_route
from blackwidow.engine.decorators.utility import decorate, is_object_context, is_role_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import CDC

__author__ = "Ziaul Haque"


@decorate(is_object_context, is_role_context, enable_export, enable_import,
          route(route='community-organizer', group='Users', module=ModuleEnum.Settings,
                display_name='Community Organizer', group_order=1, item_order=8),
          partial_route(relation='normal', models=[CDC, ]))
class CommunityOrganizer(ConsoleUser):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @property
    def render_email_address(self):
        try:
            return self.emails.first().email
        except:
            return 'N/A'

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'name', 'render_email_address',
            'created_by', 'date_created', 'last_updated'
        )

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedExport,
                ViewActionEnum.AdvancedImport]

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

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        columns = [
            ExporterColumnConfig(column=0, column_name='Division',
                                 property_name='division', ignore=False),
            ExporterColumnConfig(column=1, column_name='City',
                                 property_name='city', ignore=False),
            ExporterColumnConfig(column=2, column_name='Ward',
                                 property_name='ward', ignore=False),
            ExporterColumnConfig(column=3, column_name='Username',
                                 property_name='user_name', ignore=False),
            ExporterColumnConfig(column=4, column_name='Name',
                                 property_name='name', ignore=False),
            ExporterColumnConfig(column=5, column_name='Email',
                                 property_name='email', ignore=False),
            ExporterColumnConfig(column=6, column_name='Phone',
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
        workbook.cell(row=row, column=column).value = 'Division'
        workbook.cell(row=row, column=column + 1).value = 'City'
        workbook.cell(row=row, column=column + 2).value = 'Ward'
        workbook.cell(row=row, column=column + 3).value = 'UserName'
        workbook.cell(row=row, column=column + 4).value = 'Name'
        workbook.cell(row=row, column=column + 5).value = 'Email'
        workbook.cell(row=row, column=column + 6).value = 'Phone'
        row += 1
        community_organizer_queryset = CommunityOrganizer.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).values(
            'name', 'addresses__geography__parent__parent__name',
            'addresses__geography__parent__name', 'user__username',
            'addresses__geography__name', 'phones__phone', 'emails__email'
        )
        for entry in community_organizer_queryset:
            column = 1
            workbook.cell(row=row, column=column).value = entry['addresses__geography__parent__parent__name']
            workbook.cell(row=row, column=column + 1).value = entry['addresses__geography__parent__name']
            workbook.cell(row=row, column=column + 2).value = entry['addresses__geography__name']
            workbook.cell(row=row, column=column + 3).value = entry['user__username']
            workbook.cell(row=row, column=column + 4).value = entry['name']
            workbook.cell(row=row, column=column + 5).value = entry['emails__email']
            workbook.cell(row=row, column=column + 6).value = entry['phones__phone']
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
            ImporterColumnConfig(column=0, column_name='Division',
                                 property_name='division', ignore=False),
            ImporterColumnConfig(column=1, column_name='City',
                                 property_name='city', ignore=False),
            ImporterColumnConfig(column=2, column_name='Ward',
                                 property_name='ward', ignore=False),
            ImporterColumnConfig(column=3, column_name='Username',
                                 property_name='user_name', ignore=False),
            ImporterColumnConfig(column=4, column_name='Name',
                                 property_name='name', ignore=False),
            ImporterColumnConfig(column=5, column_name='Email',
                                 property_name='email', ignore=False),
            ImporterColumnConfig(column=6, column_name='Phone No',
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
                division = str(item[str(0)])
                city = str(item[str(1)])
                ward = str(item[str(2)])
                name = str(item[str(3)])
                email = str(item[str(4)])
                phone_no = str(item[str(5)])

                if phone_no:
                    django_user, created = User.objects.get_or_create(username=phone_no)
                    django_user.set_password('1234')
                    django_user.save()

                    co = cls.objects.filter(user=django_user, organization=organization, role=role).first()
                    if co is None:
                        co = cls.objects.get_or_create(
                            name=name,
                            user=django_user,
                            organization=organization,
                            role=role,
                            created_by=user
                        )[0]
                    ward = Geography.objects.filter(name=ward, parent__name=city, parent__parent__name=division,
                                                    level__name='Ward').first()
                    if ward:
                        address = ContactAddress.objects.create(geography_id=ward.pk)
                        co.addresses.clear()
                        co.addresses.add(address)
                    if email:
                        email_address = EmailAddress.objects.create(email=email)
                        co.emails.add(email_address)
                    if phone_no:
                        phone = PhoneNumber.objects.create(phone=phone_no)
                        co.phones.add(phone)
            except Exception as expt:
                ErrorLog.log(exp=expt)
