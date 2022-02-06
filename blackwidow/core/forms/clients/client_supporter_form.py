from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.clients.client_supporter import ClientSupporter

__author__ = 'Ziaul'


class ClientSupporterForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', form_header='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, form_header=form_header, **kwargs)

    class Meta(GenericFormMixin.Meta):
        model = ClientSupporter
        fields = ['name', 'relation', 'telephone']
