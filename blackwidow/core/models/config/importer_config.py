from django.db import models

from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity


__author__ = 'Mahmud'


class ImporterConfig(OrganizationDomainEntity):
    columns = models.ManyToManyField(ImporterColumnConfig)
    model = models.CharField(max_length=200)
    starting_row = models.IntegerField(default=1)       # 1 indexed system
    starting_column = models.IntegerField(default=0)    # 0 indexed system
