from django import forms
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.form_extensions import fields_ordering
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport

__author__ = "Shama"


class SavingsAndCreditReportForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SavingsAndCreditReportForm, self).__init__(data=data, files=files,
                                                         instance=instance, prefix=prefix, **kwargs)

        self.fields['year'] = forms.ChoiceField(
            label='Year',
            widget=forms.Select(attrs={'class': 'select2'}),
            choices=SavingsAndCreditReport.get_year_choices(),
            required=False
        )

        self.fields['month'] = forms.ChoiceField(
            label='Month',
            widget=forms.Select(attrs={'class': 'select2'}),
            choices=SavingsAndCreditReport.get_month_choices(),
            required=False
        )

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'), label='City',
            empty_label='Select One',
            initial=instance.city if instance else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}),
            required=False
        )

        self.fields['scg'] = GenericModelChoiceField(
            queryset=SavingsAndCreditGroup.objects.all(), label='Savings And Credit Group',
            initial=instance.scg if instance else None,
            required=False,
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220',
                                          'data-depends-on': 'city',
                                          'data-depends-property': 'address:geography:id',
                                          'data-url': reverse(SavingsAndCreditGroup.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1'
                                          })
        )

        self.fields['deposited_savings'] = forms.FloatField(
            label='Value of Savings deposited',
            required=False
        )

        self.fields['withdrawal_savings'] = forms.FloatField(
            label='Value of Savings withdrawn',
            required=False
        )

        self.fields['loan_disbursed_number'] = forms.FloatField(
            label='Number of Loan disbursed',
            required=False
        )

        self.fields['loan_disbursed_'] = forms.FloatField(
            label='Value of loans disbursed',
            required=False
        )

        self.fields['loan_repaid'] = forms.FloatField(
            label='Value of loans repaid',
            required=False
        )
        self.fields['outstanding_loans'] = forms.FloatField(
            label='Value of Outstanding loans',
            required=False
        )
        self.fields['overdue_loans'] = forms.FloatField(
            label='Value of overdue loans',
            required=False
        )

        self.fields['passbook_update'] = forms.ChoiceField(
            label='Passbook Updated?',
            widget=forms.Select(attrs={'class': 'select2'}),
            choices=SavingsAndCreditReport.get_choices(),
            required=False
        )

        self.fields['passbook_cdc_inconsistency'] = forms.ChoiceField(
            label=' Are there any inconsistencies between passbook and CDC record?',
            widget=forms.Select(attrs={'class': 'select2'}),
            choices=SavingsAndCreditReport.get_choices(),
            required=False
        )

        self.fields['area_inconsistency'] = forms.ChoiceField(
            label=' In which areas are there inconsistencies? ',
            widget=forms.Select(attrs={'class': 'select2'}),
            choices=SavingsAndCreditReport.get_area_choices(),
            required=False
        )

        self.fields['service_charges'] = forms.FloatField(
            label='Value of service charges collected',
            required=False
        )
        self.fields['admission_fees'] = forms.FloatField(
            label='Value of admission fees collected',
            required=False
        )
        self.fields['bank_interest'] = forms.FloatField(
            label='Value of interest from Bank collected',
            required=False
        )
        self.fields['bank_charges'] = forms.FloatField(
            label='Value of Bank charges',
            required=False
        )
        self.fields['other_expenditure'] = forms.FloatField(
            label=' Value of other expenditure',
            required=False
        )
        self.fields['bank_balance'] = forms.FloatField(
            label='Bank Balance',
            required=False
        )
        self.fields['cash_in_hand'] = forms.FloatField(
            label='Cash in Hand',
            required=False
        )
        self.fields['remarks'] = forms.CharField(
            label='Remarks',
            required=False
        )

        self.fields = fields_ordering(
            fields=self.fields, fields_order=['year', 'month', 'city', 'scg', 'deposited_savings', 'withdrawal_savings',
                                              'loan_disbursed_number',
                                              'loan_disbursed', 'loan_repaid', 'outstanding_loans', 'overdue_loans',
                                              'passbook_update',
                                              'passbook_cdc_inconsistency', 'area_inconsistency', 'service_charges',
                                              'admission_fees',
                                              'bank_interest', 'bank_charges', 'other_expenditure', 'bank_balance',
                                              'cash_in_hand', 'remarks']
        )

    class Meta(GenericFormMixin.Meta):
        model = SavingsAndCreditReport
        fields = ['year', 'month', 'city', 'scg', 'deposited_savings', 'withdrawal_savings', 'loan_disbursed_number',
                  'loan_disbursed', 'loan_repaid', 'outstanding_loans', 'overdue_loans', 'passbook_update',
                  'passbook_cdc_inconsistency', 'area_inconsistency', 'service_charges', 'admission_fees',
                  'bank_interest', 'bank_charges', 'other_expenditure', 'bank_balance', 'cash_in_hand', 'remarks', ]
