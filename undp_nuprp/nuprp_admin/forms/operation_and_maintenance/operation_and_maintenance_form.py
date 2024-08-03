from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models import CDC


from undp_nuprp.nuprp_admin.models.operation_and_maintenance.operation_and_maintenance import \
    OperationAndMaintenanceFund

__author__ = "Mahbub"


class OperationAndMaintenanceFundForm(GenericFormMixin):

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(OperationAndMaintenanceFundForm, self).__init__(data=data, files=files, instance=instance,
                                                             prefix=prefix, **kwargs)
        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['assigned_cdc'] = GenericModelChoiceField(
            required=False,
            queryset=CDC.objects.all().order_by('name'), label='CDC Name',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['contract_start_date'] = forms.DateTimeField(
            label='Contract start date',
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
        )

    @classmethod
    def get_template(cls):
        return 'large_labelled_form/large_labelled_form.html'

    class Meta(GenericFormMixin.Meta):
        model = OperationAndMaintenanceFund
        fields = ('city', 'contract_number', 'assigned_cdc', 'cdc_id', 'contract_start_date', 'value_of_contract',
                  'combined_construction_value', 'expected_om_fund_value', 'collected_om_fund_value',
                  'om_fund_balance', 'principal_fund', 'interest', 'total_fund', 'savings_account',
                  'deposit_account', 'chdf', 'other_account', 'money_withdrawn_tubewells', 'money_withdrawn_latrines',
                  'money_withdrawn_bathrooms', 'project_count_tubewells', 'project_count_latrines',
                  'project_count_bathrooms', 'project_bank_charge', 'project_total_charge',
                  'repaired_tubewells', 'repaired_latrines', 'repaired_bathrooms')

        labels = {

            'cdc_id': 'CDC ID',
            'value_of_contract': 'Total contract value',
            'combined_construction_value': 'Construction value for all tubewells, latrines and bathrooms combined in the contract',
            'expected_om_fund_value': 'For each contract expected O&M fund value (This should be 10% of previous input)',
            'collected_om_fund_value': 'For each contract how much O&M fund has been collected',
            'om_fund_balance': 'NUPPR O&M fund balance',
            'principal_fund': 'Principal',
            'interest': 'Interest/Profit',
            'total_fund': 'Total',
            'deposit_account': 'Fixed term deposit account',
            'chdf': 'CHDF',
            'other_account': 'Other',
            'money_withdrawn_tubewells': 'Tubewells',
            'money_withdrawn_latrines': 'Latrines',
            'money_withdrawn_bathrooms': 'Bathrooms',
            'project_count_tubewells': 'Tubewells',
            'project_count_latrines': 'Latrines',
            'project_count_bathrooms': 'Bathrooms',
            'project_bank_charge': 'Bank charges',
            'project_total_charge': 'Total (BDT)',
            'repaired_tubewells': 'Tubewells',
            'repaired_latrines': 'Latrines',
            'repaired_bathrooms': 'Bathrooms'
        }

    @classmethod
    def field_groups(cls):
        _group = super(OperationAndMaintenanceFundForm, cls).field_groups()
        _group['Basic Information'] = \
            ['city', 'contract_number', 'assigned_cdc', 'cdc_id', 'contract_start_date', 'value_of_contract',
             'combined_construction_value', 'expected_om_fund_value', 'collected_om_fund_value',
             'om_fund_balance']

        _group['Value of CDC O&M fund (BDT)'] = ['principal_fund', 'interest', 'total_fund']

        _group['Allocated/Invested O&M fund'] = ['savings_account', 'deposit_account', 'chdf', 'other_account']

        _group['Value of money withdrawn/deducted for O&M purposes and number of projects'] = []

        _group['Value of money withdrawn/deducted'] = ['money_withdrawn_tubewells', 'money_withdrawn_latrines',
                                                       'money_withdrawn_bathrooms']
        _group['Number of projects'] = ['project_count_tubewells', 'project_count_latrines', 'project_count_bathrooms',
                                        'project_bank_charge', 'project_total_charge']
        _group['Cumulative no. of infrastructures repaired using O&M fund (repairs completed)'] = ['repaired_tubewells',
                                                                                                   'repaired_latrines',
                                                                                                   'repaired_bathrooms']

        return _group
