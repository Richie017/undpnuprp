from collections import OrderedDict
from datetime import date, datetime

from django import forms
from django.db import models
from django.forms import Form

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.route_partial_routes import route, partial_route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models.housing_development_fund.installment_payment import InstallmentPayment

__author__ = 'Mahbub'


@decorate(is_object_context, route(
    route='housing-development-fund', group='Housing Finance', module=ModuleEnum.Analysis,
    display_name='Community Housing Development Fund', group_order=4, item_order=2), partial_route(
    relation='normal', models=[InstallmentPayment]))
class CommunityHousingDevelopmentFund(OrganizationDomainEntity):
    name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(default=None, null=True)
    gender = models.CharField(max_length=128, blank=True, null=True)
    contact_number = models.CharField(max_length=128, blank=True)
    national_id = models.CharField(max_length=200, null=True)
    city = models.ForeignKey('core.Geography', null=True)
    status_of_chdf_city_wise = models.CharField(null=True, blank=True, max_length=20)
    is_pg_member = models.CharField(max_length=20, blank=True, null=True)
    pg_member_number = models.CharField(max_length=255, blank=True)
    pg_member = models.ForeignKey('nuprp_admin.PrimaryGroupMember', null=True, on_delete=models.SET_NULL,
                                  related_name='+')
    borrower_ward = models.CharField(max_length=255, blank=True)

    seeing_difficulty = models.CharField(max_length=128, blank=True)
    hearing_difficulty = models.CharField(max_length=128, blank=True)
    walking_difficulty = models.CharField(max_length=128, blank=True)
    remembering_difficulty = models.CharField(max_length=128, blank=True)
    self_care_difficulty = models.CharField(max_length=128, blank=True)
    communication_difficulty = models.CharField(max_length=128, blank=True)

    approved_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    loan_purpose = models.CharField(max_length=512, null=True, blank=True)
    loan_status = models.CharField(max_length=512, null=True, blank=True)
    loan_tenure = models.IntegerField(null=True, blank=True, default=0)
    loan_start_date = models.DateField(default=None, null=True)
    loan_end_date = models.DateField(default=None, null=True)
    interest_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)
    number_of_households_received_housing_loan = models.IntegerField(null=True, blank=True)

    installments = models.ManyToManyField('approvals.SEFInstallment')
    repayments = models.ManyToManyField('nuprp_admin.InstallmentPayment')

    class Meta:
        app_label = 'nuprp_admin'

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        return button

    @classmethod
    def table_columns(cls):
        return [
            'code', 'city', 'pg_member_number:PG Member ID',
            'name', 'created_by', 'date_created:Created On', 'last_updated'
        ]

    @property
    def details_config(self):
        d = OrderedDict()
        chdf_info = OrderedDict()
        chdf_info['City'] = self.city if self.city else 'N/A'
        chdf_info[
            'Status of CHDF city wise'] = self.status_of_chdf_city_wise if self.status_of_chdf_city_wise else 'N/A'
        d['CHDF information'] = chdf_info

        borrower = OrderedDict()
        borrower['Is PG Member'] = self.is_pg_member if self.is_pg_member else 'N/A'
        borrower['PG Member ID'] = self.pg_member_number if self.pg_member_number else 'N/A'
        borrower['PG Name'] = self.render_primary_group
        borrower['CDC Name'] = self.render_cdc
        borrower['CDC Cluster Name'] = self.render_cdc_cluster
        borrower['Name'] = self.name if self.name else 'N/A'
        borrower['Date of Birth'] = self.date_of_birth if self.date_of_birth else 'N/A'
        borrower['Gender'] = self.gender if self.gender else 'N/A'
        borrower['Which Ward do the borrower live in?'] = self.borrower_ward if self.borrower_ward else 'N/A'
        borrower['contact_number'] = self.contact_number if self.contact_number else 'N/A'
        borrower['NID Number'] = self.national_id if self.national_id else 'N/A'

        d['Borrower information'] = borrower

        disability_status = OrderedDict()
        disability_status[
            'Difficulty seeing, even if wearing glasses'] = self.seeing_difficulty if self.seeing_difficulty else 'N/A'
        disability_status[
            'Difficulty hearing, even if using a hearing aid'] = self.hearing_difficulty if self.hearing_difficulty else 'N/A'
        disability_status[
            'Difficulty walking or climbing steps'] = self.walking_difficulty if self.walking_difficulty else 'N/A'
        disability_status[
            'Difficulty remembering or concentrating'] = self.remembering_difficulty if self.remembering_difficulty else 'N/A'
        disability_status[
            'Difficulty with self-care such as washing all over or dressing'] = self.self_care_difficulty if self.self_care_difficulty else 'N/A'
        disability_status[
            'Difficulty communicating, for example understanding or being understood'] = self.communication_difficulty if self.communication_difficulty else 'N/A'

        d['Disability status of borrower'] = disability_status

        loan_info = OrderedDict()
        loan_info['loan_purpose'] = self.loan_purpose if self.loan_purpose else 'N/A'
        loan_info['loan_status'] = self.loan_status if self.loan_status else 'N/A'
        loan_info['Loan amount (in BDT)'] = self.approved_loan_amount if self.approved_loan_amount else 'N/A'
        loan_info['Loan Tenure (in months)'] = self.loan_tenure if self.loan_tenure else 'N/A'
        loan_info['loan_start_date'] = self.loan_start_date if self.loan_start_date else 'N/A'
        loan_info['loan_end_date'] = self.loan_end_date if self.loan_end_date else 'N/A'
        loan_info['interest_rate'] = self.interest_rate if self.interest_rate else 'N/A'

        d['Loan information'] = loan_info

        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by
        audit_info['created_on'] = self.render_timestamp(self.date_created)
        d["Audit Information"] = audit_info

        return d

    @property
    def render_repayment_status_instance(self):
        if not hasattr(self, 'repayment_status_instance'):
            setattr(self, 'repayment_status_instance', self.repayments.first() if self.repayments.exists() else None)
        return self.repayment_status_instance

    @property
    def render_monthly_installment_amount(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.monthly_installment_amount if repayment_status_instance else "N/A"

    @property
    def render_number_of_due_installments(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.number_of_due_installments if repayment_status_instance else "N/A"

    @property
    def render_total_due_amount(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.total_due_amount if repayment_status_instance else "N/A"

    @property
    def render_number_of_paid_installments(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.number_of_paid_installments if repayment_status_instance else "N/A"

    @property
    def render_total_repayment_amount(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.total_repayment_amount if repayment_status_instance else "N/A"

    @property
    def render_number_of_overdue_installments(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.number_of_overdue_installments if repayment_status_instance else "N/A"

    @property
    def render_overdue_amount(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.overdue_amount if repayment_status_instance else "N/A"

    @property
    def render_total_outstanding_amount(self):
        repayment_status_instance = self.render_repayment_status_instance
        return repayment_status_instance.total_outstanding_amount if repayment_status_instance else "N/A"

    @property
    def render_primary_group(self):
        try:
            return self.pg_member.assigned_to.name
        except:
            return 'N/A'

    @property
    def render_cdc(self):
        try:
            return self.pg_member.assigned_to.parent.name
        except:
            return 'N/A'

    @property
    def render_cdc_cluster(self):
        try:
            return self.pg_member.assigned_to.parent.parent.name
        except:
            return 'N/A'

    @classmethod
    def export_file_columns(cls):
        return [
            "city", "status_of_chdf_city_wise", "is_pg_member:Is the borrower a PG member",
            "pg_member_number:If yes, PG Member ID",
            "render_primary_group:PG Name",
            "render_cdc:CDC Name", "render_cdc_cluster:CDC Cluster Name",
            "name", "date_of_birth", "gender",
            "borrower_ward:Which Ward do the borrower live in?",
            "contact_number", "national_id:NID number",
            "seeing_difficulty", "hearing_difficulty", "walking_difficulty", "remembering_difficulty",
            "self_care_difficulty", "communication_difficulty", "approved_loan_amount:Loan amount (in BDT)",
            "loan_purpose", "loan_status", "loan_tenure:Loan Tenure (in months)", "loan_start_date",
            "loan_end_date", "interest_rate",

            "render_monthly_installment_amount:Monthly Installment Amount (in BDT)",
            "render_number_of_due_installments:Number of Installments Due",
            "render_total_due_amount:Total Amount Due (in BDT)",
            "render_number_of_paid_installments:Number of Installment Paid",
            "render_total_repayment_amount:Total Repayment Amount (in BDT)",
            "render_number_of_overdue_installments:Number of Installment Overdue",
            "render_overdue_amount:Overdue Amount (in BDT)",
            "render_total_outstanding_amount:Total Outstanding Amount (in BDT)",
        ]

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit,
            ViewActionEnum.Delete, ViewActionEnum.AdvancedExport
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
        queryset = super(CommunityHousingDevelopmentFund, cls).apply_search_filter(search_params=search_params,
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

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Repayment status',
                access_key='repayments',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model='nuprp_admin.InstallmentPayment',
                property=self.repayments,
                actions=[
                ]
            )
        ]
