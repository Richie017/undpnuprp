from collections import OrderedDict

from django import forms
from django.db import models
from django.forms import Form
from datetime import datetime, date
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.approvals.models import SEFGrantee
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models import Geography,ExporterConfig, ExporterColumnConfig, ErrorLog
from undp_nuprp.approvals.models import WordPrioritizationIndicator

from undp_nuprp.reports.models import PGMemberInfoCache
from undp_nuprp.reports.models import SEFGranteesInfoCache
from undp_nuprp.reports.utils.thousand_separator import thousand_separator
import math
from django.db.models import Sum, F
from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When
from django.db.models.fields import IntegerField
from django.db.models.query_utils import Q
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models import CDCCluster, CDC
from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
__author__ = 'Md Shaheen Alam'

@decorate(is_object_context,
          route(route='grantees-by-wpi', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                display_name='Grantees by Ward Prioritization Index', group_order=3, item_order=26,extra_total_grantees='render_total_grantees'))

class GranteesByWPI(OrganizationDomainEntity):
    class Meta:
        app_label = 'approvals'

    city = models.CharField(null=True, blank=True, max_length=20)
    city_id = models.CharField(null=True, blank=True, max_length=20)
    ward = models.CharField(null=True, blank=True, max_length=20)
    ward_poverty_index = models.CharField(null=True, blank=True, max_length=20)
    total_population = models.CharField(null=True, blank=True, max_length=20)
    total_pg_registration = models.CharField(null=True, blank=True, max_length=20)
    average_mpi_ward_wise = models.CharField(null=True, blank=True, max_length=20)
    sef_grantees = models.CharField(null=True, blank=True, max_length=20)
    nutrition_grantees = models.CharField(null=True, blank=True, max_length=20)
    sif_grantees = models.CharField(null=True, blank=True, max_length=20)
    crmif_grantees = models.CharField(null=True, blank=True, max_length=20)
    total_grantee = models.CharField(null=True, blank=True, max_length=20)
    total_grantee_int = models.IntegerField(null=True, blank=True, max_length=20)
    total_family_member_benefited = models.CharField(null=True, blank=True, max_length=20)
    total_family_member_benefited_int = models.IntegerField(null=True, blank=True, max_length=20)

    @classmethod
    def table_columns(cls):
        return (
            "city", "ward", "ward_poverty_index:Ward Poverty Index", "total_population:Total Population", "total_pg_registration:Total PG Registration",
            "average_mpi_ward_wise:Average MPI by Ward", "sef_grantees:SEF Grantees", "nutrition_grantees:Nutrition Grantees",
            "sif_grantees:SIF Grantees", "crmif_grantees:CRMIF Grantees",
            "total_grantee:Total Grantees", "total_family_member_benefited_int:Total Family Member Benefited"
        )
    @classmethod
    def default_order_by(cls):
        return '-total_grantee'
        
    @classmethod
    def render_total_grantees(cls):
        return '1000'
    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedExport, ViewActionEnum.Delete]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Ward No', property_name='ward', ignore=False),
            ExporterColumnConfig(column=2, column_name='Ward Poverty Index',
                                 property_name='ward_poverty_index', ignore=False),
            ExporterColumnConfig(column=3, column_name='Total Population', property_name='total_population', ignore=False),
            ExporterColumnConfig(column=4, column_name='Total PG Registration', property_name='total_pg_registration', ignore=False),
            ExporterColumnConfig(column=5, column_name='Average MPI ward wise', property_name='average_mpi_ward_wise',
                                 ignore=False),
            ExporterColumnConfig(column=6, column_name='SEF Grantees',
                                 property_name='sef_grantees', ignore=False),
            ExporterColumnConfig(column=7, column_name='Nutrition Grantees',
                                 property_name='nutrition_grantees', ignore=False),
            ExporterColumnConfig(column=8, column_name='SIF Grantees', property_name='sif_grantees', ignore=False),
            ExporterColumnConfig(column=9, column_name='CRMIF Grantees',
                                 property_name='crmif_grantees', ignore=False),
            ExporterColumnConfig(column=10, column_name='Total Grantee',
                                 property_name='total_grantee', ignore=False),
            ExporterColumnConfig(column=11, column_name='Total Family Member Benefited',
                                 property_name='total_family_member_benefited', ignore=False),
            
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
        # target_year = int(query_params.get('year', _today.year))
        city_param = query_params.get('city', None)

        city_ids = None
        if city_param:
            city_ids = [int(x) for x in city_param.split(',')]
        # print(city_param)    
        queryset = cls.objects.using(BWDatabaseRouter.get_export_database_name()).all()
        # if target_year:
        #     _from_datetime = datetime(year=target_year, month=1, day=1).timestamp() * 1000
        #     _to_datetime = datetime(year=target_year + 1, month=1, day=1).timestamp() * 1000 - 1
        #     queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        if city_ids:
            queryset = queryset.filter(city_id=city_param)

        for cdc in queryset:
            for column in columns:
                column_value = ''
                if hasattr(cdc, column.property_name):
                    if column.property_name in ['cdc', 'cluster']:
                        column_value = getattr(cdc, column.property_name)
                        column_value = column_value.name if column_value else ''
                    else:
                        column_value = str(getattr(cdc, column.property_name))

                workbook.cell(row=row_number, column=column.column + 1).value = column_value
            row_number += 1

        return workbook, row_number

    @classmethod
    def get_export_dependant_fields(cls):
        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                # today = date.today()
                # year_choices = tuple()
                # for y in range(2000, 2100):
                #     year_choices += ((y, str(y)),)

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

                # self.fields['year'] = forms.ChoiceField(
                #     choices=year_choices,
                #     widget=forms.Select(
                #         attrs={'class': 'select2', 'width': '220'}
                #     ), initial=today.year
                # )

        return AdvancedExportDependentForm        