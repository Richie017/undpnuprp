from django import forms
from django.db import transaction

from blackwidow.core.forms.files.fileobject_form import FileObjectForm
from blackwidow.core.mixins.formmixin import GenericFormMixin
from blackwidow.filemanager.models.tags import DocumentTag
from blackwidow.filemanager.models.uploadfileobject import UploadFileObject

__author__ = 'Ziaul Haque'

CATEGORY_CHOICES = (
    ('', 'Select One'),
    ('Training Guideline', 'Training Guideline'),
    ('Donor Progress Report', 'Donor Progress Report'),
    ('Programme Presentation', 'Programme Presentation'),
    ('Programme Policy', 'Programme Policy'),
    ('Poster', 'Poster'),
    ('City Strategy', 'City Strategy'),
    ('Pamphlet', 'Pamphlet'),
    ('Guidance Note', 'Guidance Note'),
    ('Register', 'Register'),
    ('Workshop Report', 'Workshop Report'),
    ('Assessment Report', 'Assessment Report'),
    ('Think Piece', 'Think Piece'),
    ('Lessons Learned', 'Lessons Learned'),
    ('NUPRP Project Document', 'NUPRP Project Document'),
    ('Map', 'Map'),
    ('Press Release', 'Press Release'),
    ('Brief', 'Brief'),
    ('Policy Brief', 'Policy Brief'),
)


class UploadFileObjectForm(GenericFormMixin):
    title = forms.CharField(
        label='Name of document',
        max_length=8000, required=True,
        widget=forms.TextInput(attrs={'required': 'required'})
    )
    author = forms.CharField(label='Author', max_length=254, required=False)
    category = forms.CharField(label='Type of document', max_length=254, required=False)
    version = forms.CharField(max_length=254, required=False)
    keywords = forms.CharField(
        label='Tags/ keywords', max_length=500, required=False,
        widget=forms.TextInput(attrs={'class': 'enable_tagging'})
    )

    @classmethod
    def get_template(cls):
        return "_file_upload_partial.html"

    def __init__(self, data=None, files=None, instance=None, **kwargs):
        super(UploadFileObjectForm, self).__init__(data=data, files=files, instance=instance, **kwargs)
        self.fields['category'] = forms.CharField(
            label='Type of document',
            required=False,
            widget=forms.Select(
                attrs={'class': 'select2'},
                choices=CATEGORY_CHOICES
            )
        )

        self.fields['published_date'] = forms.DateTimeField(
            label='Published Date',
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True',
                    'required': 'required'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.published_date if instance else None
        )

    class Meta:
        model = UploadFileObject
        fields = ['title', 'author', 'category', 'published_date', 'keywords', 'version']

    def save(self, commit=True):
        with transaction.atomic():
            _keywords = self.cleaned_data['keywords']
            self.instance = super(UploadFileObjectForm, self).save(commit=commit)
            _file_object_form = FileObjectForm(data=self.data, files=self.files)
            if _file_object_form.is_valid():
                _file_object = _file_object_form.save()  # saving actual fileobject
                _original_file_name = _file_object.file.name
                _file_name = _file_object.file.name[:_file_object.file.name.rfind('.')]
                self.instance.fileobject = _file_object
                if self.instance.title is None:
                    self.instance.title = _file_name
                self.instance.original_name = _original_file_name
                self.instance.save()

            # saving document tags individually and link to uploadfileobject
            _tag_names = _keywords.split()
            for _tag in _tag_names:
                _tag_object, created = DocumentTag.objects.get_or_create(name=_tag)
                self.instance.tags.add(_tag_object)
            return self.instance
