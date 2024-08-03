import os
from random import choice
from string import ascii_uppercase

from django import forms
from django.db import transaction
from django.utils.text import get_valid_filename

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.file.fileobject import FileObject
from blackwidow.engine.managers.filemanager import FileManager
from blackwidow.engine.widgets.bw_file_input_widget import BWFileInput
from settings import PROJECT_PATH
from settings import STATIC_UPLOAD_ROOT

__author__ = 'ruddra, Sohel'


class FileObjectForm(GenericFormMixin):
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'description'}))
    file = forms.FileField(required=False, widget=BWFileInput)

    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super(FileObjectForm, self).__init__(data=data, files=files, instance=instance, **kwargs)
        self.fields['description'].widget = forms.HiddenInput()
        self.fields['file'].instance = instance.file if instance else None

    def save(self, commit=True):
        with transaction.atomic():
            FileManager.create_dirs(os.path.join(PROJECT_PATH, STATIC_UPLOAD_ROOT))
            file_obj = self.cleaned_data.get('file', None)
            if file_obj:
                file_obj_name = rename_file(file_obj, self.instance)

            is_file_content_updated = False
            if 'file' in self.changed_data:
                is_file_content_updated = True

            instance = super(FileObjectForm, self).save(commit)
            if instance and instance.file:
                file_name = instance.file.name[instance.file.name.rfind(os.sep) + 1:]
                extension = instance.file.name[instance.file.name.rfind('.'):] if instance.file.name is not None else ''
                instance.name = file_obj_name if file_obj else ''
                instance.extension = extension
                instance.path = instance.file.name
                instance.save()
            else:  # in case of clear file,set null to name, extension and path.
                instance.name = None
                instance.extension = None
                instance.path = None

            if is_file_content_updated:
                # set FileObject instance location reference to None, if particular instance file content is
                # updated through mission control
                instance.location = None
            instance.save()
            return instance

    class Meta:
        model = FileObject
        fields = ['file', 'description']


def rename_file(file_obj, instance):
    '''
    :param file_obj: a object of class FileField
    :param instance: an instance of class FileObject
    :return: a valid file name. Here we user  get_valid_filename method as this method used while uploading file by
    django. And it helps to make the filename compatible both in database and uploaded directory
    '''

    if hasattr(file_obj, 'instance'):
        if instance.name != file_obj.instance.name:
            file_obj_name = file_obj.name
            file_obj_name = file_obj_name.replace(",", "").replace(" ", "_")
            if file_obj_name.rfind('/') > -1:
                file_obj_name = file_obj_name[file_obj_name.rfind('/') + 1:]
            f_name = file_obj_name[:file_obj_name.rfind('.')]
            f_extension = file_obj_name[file_obj_name.rfind('.'):]
            root_dir = os.path.join(PROJECT_PATH, STATIC_UPLOAD_ROOT)
            candidate_file_name = os.path.join(root_dir, f_name + "" + f_extension)
            if os.path.isfile(candidate_file_name):
                random_digits = ''.join([choice(ascii_uppercase) for i in range(8)])
                file_obj_name = f_name + '_' + random_digits + "" + f_extension
            if len(f_name) > 32:
                random_digits = ''.join([choice(ascii_uppercase) for i in range(8)])
                file_obj_name = f_name[:31] + "_" + random_digits + "" + f_extension
                file_obj.name = file_obj_name
            instance.file.name = file_obj_name
            instance.save()
            return file_obj_name
        else:
            return get_valid_filename(instance.name)
    else:
        file_obj_name = file_obj.name
        file_obj_name = file_obj_name.replace(",", "").replace(" ", "_")
        if file_obj_name.rfind('/') > -1:
            file_obj_name = file_obj_name[file_obj_name.rfind('/') + 1:]
        f_name = file_obj_name[:file_obj_name.rfind('.')]
        f_extension = file_obj_name[file_obj_name.rfind('.'):]
        root_dir = os.path.join(PROJECT_PATH, STATIC_UPLOAD_ROOT)
        candidate_file_name = os.path.join(root_dir, f_name + "" + f_extension)
        if os.path.isfile(candidate_file_name):
            random_digits = ''.join([choice(ascii_uppercase) for i in range(8)])
            file_obj_name = f_name + '_' + random_digits + "" + f_extension
        if len(f_name) > 32:
            random_digits = ''.join([choice(ascii_uppercase) for i in range(8)])
            file_obj_name = f_name[:31] + "_" + random_digits + "" + f_extension
            file_obj.name = file_obj_name
        instance.file.name = file_obj_name
        instance.save()
        return get_valid_filename(file_obj_name)
