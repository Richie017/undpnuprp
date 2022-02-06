from collections import OrderedDict

from django import forms

from undp_nuprp.approvals.forms.settlement_infrastructure_fund.base_settlement_infrastructure_fund_form import \
    BaseSettlementInfrastructureFundForm
from undp_nuprp.approvals.models.infrastructures.sif.sif import SIF


class SifForm(BaseSettlementInfrastructureFundForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SifForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        self.fields['pre_survey_date'] = forms.DateTimeField(
            label='Pre-survey date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.pre_survey_date if instance and instance.pk else None
        )
        self.fields['community_proposal_submitted_to_PIC_date'] = forms.DateTimeField(
            label='Community proposal submitted to PIC (Date)',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.community_proposal_submitted_to_PIC_date if instance and instance.pk else None
        )

        self.fields['pic_approval_date'] = forms.DateTimeField(
            label='PIC Approval Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.pic_approval_date if instance and instance.pk else None
        )
        self.fields['tpb_cpb_approval_date'] = forms.DateTimeField(
            label='TPB/CPB Approval Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.tpb_cpb_approval_date if instance and instance.pk else None
        )
        self.fields['fund_request_date'] = forms.DateTimeField(
            label='Fund request date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.fund_request_date if instance and instance.pk else None
        )
        self.fields['fund_received_by_city_corporation_municipalities_date'] = forms.DateTimeField(
            label='Fund received by city corporation/municipalities (date)',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.fund_received_by_city_corporation_municipalities_date if instance and instance.pk else None
        )
        self.fields['fund_transfer_to_cdc'] = forms.DateTimeField(
            label='Fund transfer to CDC (Date)',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.fund_transfer_to_cdc if instance and instance.pk else None
        )

    class Meta(BaseSettlementInfrastructureFundForm.Meta):
        model = SIF
        fields = ('contract_with_cdc_or_cluster', 'cdc_or_cluster_name', 'cdc_or_cluster_id', 'contract_number',
                  'value_of_contract', 'total_number_of_installment', 'contract_approval_date', 'pre_survey_date',
                  'community_proposal_submitted_to_PIC_date', 'pic_approval_date', 'tpb_cpb_approval_date',
                  'fund_request_date', 'fund_received_by_city_corporation_municipalities_date',
                  'fund_transfer_to_cdc', 'contract_year', 'contract_completion_status', 'contract_completion_date'
                  )
        widgets = {
            'contract_number': forms.NumberInput()
        }

        render_tab = True
        tabs = OrderedDict([
            ('Basic information about the contract',
             ['contract_with_cdc_or_cluster', 'cdc_or_cluster_name', 'cdc_or_cluster_id', 'contract_number',
              'value_of_contract', 'total_number_of_installment', 'contract_approval_date', 'pre_survey_date',
              'community_proposal_submitted_to_PIC_date', 'pic_approval_date', 'tpb_cpb_approval_date',
              'contract_year', 'contract_completion_status', 'contract_completion_date' ]),
            ('Interventions', ['interventions']),
            ('Instalments', ['fund_request_date', 'fund_received_by_city_corporation_municipalities_date',
                             'fund_transfer_to_cdc', 'installments'])
        ])
