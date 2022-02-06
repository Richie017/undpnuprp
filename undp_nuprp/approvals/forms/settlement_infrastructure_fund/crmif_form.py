from collections import OrderedDict

from django import forms

from undp_nuprp.approvals.forms.settlement_infrastructure_fund.base_settlement_infrastructure_fund_form import \
    BaseSettlementInfrastructureFundForm
from undp_nuprp.approvals.models.infrastructures.crmif.crmif import CRMIF


class CRMIFForm(BaseSettlementInfrastructureFundForm):
    class Meta(BaseSettlementInfrastructureFundForm.Meta):
        model = CRMIF
        fields = ('contract_with_cdc_or_cluster', 'cdc_or_cluster_name', 'cdc_or_cluster_id', 'contract_number',
                  'value_of_contract', 'total_number_of_installment', 'contract_approval_date', 'contract_year',
                  'contract_completion_status', 'contract_completion_date')
        widgets = {
            'contract_number': forms.NumberInput()
        }

        render_tab = True
        tabs = OrderedDict([
            ('Basic information about the contract',
             ['contract_with_cdc_or_cluster', 'cdc_or_cluster_name', 'cdc_or_cluster_id', 'contract_number',
              'value_of_contract', 'total_number_of_installment', 'contract_approval_date', 'contract_year',
              'contract_completion_status', 'contract_completion_date']),
            ('Interventions', ['interventions']),
            ('Instalments', ['installments'])
        ])
