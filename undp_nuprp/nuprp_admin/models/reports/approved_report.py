from collections import OrderedDict

from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport

__author__ = "Shama"


class ApprovedReport(SavingsAndCreditReport):
    @classmethod
    def distinct_fields(cls):
        return ['parent_id']

    @classmethod
    def distinct_fields(cls):
        return ['parent_id']

    @classmethod
    def get_manage_buttons(cls):
        return []

    def details_link_config(self, **kwargs):
        return []

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
        details['cumulatve_report'] = self.render_cumulative_report
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

    class Meta:
        app_label = 'nuprp_admin'
        proxy = True
