from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'ruddra'


class ConfigurableType(OrganizationDomainEntity):
    context = models.CharField(max_length=255, null=True)
    key = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=8000, null=True)
    short_name = models.CharField(max_length=200, default='')
    short_code = models.CharField(max_length=200, default='')

    def clean(self):
        if not self.type:
            self.type = self.__class__.__name__

    @classmethod
    def table_columns(cls):
        return "code", "name", "short_name", "last_updated"

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)
        self.context = ''
        self.key = ''

    def __str__(self):
        return self.name

    def to_model_data(self):
        model_data = super(ConfigurableType, self).to_model_data()
        model_data['id'] = self.pk
        model_data['name'] = self.name
        model_data['parent'] = self.parent.pk if self.parent is not None else None
        return model_data

    class Meta:
        abstract = True
