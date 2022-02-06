from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig

__author__ = 'ruddra'
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from django.db import models


class ExporterConfig(OrganizationDomainEntity):
    columns = models.ManyToManyField(ExporterColumnConfig)
    model = models.CharField(max_length=200)
    starting_row = models.IntegerField(default=1)       # 1 indexed system
    starting_column = models.IntegerField(default=0)    # 0 indexed system