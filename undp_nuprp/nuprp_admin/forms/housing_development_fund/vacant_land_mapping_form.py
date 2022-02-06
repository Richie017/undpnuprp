from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.housing_development_fund.vacant_land_mapping import VacantLandMapping

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)


class VacantLandMappingForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(VacantLandMappingForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                    **kwargs)

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

        self.fields['vacant_land_mapping_required'] = forms.ChoiceField(
            required=False,
            label='Vacant land mapping required?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.vacant_land_mapping_required if instance and instance.pk else None
        )

        self.fields['survey_completed'] = forms.ChoiceField(
            required=False,
            label='Survey completed?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.survey_completed if instance and instance.pk else None
        )

        self.fields['mapping_completed'] = forms.ChoiceField(
            required=False,
            label='Mapping Completed?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.mapping_completed if instance and instance.pk else None
        )

        self.fields['vlm_approved'] = forms.ChoiceField(
            required=False,
            label='VLM Approved?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.vlm_approved if instance and instance.pk else None
        )

    class Meta(GenericFormMixin.Meta):
        model = VacantLandMapping

        fields = (
            'city', 'vacant_land_mapping_required', 'survey_completed', 'mapping_completed', 'vlm_approved'
        )
