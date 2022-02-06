import os

from django import forms
from django.db import transaction

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.file.apkfileobject import ApplicationFileObject
from blackwidow.engine.managers.filemanager import FileManager
from settings import APK_UPLOAD_ROOT
from settings import PROJECT_PATH


__author__ = 'zia ahmed'


class ApplicationFileObjectForm(GenericFormMixin):
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'description'}))
    file = forms.FileField(required=True)

    def save(self, commit=True):
        with transaction.atomic():
            FileManager.create_dirs(os.path.join(PROJECT_PATH, APK_UPLOAD_ROOT))
            instance = super().save(commit)
            if instance and instance.file:
                instance.name = instance.file.name[instance.file.name.rfind(os.sep) + 1:]
                instance.extension = instance.name[instance.file.name.rfind('.'):] if instance.file.name is not None else ''
                instance.path = instance.file.name
                instance.save()
            return instance

    class Meta:
        model = ApplicationFileObject
        fields = ['file', 'description']
