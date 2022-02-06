from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.email.email_template import EmailTemplate

__author__ = 'ruddra'


class EmailTemplateForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', parent_id='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, parent_id=parent_id, **kwargs)
        if not instance:
            self.fields['content_structure'].initial = '<p>Dear [@recipient_users],<br/><br/> This email has been sent to you to inform you that,<br/>[@body]<baddr/><br/>Sincerely,<br/>[@sender],<br/>[@role],<br/><b>Jita</b></p>'

    class Meta(GenericFormMixin.Meta):
        model = EmailTemplate
        fields = ['name', 'content_structure']
        widgets = {
            'content_structure': forms.Textarea(attrs={'class':'richtexteditor'}),
        }
