from collections import OrderedDict

from django.contrib.auth.models import User

from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.emailaddress import EmailAddress
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.decorators import enable_import, enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, is_role_context, has_data_filter
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock

__author__ = 'Tareq'

from blackwidow.engine.routers.database_router import BWDatabaseRouter


@decorate(is_object_context, is_role_context, has_data_filter, enable_import,
          route(route='nuprp-expert', group='Users', module=ModuleEnum.Settings,
                display_name='Expert', group_order=1, item_order=6, hide=True))
class NUPRPExpert(ConsoleUser):
    @property
    def render_email_address(self):
        try:
            return self.emails.first().email
        except:
            return 'N/A'

    @property
    def render_city(self):
        try:
            return self.addresses.first().geography.name
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
        manage_buttons = super(ConsoleUser, cls).get_manage_buttons()
        manage_buttons += [ViewActionEnum.AdvancedImport, ViewActionEnum.AdvancedExport]
        return manage_buttons

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

    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        columns = [
            ExporterColumnConfig(column=0, column_name='City',
                                 property_name='city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Name',
                                 property_name='name', ignore=False),
            ExporterColumnConfig(column=2, column_name='Email',
                                 property_name='email', ignore=False),
            ExporterColumnConfig(column=3, column_name='Phone No',
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
        workbook.cell(row=row, column=column + 1).value = 'Name'
        workbook.cell(row=row, column=column + 2).value = 'Email'
        workbook.cell(row=row, column=column + 3).value = 'Phone'
        row += 1
        nuprp_expert_queryset = NUPRPExpert.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).values('name', 'addresses__geography__name', 'phones__phone', 'emails__email')
        for entry in nuprp_expert_queryset:
            column = 1
            workbook.cell(row=row, column=column).value = entry['addresses__geography__name']
            workbook.cell(row=row, column=column + 1).value = entry['name']
            workbook.cell(row=row, column=column + 2).value = entry['emails__email']
            workbook.cell(row=row, column=column + 3).value = entry['phones__phone']
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
            ImporterColumnConfig(column=1, column_name='Name',
                                 property_name='name', ignore=False),
            ImporterColumnConfig(column=2, column_name='Email',
                                 property_name='email', ignore=False),
            ImporterColumnConfig(column=3, column_name='Phone No',
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
                name = str(item[str(1)])
                email = item[str(2)]
                phone_no = str(item[str(3)])

                if phone_no:
                    django_user, created = User.objects.get_or_create(username=phone_no)
                    django_user.set_password('1234')
                    django_user.save()

                    nuprp_expert = cls.objects.filter(
                        name=name, user=django_user, organization=organization, role=role
                    ).first()
                    if nuprp_expert is None:
                        nuprp_expert = cls.objects.get_or_create(
                            name=name, user=django_user,
                            organization=organization,
                            role=role, created_by=user
                        )[0]
                    city = Geography.objects.filter(name=city, level__name='Pourashava/City Corporation').first()
                    if city:
                        address = ContactAddress.objects.create(geography_id=city.pk)
                        nuprp_expert.addresses.clear()
                        nuprp_expert.addresses.add(address)
                        nuprp_expert.save()
                    if email:
                        email_address = EmailAddress.objects.create(email=email)
                        nuprp_expert.emails.add(email_address)
                    if phone_no:
                        phone = PhoneNumber.objects.create(phone=phone_no)
                        nuprp_expert.phones.add(phone)
            except Exception as expt:
                ErrorLog.log(exp=expt)
