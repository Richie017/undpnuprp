import uuid
from datetime import date, datetime

from django import forms
from django.db import models
from django.forms import Form
from django.utils.safestring import mark_safe
from django.conf import settings

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography, ImporterConfig, ImporterColumnConfig, ExporterConfig, ExporterColumnConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import is_object_context, decorate
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = "Ziaul Haque"

S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED


@decorate(is_object_context, route(route='meeting', group='Planning and Urban Governance',
                                   module=ModuleEnum.Analysis, display_name='Meeting',
                                   group_order=1, item_order=2), enable_import, enable_export)
class Meeting(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True)
    ward_number = models.CharField(max_length=20, null=True, blank=True)
    meeting = models.CharField(max_length=255, null=True, blank=True)
    standing_committee_name = models.CharField(max_length=255, null=True, blank=True)
    number_of_approved_members_of_the_committee = models.IntegerField(null=True, blank=True, default=0)
    meeting_date = models.DateField(default=None, null=True)

    number_of_male_participants = models.IntegerField(null=True, blank=True, default=0)
    number_of_female_participants = models.IntegerField(null=True, blank=True, default=0)
    number_of_disabled_male_participants = models.IntegerField(null=True, blank=True, default=0)
    number_of_disabled_female_participants = models.IntegerField(null=True, blank=True, default=0)
    number_of_total_participants = models.IntegerField(null=True, blank=True, default=0)
    remarks = models.TextField(null=True, blank=True)
    attachment = models.ForeignKey('core.FileObject', null=True, blank=True)

    class Meta:
        app_label = 'nuprp_admin'

    @property
    def render_minutes_of_the_meeting(self):
        return self.attachment.description if self.attachment else "N/A"

    @property
    def render_attachment(self):
        _url = self.attachment.get_file_access_path() if self.attachment.file else None
        if _url and not S3_STATIC_ENABLED:
            _url = _url.replace('static_media/static_media/', 'static_media/')
        _title = '<i class="fa fa-download" aria-hidden="true"></i>'
        return 'N/A' if not _url else mark_safe(
            '<a title="Click to download this item" href="' + _url + '" >' + _title + '</a>')

    @property
    def render_attachment_link(self):
        _url = self.attachment.get_file_access_path() if self.attachment.file else None
        if _url and not S3_STATIC_ENABLED:
            _url = _url.replace('static_media/static_media/', 'static_media/')
            _url = settings.SITE_ROOT + _url[1:]
        return 'N/A' if not _url else _url

    @classmethod
    def table_columns(cls):
        return [
            'code', 'city', 'ward_number:ward', 'meeting', 'standing_committee_name:Which Standing Committee?',
            'meeting_date:date', 'created_by', 'date_created', 'last_updated'
        ]

    @property
    def detail_title(self):
        return self.code

    @classmethod
    def details_view_fields(cls):
        return [
            'detail_title',
            'code>Basic Info', 'city>Basic Info', 'ward_number:Ward>Basic Info', 'meeting>Basic Info',
            'standing_committee_name:Which Standing Committee?>Basic Info',
            'number_of_approved_members_of_the_committee>Basic Info', 'meeting_date:Date>Basic Info',
            'render_minutes_of_the_meeting:Minutes of the meeting (With the meeting title)>Basic Info',
            'render_attachment:Minutes of the meeting attachment>Basic Info',

            'number_of_male_participants:Male>Participants', 'number_of_female_participants:Female>Participants',
            'number_of_disabled_male_participants:Disable (Male)>Participants',
            'number_of_disabled_female_participants:Disable (Female)>Participants',
            'number_of_total_participants:Total>Participants',

            'created_by>Audit Info', 'date_created>Audit Info', 'last_updated_by>Audit Info', 'last_updated>Audit Info',
        ]

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete,
            ViewActionEnum.AdvancedImport, ViewActionEnum.AdvancedExport
        ]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedImport:
            return "Import"
        if button == ViewActionEnum.AdvancedExport:
            return "Export"

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)

        columns = [
            ImporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ImporterColumnConfig(column=1, column_name='Ward', property_name='ward_number',
                                 ignore=False),
            ImporterColumnConfig(column=2, column_name='Meeting',
                                 property_name='meeting', ignore=False),
            ImporterColumnConfig(column=3, column_name='Which standing committee',
                                 property_name='standing_committee_name', ignore=False),
            ImporterColumnConfig(column=4, column_name='Date', property_name='meeting_date', ignore=False),
            ImporterColumnConfig(column=5, column_name='Minutes of the meeting (With the meeting title)',
                                 property_name='remarks', ignore=False),
            ImporterColumnConfig(column=6, column_name='Male',
                                 property_name='number_of_male_participants', ignore=False),
            ImporterColumnConfig(column=7, column_name='Female',
                                 property_name='number_of_female_participants', ignore=False),
            ImporterColumnConfig(column=8, column_name='Disable (Male)',
                                 property_name='number_of_disabled_male_participants', ignore=False),
            ImporterColumnConfig(column=9, column_name='Disable (Female)',
                                 property_name='number_of_disabled_female_participants', ignore=False),
            ImporterColumnConfig(column=10, column_name='Total',
                                 property_name='number_of_total_participants', ignore=False),
            ImporterColumnConfig(column=11, column_name='Number of approved members of the committee',
                                 property_name='number_of_approved_members_of_the_committee', ignore=False)
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
        timestamp = Clock.timestamp()
        create_list = []

        for index, item in enumerate(items):
            city = str(item['0']).strip()
            ward = str(item['1']).strip()
            if len(ward) == 1:
                ward = "0" + str(ward)
            meeting = str(item['2']).strip()
            standing_committee = str(item['3']).strip()
            meeting_date = str(item['4']).strip()
            remarks = str(item['5']).strip()  # do nothing
            male = str(item['6']).strip()
            female = str(item['7']).strip()
            disabled_male = str(item['8']).strip()
            disabled_female = str(item['9']).strip()
            total = str(item['10']).strip()
            number_of_approved_members_of_the_committee = str(item['11']).strip()

            city_ = Geography.objects.filter(level__name='Pourashava/City Corporation', name__iexact=city)

            if city_.exists():
                new_ = Meeting(
                    organization=organization,
                    city=city_.first(),
                    ward_number=ward,
                    meeting=meeting,
                    standing_committee_name=standing_committee,
                    meeting_date=meeting_date,
                    number_of_male_participants=male,
                    number_of_female_participants=female,
                    number_of_disabled_male_participants=disabled_male,
                    number_of_disabled_female_participants=disabled_female,
                    number_of_total_participants=total,
                    date_created=timestamp,
                    created_by=user,
                    tsync_id=uuid.uuid4(),
                    last_updated=timestamp,
                    last_updated_by=user,
                    type=cls.__name__,
                    number_of_approved_members_of_the_committee=number_of_approved_members_of_the_committee
                )

                timestamp += 1
                create_list.append(new_)

        if create_list:
            Meeting.objects.bulk_create(create_list, batch_size=200)

        empties = Meeting.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            Meeting.objects.bulk_update(update_list, batch_size=200)

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Ward No', property_name='ward_number',
                                 ignore=False),
            ExporterColumnConfig(column=2, column_name='Meeting',
                                 property_name='meeting', ignore=False),
            ExporterColumnConfig(column=3, column_name='Which standing committee?',
                                 property_name='standing_committee_name', ignore=False),
            ExporterColumnConfig(column=4, column_name='Date', property_name='meeting_date', ignore=False),
            ExporterColumnConfig(column=5, column_name='Minutes of the meeting (With the meeting title)',
                                 property_name='render_minutes_of_the_meeting', ignore=False),
            ExporterColumnConfig(column=6, column_name='Male',
                                 property_name='number_of_male_participants', ignore=False),
            ExporterColumnConfig(column=7, column_name='Female',
                                 property_name='number_of_female_participants', ignore=False),
            ExporterColumnConfig(column=8, column_name='Disable (Male)',
                                 property_name='number_of_disabled_male_participants', ignore=False),
            ExporterColumnConfig(column=9, column_name='Disable (Female)',
                                 property_name='number_of_disabled_female_participants', ignore=False),
            ExporterColumnConfig(column=10, column_name='Total',
                                 property_name='number_of_total_participants', ignore=False),
            ExporterColumnConfig(column=11, column_name='Number of approved members of the committee',
                                 property_name='number_of_approved_members_of_the_committee', ignore=False),
            ExporterColumnConfig(column=12, column_name='Minutes of the meeting attachment link',
                                 property_name='render_attachment_link', ignore=False),
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        return self.pk, row_number + 1

    @classmethod
    def finalize_export(cls, workbook=None, row_number=None, query_set=None, **kwargs):
        return workbook

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):
        for column in columns:
            workbook.cell(row=1, column=column.column + 1).value = column.column_name

        row_number += 1

        query_params = kwargs.get('query_params')
        _today = date.today()
        target_year = int(query_params.get('year', _today.year))
        city_param = query_params.get('city', None)

        city_ids = None
        if city_param:
            city_ids = [int(x) for x in city_param.split(',')]

        queryset = cls.objects.using(BWDatabaseRouter.get_export_database_name()).all()
        if target_year:
            _from_datetime = datetime(year=target_year, month=1, day=1).timestamp() * 1000
            _to_datetime = datetime(year=target_year + 1, month=1, day=1).timestamp() * 1000 - 1
            queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        if city_ids:
            queryset = queryset.filter(city__id__in=city_ids)

        for cdc in queryset:
            for column in columns:
                column_value = ''
                if hasattr(cdc, column.property_name):
                    column_value = str(getattr(cdc, column.property_name))

                workbook.cell(row=row_number, column=column.column + 1).value = column_value
            row_number += 1

        return workbook, row_number

    @classmethod
    def get_export_dependant_fields(cls):
        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                today = date.today()
                year_choices = tuple()
                for y in range(2000, 2100):
                    year_choices += ((y, str(y)),)

                self.fields['city'] = \
                    GenericModelChoiceField(
                        queryset=Geography.objects.using(
                            BWDatabaseRouter.get_export_database_name()
                        ).filter(level__name='Pourashava/City Corporation'),
                        label='Select City',
                        required=False,
                        widget=forms.Select(
                            attrs={
                                'class': 'select2 kpi-filter',
                                'width': '220',
                                'data-kpi-filter-role': 'city'
                            }
                        )
                    )

                self.fields['year'] = forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )

        return AdvancedExportDependentForm
