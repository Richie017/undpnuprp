from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.config.constants.sif_constants import SANITATION_FACILITY_TYPES, SANITATION_INTERVENTION_TYPES
from undp_nuprp.approvals.models.infrastructures.base.sanitary_intervention import \
    SanitaryIntervention

__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)
sanitation_facility_choices = (('', 'Select One'),)

for sanitation_facility in SANITATION_FACILITY_TYPES:
    sanitation_facility_choices += ((sanitation_facility, sanitation_facility),)


class SanitaryInterventionForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SanitaryInterventionForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                       **kwargs)

        self.fields['type_of_sanitation_before_intervention'] = forms.ChoiceField(
            label='Type of sanitation facility used by intended beneficiaries before this intervention?',
            choices=sanitation_facility_choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.type_of_sanitation_before_intervention if instance and instance.pk else None
        )

        self.fields['is_excreta_safely_disposed'] = forms.ChoiceField(
            label='Excreta is safely disposed in situ or transported to a designated place for safe disposal or '
                  'treatment?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.is_excreta_safely_disposed if instance and instance.pk else None
        )

        self.fields['does_beneficiary_share_sanitation'] = forms.ChoiceField(
            label='Are the intended beneficiaries currently sharing sanitation facilities?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.does_beneficiary_share_sanitation if instance and instance.pk else None
        )

        self.fields['type_of_sanitation_with_intervention'] = forms.ChoiceField(
            label='Type of sanitation facility',
            choices=sanitation_facility_choices,
            widget=forms.HiddenInput(),
            required=False,
            initial=instance.type_of_sanitation_with_intervention if instance and instance.pk else None
        )

        self.fields['will_the_sanitation_be_shared'] = forms.ChoiceField(
            label='Will the sanitation facility be shared by HHs?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.will_the_sanitation_be_shared if instance and instance.pk else None
        )

        self.fields['will_excreta_be_safely_disposed'] = forms.ChoiceField(
            label='Will excreta be safely disposed of in situ or transported to a designated place for safe '
                  'disposal or treatment?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.will_excreta_be_safely_disposed if instance and instance.pk else None
        )

        self.fields['if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter'] = forms.ChoiceField(
            label='If a twin pit latrine, are the bottom of the rings more than 2 meters from the ground water',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter
            if instance and instance.pk else None
        )

        self.fields['is_the_latrine_at_least_15_meters_from_nearest_water_source'] = forms.ChoiceField(
            label='Is the latrine at least 15 meters from the nearest water source?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.is_the_latrine_at_least_15_meters_from_nearest_water_source
            if instance and instance.pk else None
        )

    def clean(self):
        _intervention_no = self.prefix[14:].split('_')[0]
        _intervention_lookup_key = 'interventions-{}-type_of_intervention'.format(_intervention_no)
        _type_of_intervention = self.data[_intervention_lookup_key]

        if _type_of_intervention in SANITATION_INTERVENTION_TYPES:
            super(SanitaryInterventionForm, self).clean()
            # if 'type_of_sanitation_before_intervention' in self.cleaned_data and self.cleaned_data[
            #     'type_of_sanitation_before_intervention'] == '':
            #     self.add_error('type_of_sanitation_before_intervention', 'This field is required.')
            # if 'is_excreta_safely_disposed' in self.cleaned_data and self.cleaned_data[
            #     'is_excreta_safely_disposed'] == '':
            #     self.add_error('is_excreta_safely_disposed', 'This field is required.')
            # if 'does_beneficiary_share_sanitation' in self.cleaned_data and self.cleaned_data[
            #     'does_beneficiary_share_sanitation'] == '':
            #     self.add_error('does_beneficiary_share_sanitation', 'This field is required.')
            # if 'type_of_sanitation_with_intervention' in self.cleaned_data and self.cleaned_data[
            #     'type_of_sanitation_with_intervention'] == '':
            #     self.add_error('type_of_sanitation_with_intervention', 'This field is required.')
            # if 'will_the_sanitation_be_shared' in self.cleaned_data and self.cleaned_data[
            #     'will_the_sanitation_be_shared'] == '':
            #     self.add_error('will_the_sanitation_be_shared', 'This field is required.')
            # if 'will_excreta_be_safely_disposed' in self.cleaned_data and self.cleaned_data[
            #     'will_excreta_be_safely_disposed'] == '':
            #     self.add_error('will_excreta_be_safely_disposed', 'This field is required.')
            # For Single pit latrine intervention type, we have to skip checking the following field
            # Source - https://redmine.field.buzz/issues/16633
            # if _type_of_intervention in SANITATION_INTERVENTION_TYPES[1:] and \
            #         'if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter' in self.cleaned_data and \
            #         self.cleaned_data['if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter'] == '':
            #     self.add_error('if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter',
            #                    'This field is required.')
            # if 'is_the_latrine_at_least_15_meters_from_nearest_water_source' in self.cleaned_data and \
            #                 self.cleaned_data['is_the_latrine_at_least_15_meters_from_nearest_water_source'] == '':
            #     self.add_error('is_the_latrine_at_least_15_meters_from_nearest_water_source',
            #                    'This field is required.')

        return self.cleaned_data

    class Meta(GenericFormMixin.Meta):
        model = SanitaryIntervention
        fields = (
            'type_of_sanitation_before_intervention', 'is_excreta_safely_disposed', 'does_beneficiary_share_sanitation',
            'type_of_sanitation_with_intervention', 'will_the_sanitation_be_shared', 'will_excreta_be_safely_disposed',
            'if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter',
            'is_the_latrine_at_least_15_meters_from_nearest_water_source'
        )

    @classmethod
    def field_groups(cls):
        _group = super(SanitaryInterventionForm, cls).field_groups()
        _group['Before the intervention'] = ['type_of_sanitation_before_intervention', 'is_excreta_safely_disposed',
                                             'does_beneficiary_share_sanitation', ]
        _group['With the intervention'] = ['type_of_sanitation_with_intervention', 'will_the_sanitation_be_shared',
                                           'will_excreta_be_safely_disposed',
                                           'if_twin_pit_latrine_are_bottom_of_the_rings_more_than_two_meter',
                                           'is_the_latrine_at_least_15_meters_from_nearest_water_source']
        return _group
