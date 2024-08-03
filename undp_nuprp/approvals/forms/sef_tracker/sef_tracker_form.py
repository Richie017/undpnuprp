from collections import OrderedDict
from datetime import date

from django import forms
from django.urls import reverse

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.sef_tracker.sef_tracker import SEFTracker
from undp_nuprp.nuprp_admin.models import CDC, CDCCluster

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)
CDC_OR_Cluster_Choices = (('', 'Select One'), ('CDC', 'CDC'), ('Cluster', 'Cluster'))
Category_Name_Choices = (('', "Select One"), ('Business', 'Business'), ('Apprenticeship', 'Apprenticeship'),
                          ('Education', 'Education'), ('Nutrition', 'Nutrition') )


class SEFTrackerForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFTrackerForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
            initial=instance.city if instance and instance.pk else None,
            label='City',
            empty_label='Select One',
            required=False,
            widget=forms.Select(
                attrs={
                    'class': 'select2',
                    'width': '220',
                }
            )
        )

        self.fields['contract_with_cdc_or_cluster'] = forms.ChoiceField(
            label='Contract with CDC or Cluster',
            choices=CDC_OR_Cluster_Choices,
            required=True,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.contract_with_cdc_or_cluster if instance else None
        )

        self.fields['cluster'] = GenericModelChoiceField(
            required=False,
            queryset=CDCCluster.objects.all(), label='Cluster',
            initial=instance.cluster if instance and instance.pk else None,
            widget=forms.TextInput(attrs={
                'class': 'select2-input', 'width': '220',
                'data-depends-on': 'city',
                'data-depends-property': 'address:geography:id',
                'data-url': reverse(CDCCluster.get_route_name(ViewActionEnum.Manage)
                                    ) + '?format=json&search=1&disable_pagination=1&sort=name'
            })
        )

        self.fields['cdc'] = GenericModelChoiceField(
            required=False,
            queryset=CDC.objects.all(), label='CDC',
            initial=instance.cdc if instance and instance.pk else None,
            widget=forms.TextInput(attrs={
                'class': 'select2-input', 'width': '220',
                'data-depends-on': 'city',
                'data-depends-property': 'address:geography:parent:id',
                'data-url': reverse(CDC.get_route_name(ViewActionEnum.Manage)
                                    ) + '?format=json&search=1&disable_pagination=1&sort=name'
            })
        )

        self.fields['actual_contract_start_date'] = forms.DateTimeField(
            label='Actual contract start date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ), required=False,
            initial=instance.actual_contract_start_date if instance and instance.pk else None
        )

        self.fields['actual_contract_end_date'] = forms.DateTimeField(
            label='Actual contract end date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ), required=False,
            initial=instance.actual_contract_end_date if instance and instance.pk else None
        )

        today = date.today()
        year_choices = tuple()
        for y in range(2000, 2100):
            year_choices += ((y, str(y)),)

        self.fields['contract_year'] = forms.ChoiceField(
            choices=year_choices,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=today.year
        )

        self.fields['category_name'] = forms.ChoiceField(
            choices=Category_Name_Choices,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            )
        )

        # self.fields['installment_number'].widget = forms.HiddenInput()
        self.fields['installment_number'].label = "Installment_number"

        self.fields['transfer_from_cluster_cdc'].label = 'Transfer to cluster CDC'

    def clean(self):
        cleaned_data = super(SEFTrackerForm, self).clean()

        if cleaned_data['category_name'] != 'Nutrition':
            cleaned_data['Installment_number'] = ""
        return cleaned_data

    class Meta:
        model = SEFTracker

        fields = ('city', 'ward', 'contract_with_cdc_or_cluster', 'cluster', 'cdc', 'contract_number', 'contract_year',
                  'category_name', 'male_beneficiaries', 'female_beneficiaries', 'third_gender_beneficiaries',
                  'contract_value', 'training_cost', 'management_fee', 'installment_number',
                  'transfer_from_cluster_cdc', 'balance_with_town', 'expenditure_made_by_cluster_cdc',
                  'balance_with_cluster_cdc', 'actual_contract_start_date', 'actual_contract_end_date',
                  'achieved_male_beneficiaries', 'achieved_female_beneficiaries', 'achieved_third_gender_beneficiaries')

        render_tab = True
        tabs = OrderedDict([
            ('Part A',
             ['city', 'ward', 'contract_with_cdc_or_cluster', 'cluster', 'cdc', 'contract_number', 'contract_year',
              'category_name', 'male_beneficiaries', 'female_beneficiaries', 'third_gender_beneficiaries',
              'contract_value', 'training_cost', 'management_fee', 'installment_number']),
            ('Part B',
             ['transfer_from_cluster_cdc', 'balance_with_town', 'expenditure_made_by_cluster_cdc',
              'balance_with_cluster_cdc', 'actual_contract_start_date', 'actual_contract_end_date',
              'achieved_male_beneficiaries', 'achieved_female_beneficiaries', 'achieved_third_gender_beneficiaries'])
        ])

    @classmethod
    def field_groups(cls):
        _group = super(SEFTrackerForm, cls).field_groups()

        _group['Primary Info'] = ['city', 'ward', 'contract_with_cdc_or_cluster', 'cluster', 'cdc', 'contract_number',
                                  'contract_year', 'category_name']

        _group['No of Beneficiaries'] = ['male_beneficiaries', 'female_beneficiaries', 'third_gender_beneficiaries']

        _group['Contract Value'] = ['contract_value', 'training_cost', 'management_fee', 'installment_number']

        _group['Fund Status'] = ['transfer_from_cluster_cdc', 'balance_with_town', 'expenditure_made_by_cluster_cdc',
                                 'balance_with_cluster_cdc']

        _group['Actual Contract Date'] = ['actual_contract_start_date', 'actual_contract_end_date']

        _group['Achieved Beneficiaries'] = ['achieved_male_beneficiaries', 'achieved_female_beneficiaries',
                                            'achieved_third_gender_beneficiaries']

        return _group

    def save(self, commit=True):
        if len(self.cleaned_data['ward']) == 1:
            self.instance.ward = "0" + str(self.cleaned_data['ward'])
        return super(SEFTrackerForm, self).save(commit=commit)
