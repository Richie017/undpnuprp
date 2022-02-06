from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

__author__ = 'Ziaul Haque'


class CityWisePMFReportAchievement(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', related_name='+')
    year = models.IntegerField(default=2020)
    month = models.IntegerField(default=1)
    column = models.IntegerField()
    row = models.IntegerField()
    achieved = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    class Meta:
        app_label = 'approvals'
        unique_together = ('city', 'year', 'month', 'column', 'row')
