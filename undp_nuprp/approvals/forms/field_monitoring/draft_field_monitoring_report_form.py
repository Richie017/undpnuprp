from crequest.middleware import CrequestMiddleware
from django import forms

from blackwidow.core.mixins.fieldmixin import GenericModelMultipleChoiceField
from blackwidow.core.models import ConsoleUser
from blackwidow.engine.extensions.async_task import perform_async
from undp_nuprp.approvals.forms.field_monitoring.field_monitoring_report_form import FieldMonitoringReportForm
from undp_nuprp.approvals.models import DraftFieldMonitoringReport
from undp_nuprp.approvals.tasks import perform_draft_field_monitoring_report_post_processing


class DraftFieldMonitoringReportForm(FieldMonitoringReportForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(DraftFieldMonitoringReportForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['email_recipients'] = GenericModelMultipleChoiceField(
            required=False, label='Email Recipient(s)',
            queryset=ConsoleUser.objects.filter(
                role__name__in=['RELU', 'MIS Specialist', 'Admin', 'Coordinator', 'Town Manager', 'MNE Specialist']
            ).order_by('name'),
            widget=forms.SelectMultiple(
                attrs={'class': 'select2', 'multiple': 'multiple'}
            ),
            initial=instance.email_recipients.all() if instance and instance.pk else None
        )

    class Meta(FieldMonitoringReportForm.Meta):
        model = DraftFieldMonitoringReport
        fields = [
            'city', 'ward', 'date', 'name', 'designation', 'mission_objective', 'output', 'report_submitted',
            'followup_date', 'email_recipients'
        ]

    @classmethod
    def field_groups(cls):
        _group = super(DraftFieldMonitoringReportForm, cls).field_groups()
        _group['Basic Details'] = [
            'city', 'ward', 'date', 'name', 'designation', 'mission_objective',
            'output', 'report_submitted', 'followup_date', 'email_recipients'
        ]

        return _group

    def save(self, commit=True):
        if len(self.cleaned_data['ward']) == 1:
            self.instance.ward = "0" + str(self.cleaned_data['ward'])
        self.instance = super(DraftFieldMonitoringReportForm, self).save(commit=commit)
        if self.is_new_instance:
            request_user = CrequestMiddleware.get_request().c_user
            perform_async(
                method=perform_draft_field_monitoring_report_post_processing,
                args=(self.instance, request_user)
            )
        return self.instance
