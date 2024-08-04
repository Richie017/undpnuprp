from collections import OrderedDict
from datetime import date, datetime

from django import forms
from django.db import models
from django.forms.forms import Form

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.descriptors.training_participant import TrainingParticipant

__author__ = 'Mahbub'


@decorate(is_object_context, route(route='workshop', group='Capacity Building', module=ModuleEnum.Analysis,
                                   display_name='Workshops', group_order=7, item_order=2)
          )
class Workshop(OrganizationDomainEntity):
    training_title = models.CharField(max_length=255, blank=True)
    workshop_date = models.DateTimeField(default=None, null=True)
    training_location = models.CharField(max_length=128, blank=True)
    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)
    venue = models.CharField(max_length=255, blank=True)
    facilitators = models.CharField(max_length=2048, blank=True)
    participant_male = models.IntegerField(default=0)
    participant_female = models.IntegerField(default=0)
    participant_total = models.IntegerField(default=0)
    duration = models.CharField(max_length=20, blank=True)
    has_report = models.CharField(max_length=20, blank=True)
    number_of_pg_attendees = models.IntegerField(default=0)
    number_of_non_pg_attendees = models.IntegerField(default=0)
    training_participants = models.ManyToManyField(TrainingParticipant)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"

    @property
    def render_city(self):
        return self.city if self.city else 'N/A'

    @property
    def render_training_participants(self):
        participants = self.training_participants.values_list('name', flat=True)
        return ','.join(participants) if len(participants) > 0 else 'N/A'

    @classmethod
    def table_columns(cls):
        return 'code', 'training_title:Workshop title', 'training_location:Workshop location', 'render_city', \
               'created_by', 'last_updated'

    @property
    def details_config(self):
        d = OrderedDict()
        d['Date of Workshop'] = self.workshop_date
        d['Workshop title'] = self.training_title
        d['Workshop location'] = self.training_location
        d['City'] = self.render_city
        d['Name and designation of facilitator(s)'] = self.facilitators
        d['Venue'] = self.venue
        d['Number of PG attendees?'] = self.number_of_pg_attendees
        d['Number of Non-PG attendees?'] = self.number_of_non_pg_attendees
        d['Who were the participants?'] = self.render_training_participants
        d['Number of Male Participants'] = self.participant_male
        d['Number of Female Participants'] = self.participant_female
        d['Number of Total Participants'] = self.participant_total
        d['Duration'] = self.duration + " hours"
        d['Is a workshop report available?'] = self.has_report
        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by
        audit_info['created_on'] = self.render_timestamp(self.date_created)
        d["Audit Information"] = audit_info

        return d

    @classmethod
    def export_file_columns(cls):
        return [
            "workshop_date", "training_title:Workshop title", "training_location:Workshop location", "render_city",
            "facilitators", "venue", "number_of_pg_attendees:Number of PG attendees?",
            "number_of_non_pg_attendees:Number of Non-PG attendees?",
            "render_training_participants:Who were the participants?", "participant_male", "participant_female",
            "participant_total", "duration", "date_created:Created on"
        ]

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedExport
        ]

    @classmethod
    def get_export_dependant_fields(cls):
        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                today = date.today()
                year_choices = tuple()
                for y in range(2000, 2100):
                    year_choices += ((y, str(y)),)

                self.fields['city'] = \
                    GenericModelChoiceField(
                        queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
                        label='Select City',
                        required=False,
                        widget=forms.Select(
                            attrs={
                                'class': 'select2 kpi-filter',
                                'width': '220',
                                'data-kpi-filter-role': 'city'
                            }
                        )
                    )

                self.fields['year'] = forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )

        return AdvancedExportDependentForm

    @classmethod
    def apply_search_filter(cls, search_params=None, queryset=None, **kwargs):
        queryset = super(Workshop, cls).apply_search_filter(search_params=search_params, queryset=queryset, **kwargs)

        if search_params.get('year', None):
            target_year = int(search_params.get('year'))
            _from_datetime = datetime(year=target_year, month=1, day=1).timestamp() * 1000
            _to_datetime = datetime(year=target_year + 1, month=1, day=1).timestamp() * 1000 - 1
            queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        return queryset
