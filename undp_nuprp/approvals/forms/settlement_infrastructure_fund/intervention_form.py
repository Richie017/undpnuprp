from django import forms
from django.db import transaction
from django.forms.models import modelformset_factory

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from undp_nuprp.approvals.config.constants.sif_constants import INTERVENTION_TYPES, WATER_INTERVENTION_TYPES, \
    SANITATION_INTERVENTION_TYPES, MANDATORY_LENGTH_INTERVENTION_TYPES
from undp_nuprp.approvals.forms.settlement_infrastructure_fund.completed_contract_form import CompletedContractForm
from undp_nuprp.approvals.forms.settlement_infrastructure_fund.sanitary_intervation_form import SanitaryInterventionForm
from undp_nuprp.approvals.forms.settlement_infrastructure_fund.water_intervention_form import WaterInterventionForm
from undp_nuprp.approvals.models.infrastructures.base.intervention import Intervention
from undp_nuprp.approvals.models.infrastructures.base.sanitary_intervention import SanitaryIntervention
from undp_nuprp.approvals.models.infrastructures.base.water_intervention import WaterIntervention

__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)
Repair_New_Choices = (('', 'Select One'), ('Repair', 'Repair'), ('New', 'New'),)
intervention_type_choices = (('', 'Select One'),)

water_intervention_formset = modelformset_factory(
    WaterIntervention, form=WaterInterventionForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

sanitary_intervention_formset = modelformset_factory(
    SanitaryIntervention, form=SanitaryInterventionForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)

for intervention_type in INTERVENTION_TYPES:
    intervention_type_choices += ((intervention_type, intervention_type),)


class InterventionForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(InterventionForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        req = kwargs.get('request', None)
        if req:
            path = req.c_request_path
            if 'crmif' not in path:
                self.fields.pop('matching_fund')

        if instance and instance.pk:
            water_intervention_objects = instance.water_interventions.all()
            sanitary_intervention_objects = instance.sanitary_interventions.all()
        else:
            water_intervention_objects = WaterIntervention.objects.none()
            sanitary_intervention_objects = SanitaryIntervention.objects.none()

        self.fields['type_of_intervention'] = forms.ChoiceField(
            label='Type of intervention',
            choices=intervention_type_choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.type_of_intervention if instance and instance.pk else None
        )

        self.fields['intervention_id'].label = 'Intervention ID'
        self.fields['intervention_id'].required = True
        self.fields['length'].label = 'Length (Meter)'
        self.fields['number_of_facilities'].required = False

        self.fields['expected_start_date'] = forms.DateTimeField(
            label='Expected Start Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.expected_start_date if instance and instance.pk else None
        )

        self.fields['expected_end_date'] = forms.DateTimeField(
            label='Expected End Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.expected_end_date if instance and instance.pk else None
        )

        self.fields['type_of_intervention'] = forms.ChoiceField(
            label='Type of intervention',
            choices=intervention_type_choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.type_of_intervention if instance and instance.pk else None
        )

        self.fields['intervention_id'].label = 'Intervention ID'
        self.fields['intervention_id'].required = True
        self.fields['length'].label = 'Length (Meter)'
        self.fields['budget'].label = 'Budget (BDT)'
        self.fields['budget'].required = True
        self.fields['number_of_facilities'].required = False

        self.fields['expected_start_date'] = forms.DateTimeField(
            label='Expected start date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.expected_start_date if instance and instance.pk else None
        )

        self.fields['expected_end_date'] = forms.DateTimeField(
            label='Expected end date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.expected_end_date if instance and instance.pk else None
        )

        self.fields['percentage_of_ongoing_interventions'] = forms.ChoiceField(
            label='Percentage of ongoing Facilities',
            required=False,
            choices=((x, x) for x in range(101)),
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.percentage_of_ongoing_interventions if instance else None
        )

        self.fields['date_of_progress_reporting'] = forms.DateTimeField(
            label='Date of Progress Reporting',
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.date_of_progress_reporting if instance and instance.pk else None
        )

        self.fields['repair_or_new_project'] = forms.ChoiceField(
            label='Repair or new project?',
            choices=Repair_New_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.repair_or_new_project if instance and instance.pk else None
        )

        self.fields['number_of_male_pg_member_beneficiary'].label = 'Male'
        self.fields['number_of_male_pg_member_beneficiary'].required = False
        self.fields['number_of_female_pg_member_beneficiary'].label = 'Female'
        self.fields['number_of_female_pg_member_beneficiary'].required = False
        self.fields['number_of_total_pg_member_beneficiary'].label = 'Total'
        self.fields['number_of_total_pg_member_beneficiary'].required = False

        self.fields['number_of_male_non_pg_member_beneficiary'].label = 'Male'
        self.fields['number_of_male_non_pg_member_beneficiary'].required = False
        self.fields['number_of_female_non_pg_member_beneficiary'].label = 'Female'
        self.fields['number_of_female_non_pg_member_beneficiary'].required = False
        self.fields['number_of_total_non_pg_member_beneficiary'].label = 'Total'
        self.fields['number_of_total_non_pg_member_beneficiary'].required = False

        self.fields['number_of_family_people_with_disabilities_male'].label = 'Male'
        self.fields['number_of_family_people_with_disabilities_male'].required = False
        self.fields['number_of_family_people_with_disabilities_female'].label = 'Female'
        self.fields['number_of_family_people_with_disabilities_female'].required = False
        self.fields['number_of_family_people_with_disabilities_total'].label = 'Total'
        self.fields['number_of_family_people_with_disabilities_total'].required = False

        self.add_child_form("water_interventions", water_intervention_formset(
            header='Water intervention details',
            data=data, files=files, queryset=water_intervention_objects, prefix=prefix + '_water_interventions',
            add_more=True, **kwargs
        ))

        self.add_child_form("sanitary_interventions", sanitary_intervention_formset(
            header='Sanitation intervention details',
            data=data, files=files, queryset=sanitary_intervention_objects,
            prefix=prefix + '_sanitary_interventions',
            add_more=True, **kwargs
        ))

        self.add_child_form('completed_contract',
                            CompletedContractForm(
                                data=data, files=files, form_header='Completed Contracts',
                                prefix=self.prefix + '_completed_contract',
                                instance=self.instance.completed_contract if self.instance.pk else None,
                                **kwargs))

    def clean(self):
        super(InterventionForm, self).clean()
        if 'type_of_intervention' in self.cleaned_data and self.cleaned_data['type_of_intervention'] in list(
                        WATER_INTERVENTION_TYPES + SANITATION_INTERVENTION_TYPES):
            if 'number_of_facilities' in self.cleaned_data and self.cleaned_data['number_of_facilities'] is None:
                is_valid = False
                self.add_error('number_of_facilities', 'This field is required.')

        if 'type_of_intervention' in self.cleaned_data and self.cleaned_data[
            'type_of_intervention'] in MANDATORY_LENGTH_INTERVENTION_TYPES:
            if 'length' in self.cleaned_data and self.cleaned_data['length'] is None:
                is_valid = False
                self.add_error('length', 'This field is required.')

        _male_pg_member = self.cleaned_data.get('number_of_male_pg_member_beneficiary', None)
        _female_pg_member = self.cleaned_data.get('number_of_female_pg_member_beneficiary', None)
        _total_pg_member = self.cleaned_data.get('number_of_total_pg_member_beneficiary', None)
        _male_non_pg_member = self.cleaned_data.get('number_of_male_non_pg_member_beneficiary')
        _female_non_pg_member = self.cleaned_data.get('number_of_female_non_pg_member_beneficiary', None)
        _total_non_pg_member = self.cleaned_data.get('number_of_total_non_pg_member_beneficiary', None)
        _disable_family_member_male = self.cleaned_data.get('number_of_family_people_with_disabilities_male', None)
        _disable_family_member_female = self.cleaned_data.get('number_of_family_people_with_disabilities_female', None)
        _disable_family_member_total = self.cleaned_data.get('number_of_family_people_with_disabilities_total', None)

        if _male_pg_member is not None and _female_pg_member is not None and _total_pg_member is not None and int(
                _male_pg_member) + int(_female_pg_member) != int(_total_pg_member):
            self.add_error('number_of_total_pg_member_beneficiary', 'Please insert the correct information')

        if _disable_family_member_male is not None \
                and _disable_family_member_female is not None and _disable_family_member_total is not None and int(
            _disable_family_member_male) + int(_disable_family_member_female) != int(_disable_family_member_total):
            self.add_error('number_of_family_people_with_disabilities_total', 'Please insert the correct information')

        return self.cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            super(InterventionForm, self).save(commit=True)
            if self.instance.type_of_intervention in WATER_INTERVENTION_TYPES:
                self.instance.sanitary_interventions.all().delete()
            elif self.instance.type_of_intervention in SANITATION_INTERVENTION_TYPES:
                self.instance.water_interventions.all().delete()
            else:
                self.instance.water_interventions.all().delete()
                self.instance.sanitary_interventions.all().delete()

            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = Intervention
        fields = ('type_of_intervention', 'intervention_id', 'number_of_facilities', 'length',
                  'budget', 'matching_fund', 'repair_or_new_project', 'expected_start_date', 'expected_end_date',
                  'number_of_fully_completed_intervention', 'number_of_ongoing_interventions',
                  'percentage_of_ongoing_interventions', 'date_of_progress_reporting',
                  'number_of_male_pg_member_beneficiary', 'number_of_female_pg_member_beneficiary',
                  'number_of_total_pg_member_beneficiary', 'number_of_male_non_pg_member_beneficiary',
                  'number_of_female_non_pg_member_beneficiary', 'number_of_total_non_pg_member_beneficiary',
                  'number_of_family_people_with_disabilities_male', 'number_of_family_people_with_disabilities_female',
                  'number_of_family_people_with_disabilities_total'
                  )
        labels = {
            'number_of_fully_completed_intervention': 'Number of fully completed Facilities',
            'number_of_ongoing_interventions': 'Number of ongoing Facilities'
        }

    @classmethod
    def field_groups(cls):
        _group = super(InterventionForm, cls).field_groups()
        _group['Number of PG members benefiting (all family members)'] = ['number_of_male_pg_member_beneficiary',
                                                     'number_of_female_pg_member_beneficiary',
                                                     'number_of_total_pg_member_beneficiary']
        _group['Number of Non-PG members benefiting (all family members)'] = ['number_of_male_non_pg_member_beneficiary',
                                                         'number_of_female_non_pg_member_beneficiary',
                                                         'number_of_total_non_pg_member_beneficiary', ]
        _group['Number of people with disabilities benefiting (all family members)'] = [
            'number_of_family_people_with_disabilities_male', 'number_of_family_people_with_disabilities_female',
            'number_of_family_people_with_disabilities_total']

        return _group
