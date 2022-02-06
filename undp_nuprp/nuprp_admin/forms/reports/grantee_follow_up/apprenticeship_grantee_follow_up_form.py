"""
Created by tareq on 10/3/17
"""
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from undp_nuprp.nuprp_admin.forms.reports.grantee_follow_up.grantee_follow_up_form import GranteeFollowUpForm
from undp_nuprp.nuprp_admin.models.benificieries.grantee import Grantee
from undp_nuprp.nuprp_admin.models.reports.grantees_follow_up.apprenticeship_grantee_follow_up import \
    ApprenticeshipGranteeFollowUp
from undp_nuprp.nuprp_admin.models.reports.grantees_follow_up.education_grantee_follow_up import \
    EducationGranteeFollowUp
from django import forms

__author__ = 'Tareq'


class ApprenticeshipGranteeFollowUpForm(GranteeFollowUpForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(ApprenticeshipGranteeFollowUpForm, self).__init__(data=data, files=files,
                                                                instance=instance, prefix=prefix, **kwargs)
        self.fields['grantee'] = GenericModelChoiceField(queryset=Grantee.objects.filter(
            type_of_grant='Apprenticeship grant'),
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

        self.fields['before_employment_status'] = forms.CharField(
            label='Employment status immediately prior to receiving grant',
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=[
                ('', 'Select One'),
                ('Unemployed', 'Unemployed'),
                ('Employed', 'Employed'),
                ('Self-employed', 'Self-employed'),
            ]))
        self.fields['current_employment_status'] = forms.CharField(
            label='Current employment status (multiple option can be selected)',
            widget=forms.Select(attrs={'class': 'select2', 'width': 'width'}, choices=[
                ('', 'Select One'),
                ('Skilled employment', 'Skilled employment'),
                ('Unskilled employment', 'Unskilled employment'),
                ('Formal employment', 'Formal employment'),
                ('Informal employment', 'Informal employment'),
                ('Employed in the same area received training', 'Employed in the same area received training'),
                ('Employed but, not in the same area received training',
                 'Employed but, not in the same area received training'),
                ('Self-employed or business', 'Self-employed or business'),
                ('Not employed', 'Not employed'),
                ('Employed but not continuing now', 'Employed but not continuing now'),
            ]))

    class Meta(GranteeFollowUpForm.Meta):
        model = ApprenticeshipGranteeFollowUp
        fields = (
            'grantee', 'date_of_last_installment', 'before_employment_status', 'current_employment_status',
            'remarks')
