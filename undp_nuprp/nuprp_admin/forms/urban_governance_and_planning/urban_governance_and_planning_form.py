from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.urban_governance_and_planning.urban_governance_and_planning import \
    UrbanGovernanceAndPlanning

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class UrbanGovernanceAndPlanningForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(UrbanGovernanceAndPlanningForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City', empty_label='Select One',
            initial=instance.city if instance else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )

        self.fields['ward_committee_established'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='Established?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.ward_committee_established if instance and instance.pk else None
        )

        self.fields['ward_committee_functional'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='Functional?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.ward_committee_functional if instance and instance.pk else None
        )

        self.fields['drafted'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='Drafted?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.drafted if instance and instance.pk else None
        )

        self.fields['finalized'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='Finalized?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.finalized if instance and instance.pk else None
        )

        self.fields['approved'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='Approved?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.approved if instance and instance.pk else None
        )

        self.fields['standing_committee_established'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='Established?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.standing_committee_established if instance and instance.pk else None
        )

        self.fields['standing_committee_functional'] = forms.ChoiceField(
            required=False,
            choices=Yes_No_Choices,
            label='Functional?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.standing_committee_functional if instance and instance.pk else None
        )

    class Meta:
        model = UrbanGovernanceAndPlanning
        fields = (
            'city', 'ward_committee_ward_no', 'ward_committee_established',
            'ward_committee_functional',
            'drafted', 'finalized', 'approved',
            'standing_committee_ward_no', 'standing_committee_established',
            'standing_committee_functional'
        )
        labels = {
            'city': 'City',
            'ward_committee_ward_no': 'Ward No',
            'standing_committee_ward_no': 'Ward No'
        }

    @classmethod
    def field_groups(cls):
        _group = super(UrbanGovernanceAndPlanningForm, cls).field_groups()

        _group['Ward Committee'] = [
            'ward_committee_ward_no',
            'ward_committee_established',
            'ward_committee_functional'
        ]
        _group['Institutional Financial Capacity'] = [
            'drafted',
            'finalized',
            'approved'
        ]
        _group['Standing Committee'] = [
            'standing_committee_ward_no',
            'standing_committee_established',
            'standing_committee_functional'
        ]

        return _group
