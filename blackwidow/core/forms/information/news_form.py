from django import forms

from blackwidow.core.forms.information.information_object_form import InformationObjectForm
from blackwidow.core.models.information.news import News

__author__ = 'Tareq'


class NewsForm(InformationObjectForm):
    error_messages = {
        'subject_max_length': "Subject must be less than 200 characters.",
    }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            if len(name) > 200:
                raise forms.ValidationError(
                    self.error_messages['subject_max_length'],
                    code='subject_max_length',
                )
        return name

    class Meta(InformationObjectForm.Meta):
        model = News
