from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.citizen_participation_and_community_mobilization.community_scorecard import \
    CommunityScorecard
from datetime import date

YEAR_CHOICES = tuple()
YEAR_CHOICES += (('', "Select One"),)
for year in range(2000, 2101):
    YEAR_CHOICES += ((year, str(year)),)


class CommunityScorecardForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CommunityScorecardForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['year'] = forms.ChoiceField(
            choices=YEAR_CHOICES, required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=date.today().year
        )

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

    class Meta(GenericFormMixin.Meta):
        model = CommunityScorecard

        fields = (
            'year', 'city', 'ward_no', 'established', 'matured', 'functional', 'discontinued'
        )

        labels = {
            'established': 'How many established?',
            'matured': 'How many matured?',
            'functional': 'How many functional?',
            'discontinued': 'How many discontinued?'
        }

    def save(self, commit=True):
        if len(self.cleaned_data['ward_no']) == 1:
            self.instance.ward_no = "0" + str(self.cleaned_data['ward_no'])
        return super(CommunityScorecardForm, self).save(commit=commit)
