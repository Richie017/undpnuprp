from datetime import date
from django import forms
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.utils.month_enum import MonthEnum
from undp_nuprp.nuprp_admin.models.citizen_participation_and_community_mobilization.community_mobilization_reporting import \
    CommunityMobilizationReporting
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster

__author__ = 'Shuvro'

year_choices = tuple()
meeting_type_choices = (('', 'Select One'),)

for y in range(2000, 2100):
    year_choices += ((y, str(y)),)

meeting_types = ['Ward Level Consultation Meeting', 'Mass Meeting at Settlement level', 'Courtyard',
                 'Large Group Meeting', 'Primary Group Meeting', 'CDC Meeting', 'Cluster Meeting']

for meeting_type in meeting_types:
    meeting_type_choices += ((meeting_type, meeting_type),)


class CommunityMobilizationReportingForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CommunityMobilizationReportingForm, self).__init__(data=data, files=files, instance=instance,
                                                                 prefix=prefix, **kwargs)

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

        self.fields['ward_number'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Ward'),
            initial=instance.ward_number if instance and instance.pk else None,
            empty_label='Select One',
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'select2-input', 'width': '220',
                'data-depends-on': 'city',
                'data-depends-property': 'parent:id',
                'data-url': reverse(
                    Geography.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
            })
        )

        self.fields['cdc_cluster'] = GenericModelChoiceField(
            required=False,
            queryset=CDCCluster.objects.all(), label='CDC Cluster',
            initial=instance.cdc_cluster if instance and instance.pk else None,
            widget=forms.TextInput(attrs={
                'class': 'select2-input', 'width': '220',
                'data-depends-on': 'city',
                'data-depends-property': 'address:geography:id',
                'data-url': reverse(
                    CDCCluster.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
            }))

        self.fields['cdc'] = GenericModelChoiceField(
            required=False,
            queryset=CDC.objects.all(), label='CDC',
            initial=instance.cdc if instance and instance.pk else None,
            widget=forms.TextInput(attrs={
                'class': 'select2-input', 'width': '220',
                'data-depends-on': 'cdc_cluster',
                'data-depends-property': 'parent:id',
                'data-url': reverse(
                    CDC.get_route_name(ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
            }))

        self.fields['year'] = forms.ChoiceField(
            required=False,
            choices=year_choices,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=date.today().year if self.is_new_instance else instance.year,
        )
        self.fields['month'] = forms.ChoiceField(
            required=False,
            choices=MonthEnum.get_choices(),
            initial=date.today().month if self.is_new_instance else instance.month,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            )
        )

        self.fields['type_of_meeting'] = forms.ChoiceField(
            required=False,
            choices=meeting_type_choices,
            initial=instance.type_of_meeting if not self.is_new_instance else None,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            )
        )

        self.fields['meeting_date'] = forms.DateTimeField(
            required=False,
            label='Meeting date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.meeting_date if instance and instance.pk else None
        )

    class Meta(GenericFormMixin.Meta):
        model = CommunityMobilizationReporting

        fields = (
            'city', 'cdc_cluster', 'cdc', 'ward_number', 'year', 'month', 'type_of_meeting', 'settlement_name',
            'num_of_male_participants', 'num_of_female_participants', 'meeting_date', 'meeting_venue',
            'key_discussion_points', 'key_decision_points')

        widgets = {
            'key_discussion_points': forms.Textarea,
            'key_decision_points': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(CommunityMobilizationReportingForm, cls).field_groups()
        _group['Meeting Details'] = ['city', 'cdc_cluster', 'cdc', 'ward_number', 'year', 'month', 'type_of_meeting',
                                     'settlement_name', 'num_of_male_participants',
                                     'num_of_female_participants', 'meeting_date', 'meeting_venue',
                                     'key_discussion_points', 'key_decision_points']

        return _group

    def save(self, commit=True):
        return super(CommunityMobilizationReportingForm, self).save(commit=commit)

