from django import forms

from blackwidow.core.forms.files.fileobject_form import FileObjectForm
from blackwidow.core.models.file.importfileobject import ImportFileObject


__author__ = 'ruddra'


class ImportFileObjectForm(FileObjectForm):
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'description'}))

    class Meta:
        model = ImportFileObject
        fields = ['file', 'description']
