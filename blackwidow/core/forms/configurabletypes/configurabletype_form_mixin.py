from django.db import transaction

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin

__author__ = 'Mahmud'


class ConfigurableTypeFormMixin(GenericFormMixin):

    def save(self, commit=True):
        with transaction.atomic():
            self.instance.context = self.instance.__class__.__name__
            return super().save(commit)

    class Meta:
        fields = ['name', 'short_name']
