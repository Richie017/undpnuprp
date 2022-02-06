"""
Created by tareq on 10/2/17
"""
from django import forms
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.benificieries.grantee import Grantee
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = 'Tareq'


class GranteeForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(GranteeForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['town'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name__icontains='city'),
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))
        self.fields['referred_pg_member'] = GenericModelChoiceField(
            queryset=PrimaryGroupMember.objects.all(),
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220', 'data-depends-on': 'town',
                                          'data-url': reverse(PrimaryGroupMember.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1',
                                          'data-depends-property': 'assigned_to:parent:parent:address:geography:id'}
                                   ))

        self.fields['relation_with_pg_member'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=(
                ('', 'Select One'),
                ('PG Member', 'PG Member'),
                ('Spouse', 'Spouse'),
                ('Son', 'Son'),
                ('Daughter', 'Daughter'),
                ('Mother', 'Mother'),
                ('Father', 'Father'),
                ('Uncle', 'Uncle'),
                ('Aunt', 'Aunt'),
                ('Other', 'Other')
            )))

        self.fields['type_of_grant'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=(
                ('', 'Select One'),
                ('Apprenticeship grant', 'Apprenticeship grant'),
                ('Business grant', 'Business grant'),
                ('Education grant', 'Education grant'),
            )))

        self.fields['gender'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=(
                ('', 'Select One'),
                ('Male', 'Male'),
                ('Female', 'Female'),
                ('Hijra', 'Hijra'),
            )))

        self.fields['religion'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=(
                ('', 'Select One'),
                ('Muslim', 'Muslim'),
                ('Hindu', 'Hindu'),
                ('Buddhist', 'Buddhist'),
                ('Christian', 'Christian'),
                ('Other', 'Other')
            )))

        self.fields['ethnicity'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=(
                ('', 'Select One'),
                ('Bengali', 'Bengali'),
                ('Indigenous CHT', 'Indigenous CHT'),
                ('Bihari', 'Bihari'),
                ('Rohyngia', 'Rohyngia'),
                ('Dalit', 'Dalit'),
                ('Horizon', 'Horizon'),
                ('Other', 'Other')
            )))

        self.fields['highest_level_of_education'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=(
                ('', 'Select One'),
                ('Pre-primary/ Moktab', 'Pre-primary/ Moktab'),
                ('Primary/ Ibtadayee/ JDC', 'Primary/ Ibtadayee/ JDC'),
                ('Secondary / Dakhil', 'Secondary / Dakhil'),
                ('Higher Secondary/ Alim', 'Higher Secondary/ Alim'),
                ('University/ Fazil / Kamil ', 'University/ Fazil / Kamil '),
                ('Never attended school', 'Never attended school'),
                ('Do not know', 'Do not know')
            )))

        self.fields['area_of_business'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=(
                ('', 'Select One'),
                ('Small business', 'Small business'),
                ('Cow/goat/sheep/chicken rearing', 'Cow/goat/sheep/chicken rearing'),
                ('Rickshaw/van purchase,', 'Rickshaw/van purchase,'),
                ('Agriculture', 'Agriculture'),
                ('Farming', 'Farming'),
                ('Other', 'Other')
            )))

        self.fields['contract_start_date'] = forms.DateTimeField(
            label='Contract Start Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.contract_start_date if instance else None
        )

        self.fields['contract_end_date'] = forms.DateTimeField(
            label='Contract End Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.contract_end_date if instance else None
        )

        self.fields['first_installment_date'] = forms.DateTimeField(
            label='First Installment Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.first_installment_date if instance else None
        )

    class Meta(GenericFormMixin.Meta):
        model = Grantee
        fields = ('town', 'referred_pg_member', 'relation_with_pg_member', 'gender', 'age',
                  'religion', 'ethnicity', 'highest_level_of_education', 'type_of_grant',
                  'area_of_business', 'contact_no', 'contract_start_date', 'contract_end_date',
                  'first_installment_date')
