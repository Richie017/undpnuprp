from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.location import Location

__author__ = 'mahmudul'


class LocationForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super().__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

    class Meta:
        model = Location
        fields = ['latitude', 'longitude']
