import uuid
from datetime import date, datetime

from crequest.middleware import CrequestMiddleware
from django import forms
from django.db import models
from django.forms import Form

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


@decorate(is_object_context, route(route='urban-governance-and-planning', group='Planning and Urban Governance',
                                   module=ModuleEnum.Analysis, display_name='Planning and Urban Governance',
                                   group_order=1, item_order=1), enable_import, enable_export)
class UrbanGovernanceAndPlanning(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True, on_delete=models.SET_NULL)
    ward_committee_ward_no = models.CharField(max_length=20, null=True, blank=True)
    ward_committee_established = models.CharField(max_length=3, null=True, blank=True)
    ward_committee_functional = models.CharField(max_length=3, null=True, blank=True)

    drafted = models.CharField(max_length=3, null=True, blank=True)
    finalized = models.CharField(max_length=3, null=True, blank=True)
    approved = models.CharField(max_length=3, null=True, blank=True)

    standing_committee_ward_no = models.CharField(max_length=20, null=True, blank=True)
    standing_committee_established = models.CharField(max_length=3, null=True, blank=True)
    standing_committee_functional = models.CharField(max_length=3, null=True, blank=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def table_columns(cls):
        return ['code', 'city',
                'ward_committee_ward_no', 'ward_committee_established', 'ward_committee_functional',
                'drafted', 'finalized', 'approved',
                'standing_committee_ward_no', 'standing_committee_established', 'standing_committee_functional',
                'created_by', 'date_created', 'last_updated']

    @classmethod
    def details_view_fields(cls):
        return ['detail_title',
                'code>Basic Info', 'city>Basic Info', 'created_by>Basic Info', 'date_created>Basic Info',
                'last_updated_by>Basic Info', 'last_updated>Basic Info',
                'ward_committee_ward_no>Ward Committee', 'ward_committee_established>Ward Committee',
                'ward_committee_functional>Ward Committee',
                'drafted>Institutional Financial Capacity', 'finalized>Institutional Financial Capacity',
                'approved>Institutional Financial Capacity',
                'ward_no>Standing Committee', 'established>Standing Committee', 'functional>Standing Committee']

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedImport,
                ViewActionEnum.AdvancedExport]

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
            ImporterColumnConfig(column=1, column_name='Ward Committee Ward No', property_name='ward_committee_ward_no',
                                 ignore=False),
            ImporterColumnConfig(column=2, column_name='Ward Committee Established?',
                                 property_name='ward_committee_established', ignore=False),
            ImporterColumnConfig(column=3, column_name='Ward Committee Functional?',
                                 property_name='ward_committee_functional', ignore=False),
            ImporterColumnConfig(column=4, column_name='Drafted?', property_name='drafted', ignore=False),
            ImporterColumnConfig(column=5, column_name='Finalized?', property_name='finalized', ignore=False),
            ImporterColumnConfig(column=6, column_name='Approved?', property_name='approved', ignore=False),
            ImporterColumnConfig(column=7, column_name='Standing Committee Established?',
                                 property_name='standing_committee_ward_no', ignore=False),
            ImporterColumnConfig(column=8, column_name='Standing Committee Functional?',
                                 property_name='standing_committee_established', ignore=False),
            ImporterColumnConfig(column=9, column_name='Standing Committee Drafted?',
                                 property_name='standing_committee_functional', ignore=False)
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
            ward_committee_ward_no = str(item['1']).strip()
            ward_committee_established = str(item['2']).strip()
            ward_committee_functional = str(item['3']).strip()
            drafted = str(item['4']).strip()
            finalized = str(item['5']).strip()
            approved = str(item['6']).strip()
            standing_committee_ward_no = str(item['7']).strip()
            standing_committee_established = str(item['8']).strip()
            standing_committee_functional = str(item['9']).strip()

            city_ = Geography.objects.filter(level__name='Pourashava/City Corporation', name__iexact=city)

            if city_.exists():
                new_ = UrbanGovernanceAndPlanning(
                    organization=organization,
                    city=city_.first(),
                    ward_committee_ward_no=ward_committee_ward_no,
                    ward_committee_established=ward_committee_established,
                    ward_committee_functional=ward_committee_functional,
                    drafted=drafted,
                    finalized=finalized,
                    approved=approved,
                    standing_committee_ward_no=standing_committee_ward_no,
                    standing_committee_established=standing_committee_established,
                    standing_committee_functional=standing_committee_functional,
                    date_created=timestamp,
                    created_by=user,
                    tsync_id= uuid.uuid4(),
                    last_updated=timestamp,
                    last_updated_by=user,
                    type=cls.__name__
                )

                timestamp += 1
                create_list.append(new_)

        if create_list:
            UrbanGovernanceAndPlanning.objects.bulk_create(create_list, batch_size=200)

        empties = UrbanGovernanceAndPlanning.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            UrbanGovernanceAndPlanning.objects.bulk_update(update_list, batch_size=200)

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Ward Committee Ward No', property_name='ward_committee_ward_no',
                                 ignore=False),
            ExporterColumnConfig(column=2, column_name='Ward Committee Established?',
                                 property_name='ward_committee_established', ignore=False),
            ExporterColumnConfig(column=3, column_name='Ward Committee Functional?',
                                 property_name='ward_committee_functional', ignore=False),
            ExporterColumnConfig(column=4, column_name='Drafted?', property_name='drafted', ignore=False),
            ExporterColumnConfig(column=5, column_name='Finalized?', property_name='finalized', ignore=False),
            ExporterColumnConfig(column=6, column_name='Approved?', property_name='approved', ignore=False),
            ExporterColumnConfig(column=7, column_name='Standing Committee Established?',
                                 property_name='standing_committee_ward_no', ignore=False),
            ExporterColumnConfig(column=8, column_name='Standing Committee Functional?',
                                 property_name='standing_committee_established', ignore=False),
            ExporterColumnConfig(column=9, column_name='Standing Committee Drafted?',
                                 property_name='standing_committee_functional', ignore=False)
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
