from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.scc_partnership.activities_of_partnership import \
    ActivitiesOfPartnership

__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class ActivitiesOfPartnershipForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(ActivitiesOfPartnershipForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                          **kwargs)

        self.fields['conducted_partnership_activities'] = forms.ChoiceField(
            label='Partnership activities conducted?',
            required=False,
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.conducted_partnership_activities if instance and instance.pk else None
        )

        self.fields['date_of_activity'] = forms.DateTimeField(
            label='Date of activity',
            required=False,
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.date_of_activity if instance and instance.pk else None
        )

    def clean(self):
        super(ActivitiesOfPartnershipForm, self).clean()
        if self.cleaned_data['conducted_partnership_activities'] == 'No':
            self.cleaned_data['date_of_activity'] = None
            self.cleaned_data['with_which_organisation'] = None
            self.cleaned_data['explanation_of_the_activity'] = None
        return self.cleaned_data

    class Meta(GenericFormMixin.Meta):
        model = ActivitiesOfPartnership
        fields = ('date_of_activity', 'conducted_partnership_activities', 'with_which_organisation',
                  'explanation_of_the_activity')
        widgets = {
            'with_which_organisation': forms.Textarea,
            'explanation_of_the_activity': forms.Textarea
        }

        labels = {
            'with_which_organisation': 'With which organisation?'
        }
