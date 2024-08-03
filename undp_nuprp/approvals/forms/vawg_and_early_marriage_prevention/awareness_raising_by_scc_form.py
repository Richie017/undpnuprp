from django import forms
from django.urls.base import reverse

from blackwidow.core.forms.files.fileobject_form import FileObjectForm
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.vawg_and_early_marriage_prevention.awareness_raising_by_scc import \
    AwarenessRaisingBySCC

__author__ = 'Shuvro'

activities = (
    ('', 'Select One'),
    ('Cultural campaign against GBV and EFM', 'Cultural campaign against GBV and EFM'),
    ('Day Observation: International Women’s Day (IWD)', 'Day Observation: International Women’s Day (IWD)'),
    ('Day Observation: 16 Days of Activism against Gender-Based Violence (16 DoA)',
     'Day Observation: 16 Days of Activism against Gender-Based Violence (16 DoA)'),
    ('Others (Specify)', 'Others (Specify)')
)


class AwarenessRaisingBySCCForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(AwarenessRaisingBySCCForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                        **kwargs)

        self.fields['campaign_date'] = forms.DateTimeField(
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
            initial=instance.campaign_date if instance and instance.pk else None
        )

        self.fields['campaign_location_city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
            initial=instance.campaign_location_city if instance and instance.pk else None,
            label='Campaign city',
            empty_label='Select One',
            required=False,
            widget=forms.Select(
                attrs={
                    'class': 'select2',
                    'width': '220',
                }
            )
        )

        self.fields['campaign_location_ward'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Ward'),
            label='Campaign location (ward)',
            initial=instance.campaign_location_ward if instance and instance.pk else None,
            empty_label='Select One',
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'select2-input', 'width': '220',
                'data-depends-on': 'campaign_location_city',
                'data-depends-property': 'parent:id',
                'data-url': reverse(
                    Geography.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
            })
        )

        self.fields['activity_name'] = forms.ChoiceField(
            label='Name of activity',
            required=False,
            choices=activities,
            widget=forms.Select(
                attrs={'class': 'select2'}
            ),
            initial=instance.activity_name if instance and instance.pk else None
        )

        self.fields['campaign_key_messages'].required = False
        self.fields['name_of_usage_method'].required = False

        self.fields['number_of_female_attending'].required = False
        self.fields['number_of_male_attending'].required = False
        self.fields['number_of_disabled_male_attending'].required = False
        self.fields['number_of_disabled_female_attending'].required = False
        self.fields['number_of_transgender_attending'].required = False
        self.fields['number_of_lgi_member_attending'].required = False

        kwargs.update({
            'prefix': prefix + '-attachment'
        })

        self.add_child_form(
            "attachment", FileObjectForm(
                data=data, files=files,
                instance=instance.attachment if instance and instance.attachment else None,
                allow_login=True, form_header='Attachment', **kwargs
            )
        )

    class Meta:
        model = AwarenessRaisingBySCC
        fields = ('campaign_date', 'activity_name', 'please_specify', 'campaign_location_city',
                  'campaign_location_ward',
                  'number_of_female_attending', 'number_of_male_attending', 'number_of_disabled_male_attending',
                  'number_of_disabled_female_attending', 'number_of_transgender_attending',
                  'number_of_lgi_member_attending', 'campaign_key_messages', 'name_of_usage_method'
                  )

        widgets = {
            'campaign_key_messages': forms.Textarea(),
            'name_of_usage_method': forms.Textarea()
        }

        labels = {
            'number_of_lgi_member_attending': 'Number of LGI member attending',
            'campaign_key_messages': 'What were the key messages?',
            'name_of_usage_method': 'What method was used?'
        }
