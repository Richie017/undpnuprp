from collections import OrderedDict

from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models import FileObject, ImageFileObject, ConsoleUser
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.models.field_monitoring.field_monitoring_folloup import FieldMonitoringFollowup
from undp_nuprp.approvals.models.field_monitoring.field_monitoring_output import FieldMonitoringOutput


class FieldMonitoringReport(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    ward = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    mission_objective = models.TextField(blank=True)
    output = models.ManyToManyField(FieldMonitoringOutput)
    report_submitted = models.CharField(max_length=20, null=True, blank=True)
    attachment = models.OneToOneField(FileObject, null=True, blank=True)
    followup_date = models.DateField(null=True, blank=True)
    key_observations = models.ManyToManyField(FieldMonitoringFollowup)
    report_pictures = models.ManyToManyField(ImageFileObject, related_name='monitoring_reports')
    international_technical_adviser = models.TextField(blank=True)
    project_manager = models.TextField(blank=True)
    monitoring_and_evaluation_specialist = models.TextField(blank=True)
    output_leads = models.TextField(blank=True)
    others = models.TextField(blank=True)
    email_recipients = models.ManyToManyField(ConsoleUser)

    class Meta:
        app_label = 'approvals'

    def approval_level_1_action(self, action=None, *args, **kwargs):
        from undp_nuprp.approvals.models.field_monitoring.submitted_field_monitoring_report import \
            SubmittedFieldMonitoringReport
        if action == "Approved":
            self.type = SubmittedFieldMonitoringReport.__name__
            self.save()

    def approval_level_2_action(self, action=None, *args, **kwargs):
        from undp_nuprp.approvals.models.field_monitoring.approved_field_monitoring_report import \
            ApprovedFieldMonitoringReport
        if action == "Approved":
            self.type = ApprovedFieldMonitoringReport.__name__
            self.save()

    @classmethod
    def table_columns(cls):
        return [
            'code', 'city', 'ward', 'date', 'name', 'designation',
            'created_by', 'date_created', 'last_updated:Last updated on'
        ]

    @property
    def detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_download_url(self):
        return self.attachment if self.attachment else 'N/A'

    @property
    def render_output(self):
        if self.output.count():
            return ','.join(list(self.output.values_list('name', flat=True)))
        else:
            return ''

    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.detail_title
        details['code'] = self.code
        details['city'] = self.city
        details['ward'] = self.ward
        details['date'] = self.date
        details['name'] = self.name
        details['designation'] = self.designation
        details['mission_objective'] = self.mission_objective
        details['output'] = self.render_output
        details['report_submitted'] = self.report_submitted
        details['Attachment'] = self.render_download_url
        details['followup_date'] = self.followup_date
        details['created_by'] = self.created_by
        details['date_created'] = self.render_timestamp(self.date_created)
        details['Last updated on'] = self.render_timestamp(self.last_updated)
        return details

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Key Observation(s)',
                access_key='key_observations',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                property=self.key_observations,
                related_model=FieldMonitoringFollowup,
                queryset=self.key_observations.all(),
            ),
            TabView(
                title='Report Picture(s)',
                access_key='report_pictures',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                property=self.report_pictures,
                related_model=ImageFileObject,
                queryset=self.report_pictures.all(),
            )
        ]
