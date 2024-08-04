from collections import OrderedDict
from datetime import date

from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Ziaul Haque'


@decorate(is_object_context,
          route(route='quantitative-report', group='Target & Progress', module=ModuleEnum.Analysis,
                display_name='Qualitative Report', group_order=6, item_order=3))
class QuantitativeReport(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL, related_name='+')
    year = models.IntegerField(default=1970)
    month = models.IntegerField(default=1)
    submission_date = models.DateField(default=None, null=True)
    attached_file = models.ForeignKey('core.FileObject', null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def get_months(cls):
        return ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                'August', 'September', 'October', 'November', 'December']

    @classmethod
    def get_month_name(cls, month_id, number_base=1):
        return cls.get_months()[month_id - number_base]

    @classmethod
    def map_month_id(cls, month, number_base=1):
        try:
            return cls.get_months().index(month) + number_base
        except:
            return date.today().month

    @property
    def render_reporting_month(self):
        return self.get_month_name(self.month)

    @property
    def render_download_url(self):
        if self.attached_file and self.attached_file.name:
            download_url = '/static_media/uploads/'
            file_name = self.attached_file.name
            _url = download_url + file_name
            _title = '<i class="fa fa-download" aria-hidden="true"></i>click here to download'
            return mark_safe('<a href="' + _url + '" >' + _title + '</a>')
        return "N/A"

    @classmethod
    def table_columns(cls):
        return [
            'render_code', 'city', 'year', 'render_reporting_month', 'date_created:Created On', 'created_by',
            'last_updated:Last Updated On', 'last_updated_by'
        ]

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit]

    def details_config(self):
        details = OrderedDict()
        details['City'] = self.city
        details['Year'] = self.year
        details['Reporting Month'] = self.get_month_name(self.month)
        details['Created By'] = self.created_by
        details['Last Updated By'] = self.last_updated_by
        details['Created On'] = self.render_timestamp(self.date_created)
        details['Last Updated On'] = self.render_timestamp(self.last_updated)
        details['Attached File'] = self.render_download_url
        return details
