from django import forms

from blackwidow.core.forms.files.fileobject_form import FileObjectForm
from blackwidow.core.models.file.imagefileobject import ImageFileObject
from blackwidow.engine.exceptions import BWException
from blackwidow.engine.widgets.image_widget import ImageWidget

__author__ = 'ruddra'


class ImageFileObjectForm(FileObjectForm):
    file = \
        forms.ImageField(
            required=False,
            label='Image',
            widget=ImageWidget(
                attrs={
                    'style': 'margin:0 0 0 160px;'
                }
            )
        )

    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super(ImageFileObjectForm, self).__init__(data=data, files=files, instance=instance, **kwargs)
        self.fields['description'] = forms.CharField(label='Caption', required=False, widget=forms.Textarea())

    def is_valid(self):
        valid = super(ImageFileObjectForm, self).is_valid()
        if not valid and 'file' in self.errors:
            raise BWException(self.errors['file'][0])
        return valid

    class Meta:
        model = ImageFileObject
        fields = ['file', 'description']
