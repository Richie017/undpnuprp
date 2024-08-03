from collections import OrderedDict

from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route, partial_route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models import CDC

__author__ = 'Mahbub'


@decorate(is_object_context,
          route(route='operation-and-maintenance', group='Infrastructure & Urban Services', module=ModuleEnum.Analysis,
                display_name='Operation and Maintenance Fund', group_order=5, item_order=3))
class OperationAndMaintenanceFund(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)
    contract_number = models.CharField(max_length=128, blank=True)
    cdc_id = models.CharField(max_length=128, blank=True)
    assigned_cdc = models.ForeignKey(CDC, null=True, on_delete=models.SET_NULL)
    value_of_contract = models.IntegerField(default=0, blank=True, null=True)
    contract_start_date = models.DateField(default=None, null=True)
    combined_construction_value = models.IntegerField(default=0, blank=True, null=True)
    expected_om_fund_value = models.IntegerField(default=0, blank=True, null=True)
    collected_om_fund_value = models.IntegerField(default=0, blank=True, null=True)
    om_fund_balance = models.IntegerField(default=0, blank=True, null=True)

    principal_fund = models.IntegerField(default=0, blank=True, null=True)
    interest = models.IntegerField(default=0, blank=True, null=True)
    total_fund = models.IntegerField(default=0, blank=True, null=True)

    savings_account = models.CharField(max_length=128, blank=True)
    deposit_account = models.CharField(max_length=128, blank=True)
    chdf = models.CharField(max_length=128, blank=True)
    other_account = models.CharField(max_length=128, blank=True)

    money_withdrawn_tubewells = models.IntegerField(default=0, blank=True, null=True)
    money_withdrawn_latrines = models.IntegerField(default=0, blank=True, null=True)
    money_withdrawn_bathrooms = models.IntegerField(default=0, blank=True, null=True)

    project_count_tubewells = models.IntegerField(default=0, blank=True, null=True)
    project_count_latrines = models.IntegerField(default=0, blank=True, null=True)
    project_count_bathrooms = models.IntegerField(default=0, blank=True, null=True)

    project_bank_charge = models.IntegerField(default=0, blank=True, null=True)
    project_total_charge = models.IntegerField(default=0, blank=True, null=True)

    repaired_tubewells = models.IntegerField(default=0, blank=True, null=True)
    repaired_latrines = models.IntegerField(default=0, blank=True, null=True)
    repaired_bathrooms = models.IntegerField(default=0, blank=True, null=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"

    @classmethod
    def table_columns(cls):
        return 'code', 'city', 'created_by', 'last_updated'

    @property
    def details_config(self):
        d = OrderedDict()
        basic_info = OrderedDict()
        basic_info['city'] = self.city.name if self.city else 'N/A'
        basic_info['contract_number'] = self.contract_number
        basic_info['CDC Name'] = self.assigned_cdc.name if self.assigned_cdc else 'N/A'
        basic_info['CDC ID'] = self.cdc_id
        basic_info['Contract start date'] = self.contract_start_date
        basic_info['Total contract value'] = self.value_of_contract
        basic_info[
            'Construction value for all tubewells, latrines and bathrooms combined in the contract'] = self.combined_construction_value
        basic_info['For each contract expected O&M fund value'] = self.expected_om_fund_value
        basic_info['For each contract how much O&M fund has been collected'] = self.collected_om_fund_value
        basic_info['NUPPR O&M fund balance'] = self.om_fund_balance

        d['Basic Information'] = basic_info

        cdc_om_fund = OrderedDict()
        cdc_om_fund['Principal'] = self.principal_fund
        cdc_om_fund['Interest/Profit'] = self.interest
        cdc_om_fund['Total'] = self.total_fund

        d['Value of CDC O&M fund (BDT)'] = cdc_om_fund

        allocated_om_fund = OrderedDict()
        allocated_om_fund['Savings account'] = self.savings_account
        allocated_om_fund['Fixed term deposit account'] = self.deposit_account
        allocated_om_fund['CHDF'] = self.chdf
        allocated_om_fund['Other'] = self.other_account

        d['Allocated/Invested O&M fund'] = allocated_om_fund

        money_withdrawn = OrderedDict()
        money_withdrawn['Tubewells'] = self.money_withdrawn_tubewells
        money_withdrawn['Latrines'] = self.money_withdrawn_latrines
        money_withdrawn['Bathrooms'] = self.money_withdrawn_bathrooms

        d['Value of money withdrawn/deducted'] = money_withdrawn

        project_count = OrderedDict()
        project_count['Tubewells'] = self.project_count_tubewells
        project_count['Latrines'] = self.project_count_latrines
        project_count['Bathrooms'] = self.project_count_bathrooms
        project_count['Bank charges'] = self.project_bank_charge
        project_count['Total (BDT)'] = self.project_total_charge

        d['Number of projects'] = project_count

        repair_fund = OrderedDict()
        repair_fund['Tubewells'] = self.repaired_tubewells
        repair_fund['Latrines'] = self.repaired_latrines
        repair_fund['Bathrooms'] = self.repaired_bathrooms

        d['Cumulative no. of infrastructures repaired using O&M fund (repairs completed)'] = repair_fund

        return d

    @classmethod
    def export_file_columns(cls):
        return [
            'city', 'contract_number', 'assigned_cdc', 'cdc_id', 'contract_start_date', 'value_of_contract',
            'combined_construction_value', 'expected_om_fund_value', 'collected_om_fund_value',
            'om_fund_balance', 'principal_fund', 'interest', 'total_fund', 'savings_account',
            'deposit_account', 'chdf', 'other_account', 'money_withdrawn_tubewells', 'money_withdrawn_latrines',
            'money_withdrawn_bathrooms', 'project_count_tubewells', 'project_count_latrines',
            'project_count_bathrooms', 'project_bank_charge', 'project_total_charge',
            'repaired_tubewells', 'repaired_latrines', 'repaired_bathrooms'
        ]

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedExport
        ]
