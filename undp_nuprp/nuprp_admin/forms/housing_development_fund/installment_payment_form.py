from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin

from undp_nuprp.nuprp_admin.models.housing_development_fund.installment_payment import InstallmentPayment

__author__ = 'Ziaul Haque'


class InstallmentPaymentForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(InstallmentPaymentForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        parent_id = kwargs.get('parent_id', 0)
        if parent_id:
            from undp_nuprp.nuprp_admin.models.housing_development_fund.housing_development_fund import CommunityHousingDevelopmentFund
            parent_instance = CommunityHousingDevelopmentFund.objects.filter(pk=parent_id).first()
            if parent_instance:
                loan_amount = 0
                loan_tenure = 0
                interest_rate = 0
                if parent_instance.approved_loan_amount:
                    loan_amount = parent_instance.approved_loan_amount
                if parent_instance.loan_tenure:
                    loan_tenure = parent_instance.loan_tenure
                if parent_instance.interest_rate:
                    interest_rate = parent_instance.interest_rate

                monthly_installment_amount = 0
                if loan_amount > 0 and loan_tenure > 0:
                    monthly_installment_amount = (loan_amount / loan_tenure) + (loan_amount / loan_tenure * interest_rate / 100)

                self.fields['monthly_installment_amount'].initial = monthly_installment_amount
                # self.fields['total_due_amount'].initial = total_due_amount
        self.fields['monthly_installment_amount'].widget.attrs['readonly'] = True
        self.fields['total_due_amount'].widget.attrs['readonly'] = True
        self.fields['total_repayment_amount'].widget.attrs['readonly'] = True
        self.fields['number_of_overdue_installments'].widget.attrs['readonly'] = True
        self.fields['overdue_amount'].widget.attrs['readonly'] = True

    def clean(self):
        return super(InstallmentPaymentForm, self).clean()

    class Meta(GenericFormMixin.Meta):
        model = InstallmentPayment
        fields = [
            'monthly_installment_amount', 'number_of_due_installments', 'total_due_amount',
            'number_of_paid_installments', 'total_repayment_amount', 'number_of_overdue_installments',
            'overdue_amount', 'total_outstanding_amount'
        ]
        labels = {
            "monthly_installment_amount": "Monthly Installment Amount (in BDT)",
            "number_of_due_installments": "Number of Installments Due",
            "total_due_amount": "Total Amount Due (in BDT)",
            "number_of_paid_installments": "Number of Installment Paid",
            "total_repayment_amount": "Total Repayment Amount (in BDT)",
            "number_of_overdue_installments": "Number of Installment Overdue",
            "overdue_amount": "Overdue Amount (in BDT)",
            "total_outstanding_amount": "Total Outstanding Amount (in BDT)",
        }
