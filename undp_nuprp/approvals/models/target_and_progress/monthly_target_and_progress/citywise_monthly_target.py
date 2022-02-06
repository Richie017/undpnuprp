from datetime import date

from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.extensions import bw_titleize

__author__ = 'Ziaul Haque'

QuarterIDLowerBase = 13

class CityWiseMonthlyTarget(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL, related_name='+')
    year = models.IntegerField(default=1970)
    month = models.IntegerField(default=1)
    output = models.CharField(max_length=128, blank=True, null=True)
    activity_code = models.CharField(max_length=128, blank=True, null=True)
    activity = models.CharField(max_length=255, blank=True, null=True)
    sub_activity_code = models.CharField(max_length=128, blank=True, null=True)
    sub_activity = models.CharField(max_length=255, blank=True, null=True)
    indicator = models.TextField(blank=True, null=True)
    unit = models.CharField(max_length=255, blank=True, null=True)
    target = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    achieved = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def get_months(cls):
        return ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December']

    @classmethod
    def get_quarters(cls):
        return ['Q1', 'Q2', 'Q3', 'Q4']

    @classmethod
    def get_quarter_range(cls, quarter_id):
        quarters = cls.get_quarters()
        if quarter_id < QuarterIDLowerBase:
            raise ValueError('Quarter ID must be greater than {0}'.format(QuarterIDLowerBase))
        if quarter_id > len(quarters) + QuarterIDLowerBase - 1:
            raise ValueError('Quarter ID must be smaller than {0}'.format(len(quarters) + QuarterIDLowerBase))
        quarter_id -= QuarterIDLowerBase
        _to = (quarter_id + 1) * 3
        return list(range(quarter_id * 3 + 1, _to + 1))

    @classmethod
    def get_quarter_name(cls, quarter_id):
        quarters = cls.get_quarters()
        if quarter_id < QuarterIDLowerBase:
            raise ValueError('Quarter ID must be greater than {0}'.format(QuarterIDLowerBase))
        if quarter_id > len(quarters) + QuarterIDLowerBase - 1:
            raise ValueError('Quarter ID must be smaller than {0}'.format(len(quarters) + QuarterIDLowerBase))
        return quarters[quarter_id - QuarterIDLowerBase]

    @classmethod
    def get_month_name(cls, month_id, number_base=1):
        return cls.get_months()[month_id - number_base]

    @classmethod
    def map_month_id(cls, month, number_base=1):
        try:
            return cls.get_months().index(month) + number_base
        except:
            return date.today().month

    @classmethod
    def write_value_excel(cls, workbook, row_number, column_number, value, **kwargs):
        workbook.cell(row=row_number, column=column_number).value = value

    @classmethod
    def get_page_title(cls):
        return bw_titleize(cls.__name__)
