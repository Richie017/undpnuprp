from django import forms
from django.db import transaction
from django.forms.widgets import SelectMultiple

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.fieldmixin.multiple_select_field_mixin import GenericModelMultipleChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.models.descriptors.training_participant import TrainingParticipant
from undp_nuprp.nuprp_admin.models.training.training import Training

__author__ = "Mahbub"


class TrainingForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(TrainingForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['training_location'] = forms.ChoiceField(
            required=True,
            choices=(
                ('', 'Select One'),
                ('City', 'City'),
                ('Headquarters', 'Headquarters')
            ),
            initial=instance.training_location if instance is not None else '',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            )
        )

        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['training_date'] = forms.DateTimeField(
            label='Date of Training',
            input_formats=['%d/%m/%Y %H:%M'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy hh:mm",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y %H:%M'
            ),
        )

        self.fields['has_report'] = forms.CharField(
            label='Is a training report available, if required (Yes/ No)?',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('Yes', 'Yes'),
                    ('No', 'No'),
                )
            )
        )

        self.fields['training_participants'] = GenericModelMultipleChoiceField(
            required=True,
            label='Who were the participants?',
            queryset=TrainingParticipant.objects.all().order_by('date_created'),
            initial=instance.training_participants.all() if instance is not None else None,
            widget=SelectMultiple(
                attrs={
                    'class': 'select2',
                    'multiple': 'multiple'
                }
            ))

    def clean(self):
        cleaned_data = super(TrainingForm, self).clean()
        male_count = cleaned_data['participant_male']
        female_count = cleaned_data['participant_female']
        total_count = cleaned_data['participant_total']
        if male_count + female_count != total_count:
            self.add_error('participant_total', "Invalid count, must be sum of male and female count")

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            super(TrainingForm, self).save(commit=True)
            if self.instance.training_location == 'Headquarters':
                self.instance.city = None
                self.instance.save()
            return self.instance

    @classmethod
    def get_template(cls):
        return 'workshop/create.html'

    class Meta(GenericFormMixin.Meta):
        model = Training
        fields = (
            'title', 'training_location', 'city', 'training_date', 'venue', 'facilitators', 'number_of_pg_attendees',
            'number_of_non_pg_attendees', 'training_participants', 'participant_male', 'participant_female',
            'participant_total', 'duration', 'has_report')

        labels = {
            'facilitators': 'Name and designation of facilitator(s)',
            'duration': 'Duration (Hours)',
            'participant_male': 'Number of Male Participants',
            'participant_female': 'Number of Female Participants',
            'participant_total': 'Number of Total Partcipants',
            'number_of_pg_attendees': 'Number of PG attendees?',
            'number_of_non_pg_attendees': 'Number of Non-PG attendees?',
            'training_participants': 'Who were the participants?'
        }
        widgets = {
            'facilitators': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(TrainingForm, cls).field_groups()
        _group['The organized procedure by which people learn knowledge and/or skill for a definite purpose'] = \
            ['title', 'training_location', 'city', 'training_date', 'venue', 'facilitators', 'number_of_pg_attendees',
             'number_of_non_pg_attendees', 'training_participants', 'participant_male', 'participant_female',
             'participant_total', 'duration', 'has_report']
        return _group
