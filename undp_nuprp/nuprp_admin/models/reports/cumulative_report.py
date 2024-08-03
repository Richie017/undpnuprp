from blackwidow.core.models.common.location import Location
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport

__author__ = "Shama"


# @decorate(save_audit_log, is_object_context, expose_api('cumulative-reports'),
#           route(route='cumulative-reports', group='Savings & Credit Reports', module=ModuleEnum.Execute,
#                 display_name='Cumulative Reports', group_order=1, item_order=5))
class CumulativeReport(SavingsAndCreditReport):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @classmethod
    def get_manage_buttons(cls):
        return []

    def details_link_config(self, **kwargs):
        return []

    @classmethod
    def get_serializer(cls):
        _SavingsAndCreditReportSerializer = SavingsAndCreditReport.get_serializer()

        class CumulativeReportSerializer(_SavingsAndCreditReportSerializer):
            location = Location.get_serializer()()

            class Meta:
                model = cls
                fields = 'id', 'tsync_id', 'year', 'month', 'city', 'scg', 'deposited_savings', 'withdrawal_savings', \
                         'loan_disbursed_number', 'loan_disbursed', 'loan_repaid', 'outstanding_loans', \
                         'overdue_loans', 'passbook_update', 'passbook_cdc_inconsistency', 'area_inconsistency', \
                         'service_charges', 'admission_fees', 'bank_interest', 'bank_charges', 'other_expenditure', \
                         'bank_balance', 'cash_in_hand', 'remarks', 'location', 'last_updated'

        return CumulativeReportSerializer
