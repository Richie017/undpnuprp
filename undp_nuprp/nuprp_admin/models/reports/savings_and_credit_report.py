from collections import OrderedDict

from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.models.common.location import Location
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.geography.geography import Geography
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
from undp_nuprp.reports.managers.savings_and_credit.savings_and_credit_indicator_manager import \
    get_report_indicator_table_data
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum
from undp_nuprp.reports.utils.enums.savings_and_credit_indicator import SavingsAndCreditIndicatorEnum

__author__ = "Shama"

choices = [('Yes', 'Yes'), ('No', 'No'), ('Not Available', 'Not Available')]

area_choices = [('Savings', 'Savings'), ('Savings Withdrawals', 'Savings Withdrawals'),
                ('Loans Taken', 'Loans Taken'), ('Loans Repaid', 'Loans Repaid'), ('Balance', 'Balance')]

month_choices = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
                 (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), (9, 'September'),
                 (10, 'October'), (11, 'November'), (12, 'December')]

year_choices = []
for y in range(2010, 2101):
    year_tuple = (int(y), str(y))
    year_choices.append(year_tuple)


class SavingsAndCreditReport(OrganizationDomainEntity):
    year = models.IntegerField(default=2010)
    month = models.IntegerField(default=1)
    scg = models.ForeignKey(SavingsAndCreditGroup, null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey('core.Geography', null=True, on_delete=models.SET_NULL)
    deposited_savings = models.FloatField(default=0)
    withdrawal_savings = models.FloatField(default=0)
    loan_disbursed_number = models.IntegerField(default=0)
    loan_disbursed = models.FloatField(default=0)
    loan_repaid = models.FloatField(default=0)
    outstanding_loans = models.FloatField(default=0)
    overdue_loans = models.FloatField(default=0)
    passbook_update = models.CharField(max_length=20, blank=False, choices=choices, default=choices[0][0])
    passbook_cdc_inconsistency = models.CharField(max_length=20, blank=False, choices=choices, default=choices[0][0])
    area_inconsistency = models.CharField(max_length=100, blank=False, choices=area_choices, default=area_choices[0][0])
    service_charges = models.FloatField(default=0)
    admission_fees = models.FloatField(default=0)
    bank_interest = models.FloatField(default=0)
    bank_charges = models.FloatField(default=0)
    other_expenditure = models.FloatField(default=0)
    bank_balance = models.FloatField(default=0)
    cash_in_hand = models.FloatField(default=0)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    remarks = models.CharField(max_length=300, null=True)
    parent = models.ForeignKey('nuprp_admin.SavingsAndCreditReport', null=True, on_delete=models.SET_NULL)
    parent_tsync_id = models.CharField(max_length=60, null=True)

    @classmethod
    def get_choices(cls):
        return choices

    @classmethod
    def get_area_choices(cls):
        return area_choices

    @classmethod
    def get_month_choices(cls):
        return month_choices

    @classmethod
    def get_year_choices(cls):
        return year_choices

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_primary_group(self):
        return self.scg.primary_group if self.scg else 'N/A'

    @property
    def render_total_balance(self):
        if self.cash_in_hand or self.bank_balance:
            return self.cash_in_hand + self.bank_balance
        else:
            return 0

    @property
    def render_for_month(self):
        try:
            month_name = [m[1] for m in month_choices if m[0] == self.month][0]
            return month_name + ', ' + str(self.year)
        except:
            return 'N/A'

    @property
    def render_primary_group_id(self):
        return self.scg.primary_group.assigned_code if self.scg else 'N/A'

    @property
    def render_scg_formation_date(self):
        return self.scg.date_of_formation if self.scg else 'N/A'

    @property
    def render_cumulative_report(self):
        from undp_nuprp.nuprp_admin.models.reports.cumulative_report import CumulativeReport
        cr = CumulativeReport.objects.filter(scg_id=self.scg_id).first()
        return cr if cr is not None else 'N/A'

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'scg:SCG', 'render_primary_group', 'render_for_month', 'date_created:Report Created',
            'created_by', 'render_total_balance', 'last_updated')

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        details['code'] = self.code
        details['SCG'] = self.scg
        details['primary_group'] = self.render_primary_group
        details['for_month'] = self.render_for_month
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        details['city'] = self.city
        details['deposited_savings'] = self.deposited_savings
        details['withdrawal_savings'] = self.withdrawal_savings
        details['loan_disbursed_number'] = self.loan_disbursed_number
        details['loan_disbursed'] = self.loan_disbursed
        details['loan_repaid'] = self.loan_repaid
        details['outstanding_loans'] = self.outstanding_loans
        details['overdue_loans'] = self.overdue_loans
        details['passbook_update'] = self.passbook_update
        details['passbook_cdc_inconsistency'] = self.passbook_cdc_inconsistency
        details['area_inconsistency'] = self.area_inconsistency
        details['service_charges'] = self.service_charges
        details['admission_fees'] = self.admission_fees
        details['bank_interest'] = self.bank_interest
        details['bank_charges'] = self.bank_charges
        details['other_expenditure'] = self.other_expenditure
        details['bank_balance'] = self.bank_balance
        details['cash_in_hand'] = self.cash_in_hand
        details['remarks'] = self.remarks

        return details

    def build_report(self, wards=list(), from_time=None, to_time=None, indicator=None, graph_type=None):
        if indicator == SavingsAndCreditIndicatorEnum.SCGNumberEnum.value:
            if graph_type == DataTableConfigEnum.DataTable.value:
                return get_report_indicator_table_data(wards=wards, from_time=from_time, to_time=to_time)
    def approval_level_1_action(self, action, *args, **kwargs):
        from undp_nuprp.nuprp_admin.models.reports.cumulative_report import CumulativeReport
        from undp_nuprp.approvals.models.savings_and_credits.logs.report_log import SavingsAndCreditReportlog, \
            ActionTypeEnum
        if action == "Approved":

            SavingsAndCreditReport.objects.filter(year=self.year, month=self.month,
                                                  scg_id=self.scg_id, type='PendingReport').update(
                type='ApprovedReport')

            cumulative_report = CumulativeReport.objects.filter(scg_id=self.scg_id).first()
            if cumulative_report is None:
                cumulative_report = CumulativeReport.objects.create(scg_id=self.scg_id,
                                                                    city_id=self.city_id,
                                                                    deposited_savings=self.deposited_savings,
                                                                    withdrawal_savings=self.withdrawal_savings,
                                                                    loan_disbursed_number=self.loan_disbursed_number,
                                                                    loan_disbursed=self.loan_disbursed,
                                                                    loan_repaid=self.loan_repaid,
                                                                    outstanding_loans=self.outstanding_loans,
                                                                    overdue_loans=self.overdue_loans,
                                                                    passbook_update=self.passbook_update,
                                                                    passbook_cdc_inconsistency=self.passbook_cdc_inconsistency,
                                                                    area_inconsistency=self.area_inconsistency,
                                                                    service_charges=self.service_charges,
                                                                    admission_fees=self.admission_fees,
                                                                    bank_interest=self.bank_interest,
                                                                    bank_charges=self.bank_charges,
                                                                    other_expenditure=self.other_expenditure,
                                                                    bank_balance=self.bank_balance,
                                                                    cash_in_hand=self.cash_in_hand
                                                                    )
            else:
                cumulative_report.scg_id = self.scg_id
                cumulative_report.deposited_savings += self.deposited_savings
                cumulative_report.withdrawal_savings += self.withdrawal_savings
                cumulative_report.loan_disbursed_number += self.loan_disbursed_number
                cumulative_report.loan_disbursed += self.loan_disbursed
                cumulative_report.loan_repaid += self.loan_repaid
                cumulative_report.outstanding_loans += self.outstanding_loans
                cumulative_report.overdue_loans += self.overdue_loans
                cumulative_report.passbook_update = self.passbook_update
                cumulative_report.passbook_cdc_inconsistency = self.passbook_cdc_inconsistency
                cumulative_report.area_inconsistency = self.area_inconsistency
                cumulative_report.service_charges += self.service_charges
                cumulative_report.admission_fees += self.admission_fees
                cumulative_report.bank_interest += self.bank_interest
                cumulative_report.bank_charges += self.bank_charges
                cumulative_report.other_expenditure += self.other_expenditure
                cumulative_report.bank_balance += self.bank_balance
                cumulative_report.cash_in_hand += self.cash_in_hand

            cumulative_report.save()
            SavingsAndCreditReportlog.create_report_log(report=self.pk, action=ActionTypeEnum.Approved.value)

    @classmethod
    def get_serializer(cls):
        IUSerializer = OrganizationDomainEntity.get_serializer()

        class SavingsAndCreditReportSerializer(IUSerializer):
            location = Location.get_serializer()()

            class Meta:
                model = cls
                fields = 'id', 'tsync_id', 'type', 'city', 'year', 'month', 'scg', 'deposited_savings', 'withdrawal_savings', \
                         'loan_disbursed_number', 'loan_disbursed', 'loan_repaid', 'outstanding_loans', \
                         'overdue_loans', 'passbook_update', 'passbook_cdc_inconsistency', 'area_inconsistency', \
                         'service_charges', 'admission_fees', 'bank_interest', 'bank_charges', 'other_expenditure', \
                         'bank_balance', 'cash_in_hand', 'remarks', 'location', 'last_updated'

        return SavingsAndCreditReportSerializer

    class Meta:
        app_label = 'nuprp_admin'
