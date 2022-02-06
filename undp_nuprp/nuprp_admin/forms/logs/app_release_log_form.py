"""
    Created by tareq on 9/1/19
"""

from datetime import datetime

from django import forms
from django.db import transaction

from blackwidow.core.mixins.formmixin import GenericFormMixin
from undp_nuprp.nuprp_admin.enums.app_release_enum import AppReleaseUpdateTypeEnum
from undp_nuprp.nuprp_admin.models.logs.app_release_log import AppReleaseLog

__author__ = 'Tareq'


class AppReleaseLogForm(GenericFormMixin):
    publish_date_field = forms.DateTimeField()

    def __init__(self, data=None, files=None, prefix=None, instance=None, **kwargs):
        super(AppReleaseLogForm, self).__init__(data=data, files=files, prefix=prefix, instance=instance, **kwargs)
        self.fields['publish_date_field'] = forms.DateTimeField(
            label='Publish Date', input_formats=['%d/%m/%Y'], widget=forms.DateTimeInput(
                attrs={'data-format': "dd/MM/yyyy", 'class': 'date-time-picker', 'readonly': 'True'},
                format='%d/%m/%Y'),
            initial=datetime.fromtimestamp(instance.publish_date / 1000) if instance else None)
        self.fields['update_type'] = forms.ChoiceField(
            label="Update Type",
            choices=AppReleaseUpdateTypeEnum.get_choice_list(include_null=False),
            initial=instance.update_type if instance else False,
            widget=forms.Select(attrs={'class': 'select2'})
        )

    def save(self, commit=True):
        with transaction.atomic():
            self.instance.publish_date = (self.cleaned_data['publish_date_field']).timestamp() * 1000
            self.instance = super(AppReleaseLogForm, self).save(commit=commit)
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = AppReleaseLog
        fields = [
            'version_code', 'version_name', 'publish_date_field', 'message', 'translated_message', 'update_type',
            'app_download_url', 'comment'
        ]
        labels = {
            'message': "Message for Mobile Users",
            'app_download_url': "Playstore URL",
        }
