"""
Created by tareq on 10/3/17
"""
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from undp_nuprp.nuprp_admin.forms.reports.grantee_follow_up.grantee_follow_up_form import GranteeFollowUpForm
from undp_nuprp.nuprp_admin.models.benificieries.grantee import Grantee
from undp_nuprp.nuprp_admin.models.reports.grantees_follow_up.education_grantee_follow_up import \
    EducationGranteeFollowUp
from django import forms

__author__ = 'Tareq'


class EducationGranteeFollowUpForm(GranteeFollowUpForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(EducationGranteeFollowUpForm, self).__init__(data=data, files=files,
                                                           instance=instance, prefix=prefix, **kwargs)
        self.fields['grantee'] = GenericModelChoiceField(queryset=Grantee.objects.filter(
            type_of_grant='Education grant'),
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}),
            initial=instance.grantee if instance else None)
        self.fields['date_of_last_installment'] = forms.DateTimeField(
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.date_of_last_installment if instance else None
        )

        class_choices = [('', 'Select One')]
        for i in range(1, 11):
            class_choices.append(('Class %d' % (i,), 'Class %d' % (i,)))

        self.fields['first_year_school'] = forms.CharField(
            label='Year of schooling during first instalment of grant',
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=class_choices))
        self.fields['current_year_school'] = forms.CharField(
            label='Current year of schooling (at the time of reporting)',
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=class_choices))

    class Meta(GranteeFollowUpForm.Meta):
        model = EducationGranteeFollowUp
        fields = (
            'grantee', 'date_of_last_installment', 'first_year_school', 'current_year_school', 'status_of_education',
            'remarks')
