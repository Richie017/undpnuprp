from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.config.constants.sif_constants import DRINKING_WATER_SOURCES, WATER_INTERVENTION_TYPES, \
    WATER_COLLECTION_TIME_OPTIONS
from undp_nuprp.approvals.models.infrastructures.base.water_intervention import \
    WaterIntervention

__author__ = 'Shuvro'

Yes_No_Choices = (('', 'Select One'), ('Yes', 'Yes'), ('No', 'No'),)

DRINKING_WATER_CHOICES = (('', 'Select one'),)
for dr_water_source in DRINKING_WATER_SOURCES:
    DRINKING_WATER_CHOICES += ((dr_water_source, dr_water_source),)

water_collection_time_choices = (('', 'Select one'),)
for water_collection_time in WATER_COLLECTION_TIME_OPTIONS:
    water_collection_time_choices += ((water_collection_time, water_collection_time),)


class WaterInterventionForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(WaterInterventionForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['source_of_drinking_before_intervention'] = forms.ChoiceField(
            label='Source of drinking water for intended beneficiaries before this intervention',
            choices=DRINKING_WATER_CHOICES,
            required=False,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.source_of_drinking_before_intervention if instance and instance.pk else None
        )

        self.fields['water_collection_time_from_existing_point'] = forms.ChoiceField(
            label='Estimated average time taken for the intended beneficiaries to collect water from their existing ' \
                  'water point',
            choices=water_collection_time_choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.water_collection_time_from_existing_point if instance and instance.pk else None
        )

        self.fields['type_of_water_intervention'] = forms.ChoiceField(
            label='Type of water intervention',
            choices=DRINKING_WATER_CHOICES,
            widget=forms.HiddenInput(),
            required=False,
            initial=instance.water_collection_time_with_this_intervention if instance and instance.pk else None
        )

        self.fields['water_collection_time_with_this_intervention'] = forms.ChoiceField(
            label='Estimated average time taken for the intended beneficiaries to collect water with this intervention',
            choices=water_collection_time_choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            required=False,
            initial=instance.water_collection_time_with_this_intervention if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory'] = forms.ChoiceField(
            required=False,
            label='Has the water quality been checked by a laboratory?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory'] = forms.ChoiceField(
            required=False,
            label='Has the water quality been checked by a laboratory?',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_physical'] = forms.ChoiceField(
            required=False,
            label='Physical',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_physical
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_pH'] = forms.ChoiceField(
            required=False,
            label='pH',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_pH
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_turbidity'] = forms.ChoiceField(
            required=False,
            label='Turbidity',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_turbidity
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_chemical'] = forms.ChoiceField(
            required=False,
            label='Chemical',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_chemical
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_arsenic'] = forms.ChoiceField(
            required=False,
            label='Arsenic',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_arsenic
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_acc_level'] = forms.ChoiceField(
            required=False,
            label='Acceptable Level',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_acc_level
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_nitrate'] = forms.ChoiceField(
            required=False,
            label='Nitrate',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_nitrate
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_florid'] = forms.ChoiceField(
            required=False,
            label='Florid',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_florid
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_for_magnesium'] = forms.ChoiceField(
            required=False,
            label='Magnesium',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_for_magnesium
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_dissolved_solid'] = forms.ChoiceField(
            required=False,
            label='Total Dissolved Solid',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_dissolved_solid
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_microbiological'] = forms.ChoiceField(
            required=False,
            label='Microbiological',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_microbiological
            if instance and instance.pk else None
        )

        self.fields['has_water_quality_been_checked_by_laboratory_fecal_coliform'] = forms.ChoiceField(
            required=False,
            label='Fecal Coliform',
            choices=Yes_No_Choices,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.has_water_quality_been_checked_by_laboratory_fecal_coliform
            if instance and instance.pk else None
        )

    def clean(self):

        _intervention_no = self.prefix[14:].split('_')[0]
        _intervention_lookup_key = 'interventions-{}-type_of_intervention'.format(_intervention_no)
        _type_of_intervention = self.data[_intervention_lookup_key]

        if _type_of_intervention in WATER_INTERVENTION_TYPES:
            super(WaterInterventionForm, self).clean()
            # if 'source_of_drinking_before_intervention' in self.cleaned_data and self.cleaned_data[
            #     'source_of_drinking_before_intervention'] == '':
            #     self.add_error('source_of_drinking_before_intervention', 'This field is required.')
            # if 'water_collection_time_from_existing_point' in self.cleaned_data and self.cleaned_data[
            #     'water_collection_time_from_existing_point'] == '':
            #     self.add_error('water_collection_time_from_existing_point', 'This field is required.')
            # if 'type_of_water_intervention' in self.cleaned_data and self.cleaned_data[
            #     'type_of_water_intervention'] == '':
            #     self.add_error('type_of_water_intervention', 'This field is required.')
            # if 'water_collection_time_with_this_intervention' in self.cleaned_data and self.cleaned_data[
            #     'water_collection_time_with_this_intervention'] == '':
            #     self.add_error('water_collection_time_with_this_intervention', 'This field is required.')

            # if 'has_water_quality_been_checked_by_laboratory' in self.cleaned_data:
            #     _has_water_quality_been_checked_by_laboratory = self.cleaned_data[
            #         'has_water_quality_been_checked_by_laboratory']
            #     if _has_water_quality_been_checked_by_laboratory == '':
            #         self.add_error('has_water_quality_been_checked_by_laboratory', 'This field is required.')
            #
            #     elif _has_water_quality_been_checked_by_laboratory == 'Yes':
            #         if 'has_water_quality_been_checked_by_laboratory_for_arsenic' in self.cleaned_data and \
            #                         self.cleaned_data[
            #                             'has_water_quality_been_checked_by_laboratory_for_arsenic'] == '':
            #             self.add_error('has_water_quality_been_checked_by_laboratory_for_arsenic',
            #                            'This field is required.')
            #         if 'has_water_quality_been_checked_by_laboratory_for_nitrate' in self.cleaned_data and \
            #                         self.cleaned_data[
            #                             'has_water_quality_been_checked_by_laboratory_for_nitrate'] == '':
            #             self.add_error('has_water_quality_been_checked_by_laboratory_for_nitrate',
            #                            'This field is required.')
            #         if 'has_water_quality_been_checked_by_laboratory_for_florid' in self.cleaned_data and \
            #                         self.cleaned_data[
            #                             'has_water_quality_been_checked_by_laboratory_for_florid'] == '':
            #             self.add_error('has_water_quality_been_checked_by_laboratory_for_florid',
            #                            'This field is required.')
            #         if 'has_water_quality_been_checked_by_laboratory_for_magnesium' in self.cleaned_data and \
            #                         self.cleaned_data[
            #                             'has_water_quality_been_checked_by_laboratory_for_magnesium'] == '':
            #             self.add_error('has_water_quality_been_checked_by_laboratory_for_magnesium',
            #                            'This field is required.')

        return self.cleaned_data

    class Meta(GenericFormMixin.Meta):
        model = WaterIntervention
        fields = (
            'source_of_drinking_before_intervention', 'water_collection_time_from_existing_point',
            'type_of_water_intervention', 'water_collection_time_with_this_intervention',
            'has_water_quality_been_checked_by_laboratory',
            'has_water_quality_been_checked_by_laboratory_for_physical',
            'has_water_quality_been_checked_by_laboratory_for_pH',
            'has_water_quality_been_checked_by_laboratory_for_turbidity',
            'has_water_quality_been_checked_by_laboratory_for_chemical',
            'has_water_quality_been_checked_by_laboratory_for_arsenic',
            'has_water_quality_been_checked_by_laboratory_for_acc_level',
            'has_water_quality_been_checked_by_laboratory_for_nitrate',
            'has_water_quality_been_checked_by_laboratory_for_florid',
            'has_water_quality_been_checked_by_laboratory_for_magnesium',
            'has_water_quality_been_checked_by_laboratory_dissolved_solid',
            'has_water_quality_been_checked_by_laboratory_microbiological',
            'has_water_quality_been_checked_by_laboratory_fecal_coliform'
        )

    @classmethod
    def field_groups(cls):
        _group = super(WaterInterventionForm, cls).field_groups()
        _group['Before the intervention'] = ['source_of_drinking_before_intervention',
                                             'water_collection_time_from_existing_point']
        _group['With the intervention'] = [
            'type_of_water_intervention', 'water_collection_time_with_this_intervention',
            'has_water_quality_been_checked_by_laboratory',
        ]
        _group['If Yes, are the following parameters in line with the reference values?'] = [
            'has_water_quality_been_checked_by_laboratory_for_physical',
            'has_water_quality_been_checked_by_laboratory_for_pH',
            'has_water_quality_been_checked_by_laboratory_for_turbidity',
            'has_water_quality_been_checked_by_laboratory_for_chemical',
            'has_water_quality_been_checked_by_laboratory_for_arsenic',
            'has_water_quality_been_checked_by_laboratory_for_acc_level',
            'has_water_quality_been_checked_by_laboratory_for_nitrate',
            'has_water_quality_been_checked_by_laboratory_for_florid',
            'has_water_quality_been_checked_by_laboratory_for_magnesium',
            'has_water_quality_been_checked_by_laboratory_dissolved_solid',
            'has_water_quality_been_checked_by_laboratory_microbiological',
            'has_water_quality_been_checked_by_laboratory_fecal_coliform'
        ]

        return _group
