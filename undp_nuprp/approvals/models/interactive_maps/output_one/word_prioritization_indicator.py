from django.db import models
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Kaikobud'


class WordPrioritizationIndicator(OrganizationDomainEntity):
    Ward = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)
    poverty_index_score = models.IntegerField(null=True)
    poverty_index_quantile = models.IntegerField(null=True)
    infrastructure_index_score = models.IntegerField(null=True)
    infrastructure_index_quantile = models.IntegerField(null=True)
    livelihood_index_score = models.IntegerField(null=True)
    livelihood_index_quantile = models.IntegerField(null=True)
    land_tenure_and_housing_index_score = models.IntegerField(null=True)
    land_tenure_and_housing_index_quantile = models.IntegerField(null=True)
    total_population = models.IntegerField(null=True)

    class Meta:
        app_label = 'nuprp_admin'
