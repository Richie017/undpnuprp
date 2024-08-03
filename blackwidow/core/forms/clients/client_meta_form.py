from blackwidow.core.forms.files.imagefileobject_form import ImageFileObjectForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.clients.client_meta import ClientMeta

__author__ = 'ruddra'


class ClientMetaForm(GenericFormMixin):

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        kwargs.pop("form_header")
        self.add_child_form("p_photo", ImageFileObjectForm(data=data, files=files, instance=instance.p_photo if instance is not None else None, form_header='Personal Photograph', prefix=prefix + str(len(self.suffix_child_forms)), **kwargs))
        # self.add_child_form("nimage", ImageFileObjectForm(data=data, files=files, instance=instance.nid_image if instance is not None else None, form_header='Photo of National ID Card', prefix=prefix + str(len(self.suffix_child_forms)), **kwargs))
        # self.fields['nid_image'] = ImageFileObjectForm()
        # self.add_child_form("nid_image", ImageFileObjectForm(data=data, files=files, instance=instance.nid_image if instance is not None else None, form_header='Photo of National ID Card', prefix=prefix + str(len(self.suffix_child_forms)), **kwargs))
        # self.fields['date_of_birth']=forms.DateTimeField(input_formats=['%d/%m/%Y'], widget=forms.DateTimeInput(attrs={'data-format':"dd/MM/yyyy", 'class': 'date-time-picker', 'readonly': 'True'}, format='%d/%m/%Y'))
        #self.fields['nid_image'].label = "NID Photograph"
    class Meta(GenericFormMixin.Meta):
        model = ClientMeta
        # fields = ['gender','national_id','date_of_birth']
        # labels = {
        #     'national_id':'National ID',
        #     'gender': 'Gender',
        # }