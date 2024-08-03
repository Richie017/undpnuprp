from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.forms.reports.savings_and_credit_report_form import SavingsAndCreditReportForm
from undp_nuprp.nuprp_admin.models.reports.pending_report import PendingReport

__author__ = "Shama"


class PendingReportForm(SavingsAndCreditReportForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(PendingReportForm, self).__init__(data=data, files=files,
                                                instance=instance, prefix=prefix, **kwargs)

    class Meta(SavingsAndCreditReportForm.Meta):
        model = PendingReport
