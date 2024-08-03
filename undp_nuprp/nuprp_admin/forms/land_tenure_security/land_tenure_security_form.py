from django import forms
from django.urls import reverse

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models import LandTenureSecurity

__author__ = "Mahbub"


class LandTenureSecurityForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(LandTenureSecurityForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )

        self.fields['ward'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Ward').order_by('name'),
            label='Ward Number',
            empty_label='Select One',
            initial=instance.ward if instance is not None else None,
            widget=forms.TextInput(
                attrs={
                    'class': 'select2-input', 'width': '220', 'data-depends-on': 'city',
                    'data-depends-property': 'parent:id', 'data-url':
                        reverse(Geography.get_route_name(
                            ViewActionEnum.Manage)) + "?search=1&format=json&disable_pagination=1"
                })
        )

        self.fields['land_transfer_status'] = forms.CharField(
            label='Land transfer status', required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Yes', 'Yes'),
                    ('No', 'No'),
                )
            )
        )

        self.fields['is_mou_signed'] = forms.CharField(
            label='MoU signed', required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Yes', 'Yes'),
                    ('No', 'No'),
                )
            )
        )

        self.fields['date_of_mou_sign'] = forms.DateTimeField(
            label='Date of MoU sign', required=False,
            input_formats=['%d/%m/%Y'],
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
        )

        self.fields['allocated_land_area'].required = False
        self.fields['total_number_of_grantees'].required = False
        self.fields['number_of_sweepers_and_cleaners'].required = False
        self.fields['number_of_existing_dwellers'].required = False
        self.fields['number_of_general_beneficiaries'].required = False
        self.fields['number_of_grantees_with_disability'].required = False
        self.fields['number_of_grantees_with_difficulty_in_seeing'].required = False
        self.fields['number_of_grantees_with_difficulty_in_hearing'].required = False
        self.fields['number_of_grantees_with_difficulty_in_walking'].required = False
        self.fields['number_of_grantees_with_difficulty_in_remembering'].required = False
        self.fields['number_of_grantees_with_difficulty_in_self_care'].required = False
        self.fields['number_of_grantees_with_difficulty_in_communicating'].required = False

    def clean(self):
        cleaned_data = super(LandTenureSecurityForm, self).clean()
        return cleaned_data

    @classmethod
    def get_template(cls):
        return 'large_labelled_form/large_labelled_form.html'

    class Meta(GenericFormMixin.Meta):
        model = LandTenureSecurity
        fields = [
            "city", "ward", "allocated_land_area",
            "land_description", "land_transfer_status",
            "is_mou_signed", "date_of_mou_sign", "total_number_of_grantees",
            "number_of_sweepers_and_cleaners",
            "number_of_existing_dwellers",
            "number_of_general_beneficiaries",
            "number_of_grantees_with_disability",
            "number_of_grantees_with_difficulty_in_seeing",
            "number_of_grantees_with_difficulty_in_hearing",
            "number_of_grantees_with_difficulty_in_walking",
            "number_of_grantees_with_difficulty_in_remembering",
            "number_of_grantees_with_difficulty_in_self_care",
            "number_of_grantees_with_difficulty_in_communicating"
        ]

        labels = {
            "allocated_land_area": "Area of allocated land (in acre)",
            "land_description": "Description of land",
            "number_of_sweepers_and_cleaners": "Number of Municipality's Sweepers and Cleaners",
            "number_of_existing_dwellers": "Number of Existing Dwellers",
            "number_of_general_beneficiaries": "Number of General Beneficiaries",
            "number_of_grantees_with_disability": "Number of Grantees with disability",
            "number_of_grantees_with_difficulty_in_seeing": "Number of Grantees with difficulty in seeing, even if wearing glasses",
            "number_of_grantees_with_difficulty_in_hearing": "Number of Grantees with difficulty in hearing, even if using a hearing aid",
            "number_of_grantees_with_difficulty_in_walking": "Number of Grantees with difficulty in walking or climbing steps",
            "number_of_grantees_with_difficulty_in_remembering": "Number of Grantees with difficulty in remembering or concentrating",
            "number_of_grantees_with_difficulty_in_self_care": "Number of Grantees with difficulty in self-care such as washing all over or dressing",
            "number_of_grantees_with_difficulty_in_communicating": "Number of Grantees with difficulty in communicating, for example understanding or being understood"
        }

        widgets = {
            'land_description': forms.Textarea
        }

