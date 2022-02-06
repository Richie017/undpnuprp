from django import forms

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.file.importfileobject import ImportFileObject
from blackwidow.core.models.queue.import_queue import ImportFileQueue
from blackwidow.engine.decorators.utility import get_models_with_decorator
from config.apps import INSTALLED_APPS

__author__ = 'Mahmud'


class ImportFileQueueForm(GenericFormMixin):
    status = forms.ChoiceField(choices=[('FileQueueEnum.SCHEDULED', 'Scheduled')],
                               widget=forms.Select(attrs={'class': 'select2'}))

    def __init__(self, data=None, files=None, **kwargs):
        super().__init__(data=data, files=files, **kwargs)
        self.fields['model'] = forms.ChoiceField(choices=[(a + "." + x, x) for a, x in
                                                          get_models_with_decorator('enable_import', INSTALLED_APPS,
                                                                                    app_name=True)],
                                                 widget=forms.Select(attrs={'class': 'select2'}))
        self.fields['file'] = GenericModelChoiceField(queryset=ImportFileObject.objects.all(),
                                                      widget=forms.Select(attrs={'class': 'select2'}))
        self.fields['parent'] = GenericModelChoiceField(queryset=ImportFileQueue.objects.all(),
                                                        widget=forms.Select(attrs={'class': 'select2'}), required=False)

    class Meta:
        model = ImportFileQueue
        fields = ['file', 'model', 'parent', 'status']
        widgets = {
            'status': forms.Select(attrs={'class': 'select2'})
        }
        labels = {
            'parent': 'Depends on'
        }
