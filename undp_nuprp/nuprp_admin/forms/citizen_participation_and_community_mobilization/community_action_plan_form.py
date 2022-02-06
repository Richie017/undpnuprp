from datetime import date

from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericMultipleChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.citizen_participation_and_community_mobilization.community_action_plan import \
    CommunityActionPlan

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)

proposals = (
    ('Infrastructure', 'Infrastructure'),
    ('Social Development', 'Social Development'),
    ('Business and Employment', 'Business and Employment')
)

YEAR_CHOICES = tuple()
YEAR_CHOICES += (('', "Select One"),)
for year in range(2000, 2101):
    YEAR_CHOICES += ((year, str(year)),)


class CommunityActionPlanForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CommunityActionPlanForm, self).__init__(
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

        self.fields['approved_proposals'] = GenericMultipleChoiceField(
            required=False,
            choices=proposals,
            label='Select approved proposals',
            widget=forms.SelectMultiple(
                attrs={'class': 'select2'}
            ),
            initial=instance.approved_proposals.split(',') if instance and instance.pk else None
        )

        self.fields['cap_integrated_in_ward_planning'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='CAP integrated in ward planning?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.cap_integrated_in_ward_planning if instance and instance.pk else None
        )

    def clean(self):
        cleaned_data = super(CommunityActionPlanForm, self).clean()
        if isinstance(cleaned_data['approved_proposals'], list):
            _approval_proposals = cleaned_data['approved_proposals']
            if 'Infrastructure' not in _approval_proposals:
                cleaned_data['how_many_of_approved_infrastructure_proposals'] = None
            if 'Social Development' not in _approval_proposals:
                cleaned_data['how_many_of_approved_social_development_proposals'] = None
            if 'Business and Employment' not in _approval_proposals:
                cleaned_data['how_many_of_approved_business_and_employment_proposals'] = None
            cleaned_data['approved_proposals'] = ','.join(_approval_proposals)

        return cleaned_data

    class Meta(GenericFormMixin.Meta):
        model = CommunityActionPlan

        fields = [
            'year', 'city', 'ward_no', 'cap_developed', 'approved_proposals',
            'how_many_of_approved_infrastructure_proposals',
            'how_many_of_approved_social_development_proposals',
            'how_many_of_approved_business_and_employment_proposals', 'cap_integrated_in_ward_planning'
        ]

        labels = {
            'cap_developed': 'How many CAP developed?'
        }

    def save(self, commit=True):
        if len(self.cleaned_data['ward_no']) == 1:
            self.instance.ward_no = "0" + str(self.cleaned_data['ward_no'])
        return super(CommunityActionPlanForm, self).save(commit=commit)
