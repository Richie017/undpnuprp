from blackwidow.core.forms.files.fileobject_form import FileObjectForm
from blackwidow.core.models.file.xmlFileObject import XmlFileObject

__author__ = 'ruddra'


class XMLFileObjectForm(FileObjectForm):

    class Meta:
        model = XmlFileObject
        fields = ['file', 'description']
