from datetime import date, datetime

from django import forms
from django.db import models
from django.db.models.aggregates import Sum, Count, Max
from django.forms.forms import Form

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_disbursement import SEFGrantDisbursement
from undp_nuprp.reports.utils.thousand_separator import thousand_separator

__author__ = 'Md Shaheen Alam'


class SEFGrantee(OrganizationDomainEntity):
    pg_member = models.ForeignKey('nuprp_admin.PrimaryGroupMember', null=True, on_delete=models.SET_NULL)
    pg_member_assigned_code = models.CharField(max_length=255, blank=True, null=True)
    pg_member_name = models.CharField(max_length=255, blank=True, null=True)
    ward = models.CharField(null=True, blank=True, max_length=20)
    contact_number = models.CharField(max_length=255, blank=True, null=True, default=None)
    age = models.IntegerField(null=True)
    gender = models.CharField(max_length=128, blank=True, null=True)
    grantee_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    relation_with_pg_member = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.CharField(max_length=300, blank=True, null=True)
    address = models.ForeignKey('core.ContactAddress', null=True)
    has_disability = models.CharField(max_length=3, blank=True, null=True)
    has_disability_family = models.CharField(max_length=3, blank=True, null=True)
    difficulty_in_seeing = models.CharField(max_length=128, blank=True, null=True)
    difficulty_in_hearing = models.CharField(max_length=128, blank=True, null=True)
    difficulty_in_walking = models.CharField(max_length=128, blank=True, null=True)
    difficulty_in_remembering = models.CharField(max_length=128, blank=True, null=True)
    difficulty_in_self_care = models.CharField(max_length=128, blank=True, null=True)
    difficulty_in_communicating = models.CharField(max_length=128, blank=True, null=True)
    grantee_status = models.CharField(max_length=20, blank=True, null=True)
    sef_grant_disbursement = models.OneToOneField(SEFGrantDisbursement, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True
        app_label = 'approvals'

    def save(self, *args, organization=None, **kwargs):
        super(SEFGrantee, self).save(*args, organization=organization, **kwargs)
        if not self.ward and self.pg_member_assigned_code:
            self.ward = self.pg_member_assigned_code[3:5] if len(self.pg_member_assigned_code) > 4 else ""
            if len(self.ward) == 1:
                self.ward = "0" + str(self.ward)
            self.save(*args, organization=organization, **kwargs)

    @property
    def render_contact_number(self):
        return self.contact_number if self.contact_number else (
            self.sef_grant_disbursement.account_number
            if self.sef_grant_disbursement and self.sef_grant_disbursement.account_number else "N/A")

    @property
    def render_PG_member_ID(self):
        return self.pg_member.assigned_code \
            if self.pg_member and self.pg_member.assigned_code else self.pg_member_assigned_code

    @property
    def render_pg_member_name(self):
        return self.pg_member_name if self.pg_member_name else "N/A"

    @classmethod
    def search_PG_member_ID(cls, queryset, value):
        return queryset.filter(pg_member__assigned_code__icontains=value)

    @classmethod
    def order_by_PG_member_ID(cls):
        return ['pg_member__assigned_code']

    @property
    def render_CDC(self):
        if self.pg_member and self.pg_member.assigned_to and self.pg_member.assigned_to.parent:
            return self.pg_member.assigned_to.parent
        return "N/A"

    @property
    def render_CDC_name(self):
        if self.pg_member and self.pg_member.assigned_to and self.pg_member.assigned_to.parent:
            return self.pg_member.assigned_to.parent.name
        return "N/A"

    @property
    def render_CDC_ID(self):
        if self.pg_member and self.pg_member.assigned_to and self.pg_member.assigned_to.parent:
            return self.pg_member.assigned_to.parent.assigned_code
        return "N/A"

    @property
    def render_city_corporation(self):
        if self.pg_member and self.pg_member.assigned_to:
            return self.pg_member.assigned_to.parent.address.geography.parent.name
        else:
            return 'N/A'

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(
            pg_member__assigned_to__parent__address__geography__parent__name__icontains=value)

    @property
    def render_total_installment(self):
        if self.sef_grant_disbursement:
            total_installment = self.sef_grant_disbursement.instalments.aggregate(total_installment_value=Sum('value'))
            return thousand_separator(total_installment['total_installment_value']) if total_installment else 0
        return 0

    @property
    def render_grant_disbursement_year(self):
        if self.sef_grant_disbursement and self.sef_grant_disbursement.grant_disbursement_year:
            return self.sef_grant_disbursement.grant_disbursement_year
        return "N/A"
    @property
    def render_grant_receiving_year(self):
        if self.sef_grant_disbursement and self.sef_grant_disbursement.grant_receiving_year:
            return self.sef_grant_disbursement.grant_receiving_year
        return "N/A"
    @property
    def render_registration_year(self):
        if self.sef_grant_disbursement and self.sef_grant_disbursement.registration_year:
            return self.sef_grant_disbursement.registration_year
        return "N/A"
    @property
    def render_ward_poverty_index(self):
        if self.sef_grant_disbursement and self.sef_grant_disbursement.ward_poverty_index:
            return self.sef_grant_disbursement.ward_poverty_index
        return "N/A"
    @property
    def render_mpi(self):
        if self.sef_grant_disbursement and self.sef_grant_disbursement.mpi:
            return self.sef_grant_disbursement.mpi
        return "N/A"

    @classmethod
    def order_by_grant_disbursement_year(cls):
        return ['sef_grant_disbursement__grant_disbursement_year']

    @classmethod
    def search_grant_disbursement_year(cls, queryset, value):
        return queryset.filter(sef_grant_disbursement__grant_disbursement_year=value)

    @classmethod
    def table_columns(cls):
        return (
            "render_contact_number", "age", "gender", "has_disability","has_disability_family"
        )

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.AdvancedExport]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import"

    @property
    def tabs_config(self):
        if self.sef_grant_disbursement:
            return [
                TabView(
                    title='Instalment(s)',
                    access_key='instalments',
                    route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                    relation_type=ModelRelationType.NORMAL,
                    related_model='approvals.SEFGrantInstalment',
                    property=self.sef_grant_disbursement.instalments,
                )
            ]
        return [

        ]

    @classmethod
    def get_export_order_by(cls):
        return '-last_updated'

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):
        """
        this method is used to format the excel file at the beginning of the export
        :param workbook: the workbook instance to work on
        :param columns: exported column configs
        :param row_number: beginning row at which the cursor is on
        :param query_set: the queryset for exportable objects
        :param kwargs: extra params
        :return: tuple of (workbook, row_number): these are updated workbook and row_number after the initiatialization
        """
        column = 1
        for c in columns:
            workbook.cell(row=row_number, column=column).value = c.column_name
            column += 1

        for _col_name in cls.export_tab_columns():
            workbook.cell(row=row_number, column=column).value = bw_titleize(_col_name)
            column += 1

        return workbook, row_number

    @classmethod
    def export_tab_columns(cls):
        max_no_installment = cls.objects.using(BWDatabaseRouter.get_export_database_name()).annotate(
            num_of_installments=Count('sef_grant_disbursement__instalments')).aggregate(
            Max('num_of_installments'))
        max_no_installment = max_no_installment['num_of_installments__max'] if max_no_installment else 0

        return ['Installment {0}'.format(i + 1) for i in range(max_no_installment)]

    @classmethod
    def export_tab_items(cls, self):
        if self.sef_grant_disbursement:
            items = list(self.sef_grant_disbursement.instalments.using(
                BWDatabaseRouter.get_export_database_name()
            ).values_list('value', flat=True))
            return list(map(lambda x: thousand_separator(x), items))
        return []

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
        queryset = super(SEFGrantee, cls).apply_search_filter(search_params=search_params, queryset=queryset, **kwargs)

        if search_params.get('city', None):
            city_param = search_params.get('city')
            city_ids = [int(x) for x in city_param.split(',')]
            queryset = queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__id__in=city_ids
            )

        if search_params.get('year', None):
            target_year = int(search_params.get('year'))
            # _from_datetime = datetime(year=target_year, month=1, day=1).timestamp() * 1000
            # _to_datetime = datetime(year=target_year + 1, month=1, day=1).timestamp() * 1000 - 1
            # queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)
            queryset = queryset.filter(sef_grant_disbursement__grant_disbursement_year=target_year)

        return queryset
