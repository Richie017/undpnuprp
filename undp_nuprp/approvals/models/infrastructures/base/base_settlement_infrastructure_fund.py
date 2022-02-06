import re
from collections import OrderedDict

from django.db import models
from django.forms import Form
from django import forms
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField

from django.db.models.aggregates import Count, Max, Sum
from django.db.models.query_utils import Q
from django.utils.safestring import mark_safe

from blackwidow.core.models import Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from blackwidow.engine.templatetags.blackwidow_filter import SITE_ROOT
from undp_nuprp.approvals.models.infrastructures.base.completed_contract import CompletedContract
from undp_nuprp.approvals.models.infrastructures.base.installment import SIFInstallment
from undp_nuprp.approvals.models.infrastructures.base.intervention import Intervention
from undp_nuprp.approvals.models.infrastructures.base.sanitary_intervention import \
    SanitaryIntervention
from undp_nuprp.approvals.models.infrastructures.base.water_intervention import \
    WaterIntervention
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster
from datetime import date, datetime


__author__ = 'Shuvro, sayad'


class BaseSettlementInfrastructureFund(OrganizationDomainEntity):
    contract_with_cdc_or_cluster = models.CharField(max_length=128, blank=True, null=True)
    cdc_or_cluster_name = models.CharField(max_length=128, blank=True, null=True)
    cdc_or_cluster_id = models.CharField(max_length=128, blank=True, null=True)
    assigned_cdc_cluster = models.ForeignKey(CDCCluster, null=True, on_delete=models.SET_NULL, related_name='+')
    assigned_cdc = models.ForeignKey(CDC, null=True, on_delete=models.SET_NULL, related_name='+')
    assigned_city = models.CharField(max_length=128, blank=True, null=True)
    contract_number = models.CharField(max_length=128, blank=True, null=True)
    value_of_contract = models.IntegerField(null=True)
    contract_approval_date = models.DateField(default=None, null=True)
    contract_year = models.CharField(max_length=4, null=True)
    contract_completion_status = models.CharField(max_length=20, blank=True, null=True)
    contract_completion_date = models.DateField(default=None, null=True)
    pre_survey_date = models.DateField(default=None, null=True)
    community_proposal_submitted_to_PIC_date = models.DateField(default=None, null=True)
    pic_approval_date = models.DateField(default=None, null=True)
    tpb_cpb_approval_date = models.DateField(default=None, null=True)
    total_number_of_installment = models.IntegerField(null=True)
    interventions = models.ManyToManyField(Intervention)
    installments = models.ManyToManyField(SIFInstallment)
    fund_request_date = models.DateField(default=None, null=True)
    fund_received_by_city_corporation_municipalities_date = models.DateField(default=None, null=True)
    fund_transfer_to_cdc = models.DateField(default=None, null=True)

    class Meta:
        app_label = 'approvals'
        abstract = True

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_value_of_instalments_made(self):
        total_instalment = self.installments.aggregate(total=Sum('installment_value'))
        return total_instalment['total'] if total_instalment['total'] else 'N/A'

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title

        # basic information
        basic_info = OrderedDict()
        basic_info['Contract with CDC or Cluster or Federation'] = self.contract_with_cdc_or_cluster
        basic_info['Name'] = self.cdc_or_cluster_name
        basic_info['ID'] = self.cdc_or_cluster_id
        basic_info['Contract number'] = self.contract_number
        basic_info['Value of contract (Taka)'] = self.value_of_contract
        basic_info['Total number of instalments'] = self.total_number_of_installment
        basic_info['Contract approval date'] = self.contract_approval_date
        basic_info['Contract year'] = self.contract_year
        basic_info['Contract Completion Status'] = self.contract_completion_status
        basic_info['Contract Completion Date'] = self.contract_completion_date
        basic_info['Pre-survey date'] = self.pre_survey_date
        basic_info['Community proposal submitted to PIC (Date)'] = self.community_proposal_submitted_to_PIC_date
        basic_info['PIC Approval Date'] = self.pic_approval_date
        basic_info['TPB/CPB Approval Date'] = self.tpb_cpb_approval_date
        Instalment_info = OrderedDict()
        Instalment_info['Fund request date'] = self.fund_request_date
        Instalment_info['Fund received by city corporation/municipalities (date)'] = self.fund_received_by_city_corporation_municipalities_date
        Instalment_info['Fund transfer to CDC (Date)'] = self.fund_transfer_to_cdc

        details['Basic information about the contract'] = basic_info
        details['Basic information about the Fund'] = Instalment_info

        return details

    @classmethod
    def tab_configs_info(cls):
        tab_configs_info = OrderedDict()

        tab_configs_info['water_interventions'] = dict(
            title='Water Intervention(s)',
            access_key='water_interventions',
            related_model=WaterIntervention,
            property='self.water_interventions',
            max_number_of_instance=cls.objects.annotate(num_of_instances=Count('water_interventions')).aggregate(
                Max('num_of_instances'))['num_of_instances__max']
        )

        tab_configs_info['sanitary_interventions'] = dict(
            title='Sanitary Intervention(s)',
            access_key='sanitary_interventions',
            related_model=SanitaryIntervention,
            property='self.sanitary_interventions',
            max_number_of_instance=cls.objects.annotate(num_of_instances=Count('sanitary_interventions')).aggregate(
                Max('num_of_instances'))['num_of_instances__max']
        )

        tab_configs_info['installments'] = dict(
            title='Installment(s)',
            access_key='installments',
            related_model=SIFInstallment,
            property='self.installments',
            max_number_of_instance=cls.objects.annotate(num_of_instances=Count('installments')).aggregate(
                Max('num_of_instances'))['num_of_instances__max']
        )

        return tab_configs_info

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Instalment(s)',
                access_key='instalments',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=SIFInstallment,
                property=self.installments,
            ),
            TabView(
                title='Intervention(s)',
                access_key='interventions',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=Intervention,
                property=self.interventions,
            ),
            TabView(
                title='Water Intervention(s)',
                access_key='water_interventions',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model=WaterIntervention,
                queryset_filter=Q(**{'intervention__in': self.interventions.all()})
            ),
            TabView(
                title='Sanitary Intervention(s)',
                access_key='sanitary_interventions',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model=SanitaryIntervention,
                queryset_filter=Q(**{'intervention__in': self.interventions.all()})
            ),
            TabView(
                title='Completed Contract(s)',
                access_key='completed_contracts',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model=CompletedContract,
                queryset_filter=Q(**{'intervention__in': self.interventions.all()})
            )
        ]

    @classmethod
    def table_columns(cls):
        return 'code', 'contract_with_cdc_or_cluster: Contract with CDC or Cluster or Federation', \
               'cdc_or_cluster_name:Name', \
               'cdc_or_cluster_id:ID', 'contract_number', 'assigned_city:City corporation', 'value_of_contract', \
               'total_number_of_installment:Total number of instalments', 'render_value_of_instalments_made', \
               'date_created:Created On', "last_updated:Last Updated On"

    @classmethod
    def export_file_columns(cls):
        """
        this method is used to get the list of columns to be exported
        :return: a list of column properties
        """
        return [
            'assigned_city:City corporation',
            'contract_with_cdc_or_cluster: Contract with CDC or Cluster or Federation',
            'cdc_or_cluster_name:Name', 'cdc_or_cluster_id:ID', 'contract_number', 'value_of_contract',
            'contract_approval_date', 'contract_year', 'contract_completion_status', 'contract_completion_date',
            'pre_survey_date:Pre-survey date',
            'community_proposal_submitted_to_PIC_date:Community proposal submitted to PIC (Date)',
            'pic_approval_date:PIC Approval Date', 'tpb_cpb_approval_date:TPB/CPB Approval Date',
            'fund_request_date',
            'fund_received_by_city_corporation_municipalities_date:Fund received by city corporation/municipalities (date)',
            'fund_transfer_to_cdc:Fund transfer to CDC (Date)'

        ]

    @classmethod
    def get_export_order_by(cls):
        return '-last_updated'

    @classmethod
    def apply_search_filter(cls, search_params=None, queryset=None, **kwargs):
        queryset = super(BaseSettlementInfrastructureFund, cls).apply_search_filter(search_params=search_params, queryset=queryset, **kwargs)

        if search_params.get('city', None):
            try:
                city_param = search_params.get('city')
                city_name = Geography.objects.get(id=city_param).name
                queryset = queryset.filter(assigned_city=city_name)
                # print(city_name)
                # print(len(queryset))
            except Exception as exc:
                print(exc)

        if search_params.get('year', None):
            target_year = int(search_params.get('year'))
            _from_datetime = datetime(year=target_year, month=1, day=1, hour=1, minute=0, second=0).timestamp() * 1000
            _to_datetime = datetime(year=target_year + 1, month=1, day=1, hour=23, minute=59, second=59).timestamp() * 1000
            queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        return queryset

    def export_row_item(self, index, workbook=None, row_number=None, items=None, **kwargs):
        """
        prepare individual row for the excel file
        :param workbook: the workbook instance to work on
        :param row_number: number of current row of cursor position
        :param items: items of the tow to be write in workbook
        :return:
        """
        column_no = 1
        for item in items:
            if index > 1 and column_no == 6: # value_of_contract
                workbook.cell(row=row_number, column=column_no).value = ""
            else:
                workbook.cell(row=row_number, column=column_no).value = str(item)
            column_no += 1

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        """
        prepare individual row for the excel file
        :param workbook: the workbook instance to work on
        :param columns: exported column configs
        :param row_number: number of current row of cursor position
        :return: tuple (pk, row_number): pk of the current item, and the updated cursor position as row
        """
        items = []
        for column in columns:
            _value = getattr(self, column.property_name, '')

            if column.property_name in self.__class__.get_datetime_fields():
                _value = self.render_timestamp(_value)

            if _value:
                url_search = re.search('<a(.+?)href=(.+?)>(.+?)</a>', str(_value))
                if url_search:
                    _value = url_search.group(3)
                    _url = url_search.group(2).replace('"', '').replace("'", '')
            else:
                _value = ''
            items.append(str(_value))

        for _index, _intervention in enumerate(
                self.interventions.using(BWDatabaseRouter.get_export_database_name()).all(), 1):
            _water_intervention = _intervention.water_interventions.using(
                BWDatabaseRouter.get_export_database_name()
            ).last()
            _water_intervention_items = _water_intervention.export_file_column_items() \
                if _water_intervention else [''] * len(WaterIntervention.export_file_columns_title())

            _sanitary_intervention = _intervention.sanitary_interventions.using(
                BWDatabaseRouter.get_export_database_name()
            ).last()
            _sanitary_intervention_items = _sanitary_intervention.export_file_column_items() \
                if _sanitary_intervention else [''] * len(SanitaryIntervention.export_file_columns_title())

            _completed_contract_items = _intervention.completed_contract.export_file_column_items()

            _items = items + _intervention.export_file_column_items() + _water_intervention_items + \
                     _sanitary_intervention_items + _completed_contract_items + \
                     self.instalments_export_column_values(index=_index)

            self.export_row_item(index=_index, workbook=workbook, row_number=row_number, items=_items)
            row_number += 1

        return self.pk, row_number

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):
        """
        this method is used to format the excel file at the beginning of the export
        :param workbook: the workbook instance to work on
        :param columns: exported column configs
        :param row_number: beginning row at which the cursor is on
        :param query_set: the queryset for exportable objects
        :param kwargs: extra params
        :return: tuple of (workbook, row_number): these are updated workbook and row_number after the initiatialization
        """
        column = 1
        for c in columns:
            workbook.cell(row=row_number, column=column).value = c.column_name
            column += 1

        tab_columns = list(
            Intervention.export_file_columns_title() +
            WaterIntervention.export_file_columns_title() +
            SanitaryIntervention.export_file_columns_title() +
            CompletedContract.export_file_columns_title() +
            cls.instalments_export_column_titles())

        for _col_name in tab_columns:
            workbook.cell(row=row_number, column=column).value = bw_titleize(_col_name)
            column += 1

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

    def instalments_export_column_values(self, index):
        instalment_column_values = self.installments.values_list(
            'installment_value', 'installment_date',
            'status_of_physical_progress',
            'status_of_financial_progress'
        )
        if index > 1:
            instalments_values = ['', '']
        else:
            instalments_values = [self.total_number_of_installment, self.render_value_of_instalments_made]
        for instalment_column_value in instalment_column_values:
            _value, _date, _status_of_physical_progress, _status_of_financial_progress = instalment_column_value
            if index > 1:
                instalments_values.append('')
                instalments_values.append('')
                instalments_values.append('')
                instalments_values.append('')
            else:
                instalments_values.append(_value if _value else '')
                instalments_values.append(_date if _date else '')
                instalments_values.append(_status_of_physical_progress if _status_of_physical_progress else '')
                instalments_values.append(_status_of_financial_progress if _status_of_financial_progress else '')

        return instalments_values

    @classmethod
    def instalments_export_column_titles(cls):
        _instalment_col_header_prefix = ['Total number of instalments', 'Value of instalments made']
        column_name = [
            'Instalment', 'Date of instalment',
            'Status of physical Progress (descriptive)',
            'Status of Financial Progress %'
        ]
        _max_no_installments = cls.objects.using(
            BWDatabaseRouter.get_export_database_name()
        ).annotate(total=Count('installments')).aggregate(Max('total'))['total__max']
        _max_no_installments = _max_no_installments if _max_no_installments else 0
        return _instalment_col_header_prefix + ['{} {}'.format(_col_name, i + 1)
                                                for i in range(_max_no_installments) for _col_name in column_name]
