import uuid
from datetime import date, datetime

from crequest.middleware import CrequestMiddleware
from django import forms
from django.db import models
from django.forms import Form
from django.utils.safestring import mark_safe

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography, ImporterConfig, ImporterColumnConfig, ExporterConfig, ExporterColumnConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter


@decorate(is_object_context, route(route='land-tenure-action-plan', group='Housing Finance',
                                   module=ModuleEnum.Analysis, display_name='Land Tenure Action Plan',
                                   group_order=4, item_order=4), enable_import, enable_export)
class LandTenureActionPlan(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True)
    land_tenure_action_plan_required = models.CharField(max_length=3, null=True, blank=True)
    started = models.CharField(max_length=3, null=True, blank=True)
    developed = models.CharField(max_length=3, null=True, blank=True)
    implemented = models.CharField(max_length=3, null=True, blank=True)

    @property
    def detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_city(self):
        return self.city.name if self.city else 'N/A'

    @classmethod
    def details_view_fields(cls):
        return 'detail_title', 'code', 'render_city', 'land_tenure_action_plan_required', 'started', \
               'developed', 'implemented', 'created_by', 'date_created', 'last_updated:Last Updated On'

    @classmethod
    def table_columns(cls):
        return ['code', 'render_city', 'land_tenure_action_plan_required', 'started',
                'developed', 'implemented', 'created_by', 'date_created', 'last_updated:Last Updated On']

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
            ImporterColumnConfig(column=1, column_name='Land tenure action plan required',
                                 property_name='land_tenure_action_plan_required', ignore=False),
            ImporterColumnConfig(column=2, column_name='Started', property_name='started', ignore=False),
            ImporterColumnConfig(column=3, column_name='Developed', property_name='developed', ignore=False),
            ImporterColumnConfig(column=4, column_name='Implemented', property_name='implemented', ignore=False)
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
            item2 = str(item['1']).strip() if item['1'] else None
            item3 = str(item['2']).strip() if item['2'] else None
            item4 = str(item['3']).strip() if item['3'] else None
            item5 = str(item['4']).strip() if item['4'] else None

            city_ = Geography.objects.filter(level__name='Pourashava/City Corporation', name__iexact=city)

            if city_.exists():
                new_ = LandTenureActionPlan(
                    organization=organization,
                    city=city_.first(),
                    land_tenure_action_plan_required=item2,
                    started=item3,
                    developed=item4,
                    implemented=item5,
                    date_created=timestamp,
                    created_by=user,
                    tsync_id=uuid.uuid4(),
                    last_updated=timestamp,
                    last_updated_by=user,
                    type=cls.__name__
                )

                timestamp += 1
                create_list.append(new_)

        if create_list:
            LandTenureActionPlan.objects.bulk_create(create_list, batch_size=200)

        empties = LandTenureActionPlan.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            LandTenureActionPlan.objects.bulk_update(update_list, batch_size=200)

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Land tenure action plan required',
                                 property_name='land_tenure_action_plan_required', ignore=False),
            ExporterColumnConfig(column=2, column_name='Started', property_name='started', ignore=False),
            ExporterColumnConfig(column=3, column_name='Developed', property_name='developed', ignore=False),
            ExporterColumnConfig(column=4, column_name='Implemented', property_name='implemented', ignore=False)
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
