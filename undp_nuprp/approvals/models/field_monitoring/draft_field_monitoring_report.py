from datetime import datetime

from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.safestring import mark_safe

from blackwidow.core.models import EmailTemplate, EmailLog
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, save_audit_log
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from config.email_config import DEFAULT_FROM_EMAIL
from settings import SITE_NAME
from undp_nuprp.approvals.models import FieldMonitoringReport


@decorate(is_object_context, save_audit_log, route(
    route='draft-field-monitoring-report', module=ModuleEnum.Analysis, group='Field Monitoring', group_order=8,
    item_order=1, display_name='Draft Field Monitoring Report'
))
class DraftFieldMonitoringReport(FieldMonitoringReport):
    class Meta:
        app_label = 'approvals'
        proxy = True

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Approve]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit]

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Edit',
                action='edit',
                icon='fbx-rightnav-edit',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit)
            ),
            dict(
                name='Submit',
                action='approve',
                icon='fbx-rightnav-tick',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Approve),
                classes='manage-action all-action confirm-action',
            )
        ]

    @property
    def render_email_recipients(self):
        return ', '.join([str(x) for x in self.email_recipients.all()])

    def details_config(self):
        details = super(DraftFieldMonitoringReport, self).details_config()
        details['Email Recipient(s)'] = self.render_email_recipients
        return details

    def get_report_link(self):
        return mark_safe('<a class="inline-link" href="http://' + SITE_NAME + reverse(
            DraftFieldMonitoringReport.get_route_name(action=ViewActionEnum.Details),
            kwargs={'pk': self.pk}) + '">' + self.name + '</a>')

    def perform_mail_sending(self):
        try:
            for _user in self.email_recipients.all():
                email_template, created = EmailTemplate.objects.get_or_create(
                    name='Draft Field Monitoring Report Submit Mails', organization=self.organization,
                    content_structure='<p>Dear [@recipient_users],<br/><br/>[@body]<br/><br/><br/>[@footer]<br/></p>'
                )

                email_body = 'A draft field monitoring report has been submitted on {0} by {1}. ' \
                             'You can check and approve the report by clicking on this link: {2}.'.format(
                    self.render_timestamp(self.date_created), self.created_by, self.get_report_link()
                )
                email_body += '<br/>Thank you.'

                html_msg = email_template.content_structure \
                    .replace('[@recipient_users]', _user.name) \
                    .replace('[@body]', email_body) \
                    .replace('[@footer]',
                             '<div style="color:gray;font-style:italic;">'
                             'This is an auto generated email by NUPRP Digital Management System '
                             '(Powered by <a href="http://field.buzz">Field Buzz</a>) on %s</div>'
                             % datetime.now().strftime("%d/%m/%Y %I:%M %p"))

                subject = "Updated draft field monitoring report awaiting approval"
                emails = [email_obj.email for email_obj in _user.emails.all()]

                cc = list()

                if emails:
                    mail = EmailMultiAlternatives(
                        subject=subject,
                        body="Draft Field Monitoring Report Submit",
                        from_email=DEFAULT_FROM_EMAIL,
                        to=emails,
                        cc=cc
                    )
                    mail.attach_alternative(html_msg, "text/html")
                    status = mail.send()

                    if status == 1:
                        EmailLog.objects.create(
                            status="Success",
                            message="Email sent successfully!",
                            organization=self.organization,
                            recipient_user=_user
                        )
                    else:
                        EmailLog.objects.create(
                            status="Failed",
                            message="Failed to send email.",
                            organization=self.organization,
                            recipient_user=_user
                        )
        except:
            pass
