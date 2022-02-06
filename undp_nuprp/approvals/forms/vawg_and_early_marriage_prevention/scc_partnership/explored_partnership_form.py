from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.scc_partnership.explored_partnership import \
    ExploredPartnership

__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class ExploredPartnershipForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(ExploredPartnershipForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                      **kwargs)

        self.fields['is_partnerships_explored'] = forms.ChoiceField(
            label='Partnerships explored (e.g. through meetings, letters etc)',
            required=False,
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.is_partnerships_explored if instance and instance.pk else None
        )

        self.fields['date_of_partnership'] = forms.DateTimeField(
            label='Date',
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
            initial=instance.date_of_partnership if instance and instance.pk else None
        )

    def clean(self):
        super(ExploredPartnershipForm, self).clean()
        if self.cleaned_data['is_partnerships_explored'] == 'No':
            self.cleaned_data['date_of_partnership'] = None
            self.cleaned_data['with_which_organisation'] = None
            self.cleaned_data['partnership_related_to_what'] = None
        return self.cleaned_data


    class Meta(GenericFormMixin.Meta):
        model = ExploredPartnership
        fields = ('date_of_partnership', 'is_partnerships_explored', 'with_which_organisation',
                  'partnership_related_to_what')
        widgets = {
            'with_which_organisation': forms.Textarea,
            'partnership_related_to_what': forms.Textarea
        }

        labels = {
            'with_which_organisation': 'With which organisation?',
            'partnership_related_to_what': 'Partnership related to what?',
        }
