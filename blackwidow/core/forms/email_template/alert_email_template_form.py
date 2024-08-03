from blackwidow.core.forms.email_template.email_template_form import EmailTemplateForm
from blackwidow.core.models.email.alert_email_template import AlertEmailTemplate

__author__ = 'ruddra'


class AlertEmailTemplateForm(EmailTemplateForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', parent_id='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, parent_id=parent_id, **kwargs)
        if not instance:
            self.fields['content_structure'].initial = '<p>Dear [@recipient_users],<br/><br/> This email has been sent to you to inform you that,<br/>[@body]<baddr/><br/>Sincerely,<br/>[@sender],<br/>[@role],<br/><b>Jita</b></p>'
    class Meta(EmailTemplateForm.Meta):
        model = AlertEmailTemplate
