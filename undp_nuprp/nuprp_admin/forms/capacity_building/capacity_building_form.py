"""
    Created by tareq on 9/22/19
"""

from pydoc import plain
from django import forms
from django.db import transaction
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster
from undp_nuprp.nuprp_admin.models.output_title_link.output_title_link import OutputTitleLink
from undp_nuprp.nuprp_admin.enums.capacity_building_output_enum import CapacityBuildingOutputEnum
from undp_nuprp.nuprp_admin.enums.capacity_building_organization_enum import CapacityBuildingOrganizationEnum
from undp_nuprp.nuprp_admin.enums.capacity_building_type_enum import CapacityBuildingTypeEnum
from undp_nuprp.nuprp_admin.models.capacity_building.capacity_building import CapacityBuilding

__author__ = "Tareq"


class CapacityBuildingForm(GenericFormMixin):

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CapacityBuildingForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)


        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['type_of_capacity_building'] = forms.IntegerField(
            widget=forms.Select(attrs={'class': 'select2'}, choices=CapacityBuildingTypeEnum.get_choice_list()))
        
        
        # print(CapacityBuildingOutputEnum.get_output_choice_list_from_object(OutputTitleLink.objects.all().distinct('output')))
        self.fields['output'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2'}, choices=CapacityBuildingOutputEnum.get_output_choice_list_from_object(OutputTitleLink.objects.all().distinct('output'))))
        
        
        # print(CapacityBuildingOutputEnum.get_title_choice_list_from_object(OutputTitleLink.objects.all()))
        self.fields['title'] = forms.CharField(
            widget=forms.Select(attrs={'class': 'select2'}, choices=CapacityBuildingOutputEnum.get_title_choice_list_from_object(OutputTitleLink.objects.all())))


        self.fields['organized_by'] = forms.IntegerField(
            widget=forms.Select(attrs={'class': 'select2'}, choices=CapacityBuildingOrganizationEnum.get_choice_list()))
        self.fields['start_date'] = forms.DateField(
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker'
                },
                format='%d/%m/%Y'
            ),
        )
        self.fields['end_date'] = forms.DateField(
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker'
                },
                format='%d/%m/%Y'
            ),
        )

    @classmethod
    def field_groups(cls):
        _group = super(CapacityBuildingForm, cls).field_groups()
        _group['Cumulative Progress'] = [
            'batched_planned', 'batched_held', 'cumulative_male', 'cumulative_female', 'cumulative_disabled']
        _group['Participants and Cost in the Reporting Month'] = [
            'start_date', 'end_date', 'duration', 'number_of_male_cluster_leader', 'number_of_female_cluster_leader',
            'number_of_disabled_cluster_leader',
            'number_of_male_cluster_member', 'number_of_female_cluster_member', 'number_of_disabled_cluster_member',
            'number_of_male_elected',
            'number_of_female_elected', 'number_of_disabled_elected', 'number_of_male_town_staff',
            'number_of_female_town_staff',
            'number_of_disabled_town_staff',
            'number_of_male_other', 'number_of_female_other', 'number_of_disabled_other', 'specify_if_other', 'total_budget',
            'total_cost', 'organized_by',
            'specify_if_other_organizer', 'venue'
        ]
        _group['Remarks'] = ['remarks']
        return _group

    def clean(self):
        cleaned_data = super(CapacityBuildingForm, self).clean()

        print("Cleaned Data")
        print(cleaned_data)

        type_of_capacity_building = cleaned_data['type_of_capacity_building']
        specify_if_other_type_of_cb = cleaned_data['specify_if_other_type_of_cb']

        organized_by = cleaned_data['organized_by']
        specify_if_other_organizer = cleaned_data['specify_if_other_organizer']

        if type_of_capacity_building == CapacityBuildingTypeEnum.Other.value and specify_if_other_type_of_cb == '':
            self.add_error('specify_if_other_type_of_cb', "Please specify the type.")
        if type_of_capacity_building != CapacityBuildingTypeEnum.Other.value and specify_if_other_type_of_cb != '':
            self.add_error('specify_if_other_type_of_cb', "This field should be empty.")

        if organized_by == CapacityBuildingOrganizationEnum.Other.value and specify_if_other_organizer == '':
            self.add_error('specify_if_other_organizer', "Please specify the type.")
        if organized_by != CapacityBuildingOrganizationEnum.Other.value and specify_if_other_organizer != '':
            self.add_error('specify_if_other_organizer', "This field should be empty.")

        return cleaned_data

    # def save(self):
    #     with transaction.atomic():
    #         print("Save Capacity Building")
    #         super(CapacityBuildingForm, self).save()
    #         self.instance.save()
    #         return self.instance


    class Meta(GenericFormMixin.Meta):
        model = CapacityBuilding
        fields = [
            'city', 'output', 'type_of_capacity_building', 'specify_if_other_type_of_cb', 'title',

            'batched_planned', 'batched_held', 'cumulative_male', 'cumulative_female', 'cumulative_disabled',

            'start_date', 'end_date', 'duration', 'number_of_male_cluster_leader', 'number_of_female_cluster_leader',
            'number_of_disabled_cluster_leader',
            'number_of_male_cluster_member', 'number_of_female_cluster_member', 'number_of_disabled_cluster_member',
            'number_of_male_elected',
            'number_of_female_elected', 'number_of_disabled_elected', 'number_of_male_town_staff',
            'number_of_female_town_staff', 'number_of_disabled_town_staff',
            'number_of_male_other', 'number_of_female_other', 'number_of_disabled_other', 'specify_if_other', 'total_budget',
            'total_cost', 'organized_by',
            'specify_if_other_organizer', 'venue', 'remarks'
        ]
        labels = {
            'type_of_capacity_building': 'Type of Capacity Building Activity',
            'specify_if_other_type_of_cb': 'Specify if other',
            'specify_if_other_organizer': 'Specify if other',
            'duration': 'Duration',
            'batched_planned': 'No. of total Courses/batches Planned',
            'batched_held': 'No. of total Courses/batches Held',
            'cumulative_male': 'Male',
            'cumulative_female': 'Female',
            'cumulative_disabled': 'Person with disabilities',
            'number_of_male_cluster_leader': 'No of PG/CDC/Cluster Leaders (male)',
            'number_of_female_cluster_leader': 'No of PG/CDC/Cluster Leaders (female)',
            'number_of_disabled_cluster_leader': 'No of PG/CDC/Cluster Leaders (person with disabilities)',
            'number_of_male_cluster_member': 'No of PG/CDC/Cluster members (male)',
            'number_of_female_cluster_member': 'No of PG/CDC/Cluster members (female)',
            'number_of_disabled_cluster_member': 'No of PG/CDC/Cluster members (person with disabilities)',
            'number_of_male_elected': 'No of Local Elected Person (male)',
            'number_of_female_elected': 'No of Local Elected Person (female)',
            'number_of_disabled_elected': 'No of Local Elected Person (person with disabilities)',
            'number_of_male_town_staff': 'No of Town Staff (male)',
            'number_of_female_town_staff': 'No of Town Staff (female)',
            'number_of_disabled_town_staff': 'No of Town Staff (person with disabilities)',
            'number_of_male_other': 'Other (male)',
            'number_of_female_other': 'Other (female)',
            'number_of_disabled_other': 'Other (person with disabilities)'
        }
