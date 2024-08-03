from django import forms
from django.forms.models import modelformset_factory

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.engine.exceptions.exceptions import BWException
from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_TYPES
from undp_nuprp.approvals.forms.settlement_infrastructure_fund.installment_form import SIFInstallmentForm
from undp_nuprp.approvals.forms.settlement_infrastructure_fund.intervention_form import InterventionForm
from undp_nuprp.approvals.models.infrastructures.base.installment import SIFInstallment
from undp_nuprp.approvals.models.infrastructures.base.intervention import Intervention
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster
from datetime import date


__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)
CDC_OR_Cluster_Choices = (('', 'Select One'), ('CDC', 'CDC'), ('Cluster', 'Cluster'), ('Federation', 'Federation'))

YEAR_CHOICES = tuple()
YEAR_CHOICES += (('', "Select One"),)
for year in range(2000, 2101):
    YEAR_CHOICES += ((year, str(year)),)

Contract_Completion_Status_Choices = tuple()
Contract_Completion_Status_Choices += (('', "Select One"), ('On-going', 'On-going'),
                                      ('Completed','Completed'), ('Drop-out', 'Drop out'))

installment_formset = modelformset_factory(
    SIFInstallment, form=SIFInstallmentForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

intervention_formset = modelformset_factory(
    Intervention, form=InterventionForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

intervention_type_choices = (('', 'Select One'),)

for intervention_type in INTERVENTION_TYPES:
    intervention_type_choices += ((intervention_type, intervention_type),)


class BaseSettlementInfrastructureFundForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(BaseSettlementInfrastructureFundForm, self).__init__(data=data, files=files, instance=instance,
                                                                   prefix=prefix, **kwargs)
        if instance and instance.pk:
            intervention_objects = instance.interventions.all()
            installment_objects = instance.installments.all()
        else:
            intervention_objects = Intervention.objects.none()
            installment_objects = SIFInstallment.objects.none()

        self.fields['contract_with_cdc_or_cluster'] = forms.ChoiceField(
            label='Contract with CDC or Cluster or Federation',
            choices=CDC_OR_Cluster_Choices,
            required=True,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=self.instance.contract_with_cdc_or_cluster if not self.is_new_instance else None
        )
        self.fields['cdc_or_cluster_name'].label = 'Name'
        self.fields['cdc_or_cluster_name'].required = True
        self.fields['cdc_or_cluster_id'].label = 'ID'
        self.fields['cdc_or_cluster_id'].required = True
        self.fields['contract_number'].label = 'Contract number'
        self.fields['contract_number'].required = True
        self.fields['value_of_contract'].label = 'Value of contract (BDT)'
        self.fields['total_number_of_installment'].label = 'Total number of instalments'
        self.fields['contract_approval_date'] = forms.DateTimeField(
            label='Contract approval date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.contract_approval_date if instance and instance.pk else None
        )

        self.fields['contract_year'] = forms.ChoiceField(
            choices=YEAR_CHOICES, required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=date.today().year
        )

        self.fields['contract_completion_status'] = forms.ChoiceField(
            choices=Contract_Completion_Status_Choices, required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=None
        )

        self.fields['contract_completion_date'] = forms.DateTimeField(
            label='Contract Completion date',
            input_formats=['%d/%m/%Y'], required=False,
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.contract_approval_date if instance and instance.pk else None
        )

        self.add_child_form("interventions", intervention_formset(
            data=data, files=files, queryset=intervention_objects, prefix='interventions', header='Interventions',
            add_more=True, **kwargs
        ))
        self.add_child_form("installments", installment_formset(
            data=data, files=files, queryset=installment_objects, prefix='installments', header='Instalments',
            add_more=True, **kwargs
        ))

    def clean(self):
        cleaned_data = super(BaseSettlementInfrastructureFundForm, self).clean()

        contract_completion_status = cleaned_data['contract_completion_status']
        if contract_completion_status != 'Completed':
            cleaned_data['contract_completion_date'] = None

        if 'cdc_or_cluster_name' and 'cdc_or_cluster_id' in cleaned_data:
            _name = cleaned_data['cdc_or_cluster_name'].strip('\'')
            _id = cleaned_data['cdc_or_cluster_id'].strip('\'')
            if 'contract_with_cdc_or_cluster' in cleaned_data:
                _contract_with = cleaned_data['contract_with_cdc_or_cluster']
                if _contract_with == 'CDC':
                    if not CDC.objects.filter(name=_name, assigned_code=_id).exists():
                        self.add_error('cdc_or_cluster_name', "Name and ID does not match with any CDC")
                        self.add_error('cdc_or_cluster_id', "Name and ID does not match with any CDC")
                        raise BWException("CDC with this name and ID doesn't exists")
                elif _contract_with == 'Cluster':
                    if not CDCCluster.objects.filter(name=_name, assigned_code=_id).exists():
                        self.add_error('cdc_or_cluster_name', "Name and ID does not match with any CDC Cluster")
                        self.add_error('cdc_or_cluster_id', "Name and ID does not match with any CDC Cluster")
                        raise BWException("CDC Cluster with this name and ID doesn't exists")

        return cleaned_data

    def save(self, commit=True):
        super(BaseSettlementInfrastructureFundForm, self).save(commit=True)
        if self.instance.contract_with_cdc_or_cluster == 'CDC':
            _cdc = CDC.objects.filter(name=self.instance.cdc_or_cluster_name,
                                      assigned_code=self.instance.cdc_or_cluster_id).last()
            self.instance.assigned_cdc = _cdc
            self.instance.assigned_cdc_cluster = _cdc.parent
            self.instance.assigned_city = _cdc.render_city_corporation if _cdc else ''
        elif self.instance.contract_with_cdc_or_cluster == 'Cluster':
            _cluster = CDCCluster.objects.filter(name=self.instance.cdc_or_cluster_name,
                                                 assigned_code=self.instance.cdc_or_cluster_id).last()
            self.instance.assigned_cdc_cluster = _cluster
            self.instance.assigned_cdc = None
            self.instance.assigned_city = _cluster.render_city_corporation if _cluster else ''

        self.instance.save()
        return self.instance
