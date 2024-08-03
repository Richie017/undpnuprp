from collections import OrderedDict
from datetime import date, datetime

from django import forms
from django.db import models
from django.forms import Form

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Mahbub'


@decorate(is_object_context,
          route(route='land-tenure-security', group='Housing Finance', module=ModuleEnum.Analysis,
                display_name='Low-Cost Housing Fund', group_order=4, item_order=1))
class LandTenureSecurity(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', related_name="land_securities_by_city", null=True)
    ward = models.ForeignKey('core.Geography', related_name="land_securities_by_ward", null=True)
    allocated_land_area = models.DecimalField(max_digits=20, decimal_places=2, null=True)
    land_description = models.CharField(max_length=128, blank=True)
    land_transfer_status = models.CharField(max_length=3, blank=True, null=True)
    is_mou_signed = models.CharField(max_length=3, blank=True, null=True)
    date_of_mou_sign = models.DateTimeField(default=None, null=True)
    total_number_of_grantees = models.IntegerField(null=True)
    number_of_sweepers_and_cleaners = models.IntegerField(null=True)
    number_of_existing_dwellers = models.IntegerField(null=True)
    number_of_general_beneficiaries = models.IntegerField(null=True)
    number_of_grantees_with_disability = models.IntegerField(null=True)
    number_of_grantees_with_difficulty_in_seeing = models.IntegerField(null=True)
    number_of_grantees_with_difficulty_in_hearing = models.IntegerField(null=True)
    number_of_grantees_with_difficulty_in_walking = models.IntegerField(null=True)
    number_of_grantees_with_difficulty_in_remembering = models.IntegerField(null=True)
    number_of_grantees_with_difficulty_in_self_care = models.IntegerField(null=True)
    number_of_grantees_with_difficulty_in_communicating = models.IntegerField(null=True)

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def export_file_columns(cls):
        return [
            "city", "ward:Ward Number", "allocated_land_area:Area of allocated land (in acre)",
            "land_description:Description of land", "land_transfer_status:Land transfer status",
            "is_mou_signed:MoU signed", "date_of_mou_sign:Date of MoU sign", "total_number_of_grantees",
            "number_of_sweepers_and_cleaners:Number of Municipality's Sweepers and Cleaners",
            "number_of_existing_dwellers:Number of Existing Dwellers",
            "number_of_general_beneficiaries:Number of General Beneficiaries",
            "number_of_grantees_with_disability:Number of Grantees with disability",
            "number_of_grantees_with_difficulty_in_seeing:Number of Grantees with difficulty in seeing, even if wearing glasses",
            "number_of_grantees_with_difficulty_in_hearing:Number of Grantees with difficulty in hearing, even if using a hearing aid",
            "number_of_grantees_with_difficulty_in_walking:Number of Grantees with difficulty in walking or climbing steps",
            "number_of_grantees_with_difficulty_in_remembering:Number of Grantees with difficulty in remembering or concentrating",
            "number_of_grantees_with_difficulty_in_self_care:Number of Grantees with difficulty in self-care such as washing all over or dressing",
            "number_of_grantees_with_difficulty_in_communicating:Number of Grantees with difficulty in communicating, for example understanding or being understood"
        ]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"

    @classmethod
    def table_columns(cls):
        return [
            'code', 'city', 'ward:Ward Number', 'allocated_land_area:Area of allocated land (in acre)',
            'land_transfer_status', 'is_mou_signed:MoU signed', 'date_of_mou_sign:Date of MoU sign',
            'created_by', 'date_created:Created On', 'last_updated'
        ]

    @property
    def details_config(self):
        d = OrderedDict()

        investee = OrderedDict()
        investee['Code'] = self.code
        investee['City'] = self.city if self.city else "N/A"
        investee['Ward Number'] = self.ward if self.ward else "N/A"
        investee['Area of allocated land (in acre)'] = self.allocated_land_area if self.allocated_land_area else "N/A"
        investee['Description of land'] = self.land_description if self.land_description else "N/A"
        investee['Land transfer status'] = self.land_transfer_status if self.land_transfer_status else "N/A"
        investee['MoU signed'] = self.is_mou_signed if self.is_mou_signed else "N/A"
        investee['Date of MoU sign'] = self.date_of_mou_sign if self.date_of_mou_sign else "N/A"
        investee['Total number of Grantees'] = self.total_number_of_grantees if self.total_number_of_grantees else "N/A"
        investee[
            "Number of Municipality's Sweepers and Cleaners"] = self.number_of_sweepers_and_cleaners if self.number_of_sweepers_and_cleaners else "N/A"
        investee[
            "Number of Existing Dwellers"] = self.number_of_existing_dwellers if self.number_of_existing_dwellers else "N/A"
        investee[
            "Number of General Beneficiaries"] = self.number_of_general_beneficiaries if self.number_of_general_beneficiaries else "N/A"
        investee[
            "Number of Grantees with disability"] = self.number_of_grantees_with_disability if self.number_of_grantees_with_disability else "N/A"
        investee[
            "Number of Grantees with difficulty in seeing, even if wearing glasses"] = self.number_of_grantees_with_difficulty_in_seeing if self.number_of_grantees_with_difficulty_in_seeing else "N/A"
        investee[
            "Number of Grantees with difficulty in hearing, even if using a hearing aid"] = self.number_of_grantees_with_difficulty_in_hearing if self.number_of_grantees_with_difficulty_in_hearing else "N/A"
        investee[
            "Number of Grantees with difficulty in walking or climbing steps"] = self.number_of_grantees_with_difficulty_in_walking if self.number_of_grantees_with_difficulty_in_walking else "N/A"
        investee[
            "Number of Grantees with difficulty in remembering or concentrating"] = self.number_of_grantees_with_difficulty_in_remembering if self.number_of_grantees_with_difficulty_in_remembering else "N/A"
        investee[
            "Number of Grantees with difficulty in self-care such as washing all over or dressing"] = self.number_of_grantees_with_difficulty_in_self_care if self.number_of_grantees_with_difficulty_in_self_care else "N/A"
        investee[
            "Number of Grantees with difficulty in communicating, for example understanding or being understood"] = self.number_of_grantees_with_difficulty_in_communicating if self.number_of_grantees_with_difficulty_in_communicating else "N/A"

        d['Basic Information'] = investee

        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by
        audit_info['created_on'] = self.render_timestamp(self.date_created)
        d["Audit Information"] = audit_info

        return d

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedExport
        ]

    @classmethod
    def get_export_dependant_fields(cls):
        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                today = date.today()
                year_choices = tuple()
                for y in range(2000, 2100):
                    year_choices += ((y, str(y)),)

                self.fields['city'] = \
                    GenericModelChoiceField(
                        queryset=Geography.objects.using(
                            BWDatabaseRouter.get_export_database_name()
                        ).filter(level__name='Pourashava/City Corporation'),
                        label='Select City',
                        required=False,
                        widget=forms.Select(
                            attrs={
                                'class': 'select2 kpi-filter',
                                'width': '220',
                                'data-kpi-filter-role': 'city'
                            }
                        )
                    )

                self.fields['year'] = forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )

        return AdvancedExportDependentForm

    @classmethod
    def apply_search_filter(cls, search_params=None, queryset=None, **kwargs):
        queryset = super(LandTenureSecurity, cls).apply_search_filter(search_params=search_params,
                                                                      queryset=queryset, **kwargs)

        if search_params.get('city', None):
            try:
                city_param = search_params.get('city')
                city_name = Geography.objects.get(id=city_param).name
                queryset = queryset.filter(assigned_city=city_name)
                # print(city_name)
                # print(len(queryset))
            except Exception as exc:
                print(exc)

        if search_params.get('year', None):
            target_year = int(search_params.get('year'))
            _from_datetime = datetime(year=target_year, month=1, day=1, hour=1, minute=0, second=0).timestamp() * 1000
            _to_datetime = datetime(year=target_year + 1, month=1, day=1, hour=23, minute=59,
                                    second=59).timestamp() * 1000
            queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        return queryset
