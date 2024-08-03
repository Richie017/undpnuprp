from django import forms
from django.urls import reverse

from blackwidow.core.forms import FileObjectForm
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography, FileObject
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.urban_governance_and_planning.meeting import Meeting

__author__ = "Ziaul Haque"

Yes_No_Choices = [
    ('', 'Select One'),
    ('Yes', 'Yes'),
    ('No', 'No'),
]

MeetingChoices = [
    ('', 'Select One'),
    ('Project Implementation Committee', 'Project Implementation Committee'),
    ('Streeting Committee', 'Streeting Committee'),
    ('Ward Committee', 'Ward Committee'),
    ('Standing Committee', 'Standing Committee'),
    ('Town Level Coordination Committee (TLCC)', 'Town Level Coordination Committee (TLCC)'),
]

StandingCommitteeChoices = [
    ('', 'Select One'),
    ('Standing committee on Disaster management', 'Standing committee on Disaster management'),
    ('Standing committee on Woman and Children', 'Standing committee on Woman and Children'),
    ('Standing committee on Poverty reduction and slum development',
     'Standing committee on Poverty reduction and slum development'),
]


class MeetingAttachmentForm(FileObjectForm):
    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super(MeetingAttachmentForm, self).__init__(data=data, files=files, instance=instance, **kwargs)
        self.fields['description'] = forms.CharField(
            label='Please Upload Minutes of the meeting (With the meeting title)',
            required=False, widget=forms.Textarea()
        )
        self.fields['file'].label = "Attachment"

    class Meta:
        model = FileObject
        fields = ['description', 'file',]


class MeetingForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(MeetingForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City', empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )
        _message = "<ol><li>TLCC and Ward Committee are for only 08 Pouroshova.</li>"
        _message += "<li>PIC and Ward Committee are for Ward level.</li>"
        _message += "<li>Streeting Committee, Standing Committee and TLCC are only for the City level.</li></ol>"

        self.fields['ward_number'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Ward'),
            initial=instance.ward_number if instance and instance.pk else None,
            label='Ward',
            empty_label='Select One',
            required=False,
            widget=forms.TextInput(attrs={
                'class': 'select2-input has-helptext', 'width': '220',
                'data-depends-on': 'city',
                'data-message': _message,
                'data-depends-property': 'parent:id',
                'data-url': reverse(
                    Geography.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
            })
        )

        self.fields['meeting'] = forms.ChoiceField(
            required=False,
            choices=MeetingChoices,
            label='Meeting',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.meeting if instance and instance.pk else None
        )

        self.fields['standing_committee_name'] = forms.ChoiceField(
            required=False,
            choices=StandingCommitteeChoices,
            label='Which Standing Committee?',
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.standing_committee_name if instance and instance.pk else None
        )

        self.fields['meeting_date'] = forms.DateField(
            input_formats=['%d/%m/%Y'],
            required=False, label='Date',
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker'
                },
                format='%d/%m/%Y'
            ),
        )
        self.fields['number_of_total_participants'].widget.attrs['readonly'] = True

        self.add_child_form("attachment", MeetingAttachmentForm(
            data=data, files=files, instance=instance.attachment if instance and instance.pk else None,
            form_header='Meeting Minutes ', **kwargs
        ))

    class Meta:
        model = Meeting
        fields = (
            'city', 'ward_number', 'meeting', 'standing_committee_name', 'number_of_approved_members_of_the_committee',
            'meeting_date', 'number_of_male_participants', 'number_of_female_participants',
            'number_of_disabled_male_participants', 'number_of_disabled_female_participants',
            'number_of_total_participants',
        )
        labels = {
            'number_of_male_participants': 'Male',
            'number_of_female_participants': 'Female',
            'number_of_disabled_male_participants': 'Disable (Male)',
            'number_of_disabled_female_participants': 'Disable (Female)',
            'number_of_total_participants': 'Total',
            # 'remarks': 'Please Upload Minutes of the meeting (With the meeting title)',
        }

    @classmethod
    def field_groups(cls):
        _group = super(MeetingForm, cls).field_groups()

        _group['Participants'] = [
            'number_of_male_participants', 'number_of_female_participants', 'number_of_disabled_male_participants',
            'number_of_disabled_female_participants', 'number_of_total_participants',
        ]

        return _group

    def save(self, commit=True):
        return super(MeetingForm, self).save(commit=commit)
