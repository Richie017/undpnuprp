from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.scc_partnership.agreed_partnership import \
    AgreedPartnership

__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class AgreedPartnershipForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(AgreedPartnershipForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                    **kwargs)

        self.fields['is_agreed_partnership'] = forms.ChoiceField(
            label='Partnerships agreed?',
            required=False,
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.is_agreed_partnership if instance and instance.pk else None
        )

        self.fields['date_of_agreement'] = forms.DateTimeField(
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
            initial=instance.date_of_agreement if instance and instance.pk else None
        )

    def clean(self):
        super(AgreedPartnershipForm, self).clean()
        if self.cleaned_data['is_agreed_partnership'] == 'No':
            self.cleaned_data['date_of_agreement'] = None
            self.cleaned_data['with_which_organisation'] = None
            self.cleaned_data['duration_of_agreement'] = None
            self.cleaned_data['partnership_related_to_what'] = None
        return self.cleaned_data

    class Meta(GenericFormMixin.Meta):
        model = AgreedPartnership
        fields = ('date_of_agreement', 'is_agreed_partnership', 'with_which_organisation', 'duration_of_agreement',
                  'partnership_related_to_what')

        widgets = {
            'with_which_organisation': forms.Textarea,
            'partnership_related_to_what': forms.Textarea
        }

        labels = {
            'with_which_organisation': 'With which organisation?', 'duration_of_agreement': 'Duration of agreement?',
            'partnership_related_to_what': 'Partnership related to what?'
        }
