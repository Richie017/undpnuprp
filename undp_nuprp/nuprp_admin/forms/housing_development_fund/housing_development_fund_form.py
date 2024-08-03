from django import forms
from django.forms import modelformset_factory

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models import Geography
from undp_nuprp.nuprp_admin.forms.housing_development_fund.installment_payment_form import InstallmentPaymentForm
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.housing_development_fund.housing_development_fund import \
    CommunityHousingDevelopmentFund
from undp_nuprp.nuprp_admin.models.housing_development_fund.installment_payment import InstallmentPayment

__author__ = "Mahbub"

difficulty_options = (
    ('', 'Select One'),
    ('No difficulty', 'No difficulty'),
    ('Some difficulty', 'Some difficulty'),
    ('A lot of difficulty', 'A lot of difficulty'),
    ('Cannot do at all', 'Cannot do at all')
)
loan_purpose_choices = (
    ('', 'Select One'),
    ('New House Construction/Purchase', 'New House Construction/Purchase'),
    ('House Upgradation', 'House Upgradation'),
    ('Land Purchase', 'Land Purchase'),
    ('Extensions (e.g. Toilet)', 'Extensions (e.g. Toilet)'),
    ('Other Tenure Security Related Activities', 'Other Tenure Security Related Activities'),
)
loan_status_choices = (
    ('', 'Select One'),
    ('Applied', 'Applied'),
    ('Approved', 'Approved'),
    ('Disbursed', 'Disbursed'),
)
status_of_chdf_city_wise_choices = (
    ('', 'Select One'),
    ('Newly Formed', 'Newly Formed'),
    ('Reactivated', 'Reactivated'),
    ('Registered', 'Registered'),
    ('Construction Started', 'Construction Started'),
    ('Construction Completed', 'Construction Completed'),
    ('Finished', 'Finished'),
)

repayment_formset = modelformset_factory(
    InstallmentPayment, form=InstallmentPaymentForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, max_num=1, validate_min=True, can_delete=False
)


class CommunityHousingDevelopmentFundForm(GenericFormMixin):
    pg_name = forms.CharField(required=False, disabled=True, label="PG Name")
    cdc_name = forms.CharField(required=False, disabled=True, label="CDC Name")
    cdc_cluster_name = forms.CharField(required=False, disabled=True, label="CDC Cluster Name")

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(CommunityHousingDevelopmentFundForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['gender'] = forms.CharField(
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Male', 'Male'),
                    ('Female', 'Female'),
                    ('Hijra', 'Hijra'),
                )), required=False
        )

        self.fields['borrower_ward'] = forms.CharField(
            label="Which Ward do the borrower live in?",
            required=False
        )

        self.fields['is_pg_member'] = forms.CharField(
            label='Is the borrower a PG member',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Yes', 'Yes'),
                    ('No', 'No'),
                )
            ), required=False
        )
        self.fields['pg_member_number'].label = 'If yes, PG Member ID'
        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City', empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['national_id'] = forms.IntegerField(
            label='NID number',
            required=False
        )

        self.fields['status_of_chdf_city_wise'] = forms.ChoiceField(
            required=False,
            label='Status of CHDF city wise',
            choices=status_of_chdf_city_wise_choices,
            initial=instance.status_of_chdf_city_wise if instance else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )

        self.fields['date_of_birth'] = forms.DateTimeField(
            label='Date of Birth',
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
        )
        self.fields['loan_purpose'] = forms.CharField(
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'},
                choices=loan_purpose_choices
            ), required=False
        )
        self.fields['loan_status'] = forms.CharField(
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'},
                choices=loan_status_choices
            ), required=False
        )
        self.fields['loan_start_date'] = forms.DateTimeField(
            label='Start Date',
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
        )

        self.fields['loan_end_date'] = forms.DateTimeField(
            label='End Date',
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
        )

        self.fields['seeing_difficulty'] = forms.CharField(
            label='Difficulty seeing, even if wearing glasses',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=difficulty_options
            ), required=False
        )

        self.fields['hearing_difficulty'] = forms.CharField(
            label='Difficulty hearing, even if using a hearing aid',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=difficulty_options
            ), required=False
        )

        self.fields['walking_difficulty'] = forms.CharField(
            label='Difficulty walking or climbing steps',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=difficulty_options
            ), required=False
        )

        self.fields['remembering_difficulty'] = forms.CharField(
            label='Difficulty remembering or concentrating',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=difficulty_options
            ), required=False
        )

        self.fields['self_care_difficulty'] = forms.CharField(
            label='Difficulty with self-care such as washing all over or dressing',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=difficulty_options
            ), required=False
        )

        self.fields['communication_difficulty'] = forms.CharField(
            label='Difficulty communicating, for example understanding or being understood',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=difficulty_options
            ), required=False
        )

        if self.instance.pk and self.instance.pg_member:
            try:
                self.fields['pg_name'].initial = self.instance.pg_member.assigned_to.name
            except:
                pass

            try:
                self.fields['cdc_name'].initial = self.instance.pg_member.assigned_to.parent.name
            except:
                pass

            try:
                self.fields['cdc_cluster_name'].initial = self.instance.pg_member.assigned_to.parent.parent.name
            except:
                pass

        if instance and instance.pk:
            repayment_objects = instance.repayments.all()
        else:
            repayment_objects = InstallmentPayment.objects.none()

        self.add_child_form("repayments", repayment_formset(
            data=data, files=files, queryset=repayment_objects,
            header='Repayment status', add_more=False, **kwargs
        ))

    @classmethod
    def get_template(cls):
        return 'communityhousingdevelopmentfund/create.html'

    def clean(self):
        cleaned_data = super(CommunityHousingDevelopmentFundForm, self).clean()
        self.pg_member = None
        if 'is_pg_member' in cleaned_data and cleaned_data['is_pg_member'] == 'Yes':
            if 'pg_member_number' in cleaned_data:
                pg_member_number = cleaned_data['pg_member_number']
                if pg_member_number:
                    if len(pg_member_number) != 12:
                        self.add_error('pg_member_number', "PG Member ID must be 12 digits.")
                        del cleaned_data['pg_member_number']
                    elif not PrimaryGroupMember.objects.filter(assigned_code=pg_member_number).exists():
                        self.add_error('pg_member_number', "PG Member ID is not valid.")
                        del cleaned_data['pg_member_number']
                    else:
                        self.pg_member = PrimaryGroupMember.objects.filter(assigned_code=pg_member_number).first()
                else:
                    self.add_error('pg_member_number', "PG Member ID is required.")
                    del cleaned_data['pg_member_number']
            else:
                self.add_error('pg_member_number', "PG Member ID is required.")
                del cleaned_data['pg_member_number']
        else:
            cleaned_data['pg_member_number'] = ''
        return cleaned_data

    def save(self, commit=True):
        self.instance.pg_member = self.pg_member
        self.instance = super(CommunityHousingDevelopmentFundForm, self).save(commit=commit)
        return self.instance

    class Meta(GenericFormMixin.Meta):
        model = CommunityHousingDevelopmentFund
        fields = [
            'name', 'date_of_birth', 'gender', 'borrower_ward', 'is_pg_member', 'pg_member_number',
            'pg_name', 'cdc_name', 'cdc_cluster_name',
            'contact_number', 'national_id', 'city', 'status_of_chdf_city_wise',
            'seeing_difficulty', 'hearing_difficulty', 'walking_difficulty', 'remembering_difficulty',
            'self_care_difficulty', 'communication_difficulty', 'loan_purpose', 'loan_status',
            'approved_loan_amount', 'loan_tenure', 'loan_start_date', 'loan_end_date', 'interest_rate',
        ]

        labels = {
            'pg_member_number': 'PG Member ID',
            'national_id': 'NID number',
            'approved_loan_amount': 'Loan amount (in BDT)',
            'loan_tenure': 'Loan Tenure (in months)',
        }

    @classmethod
    def field_groups(cls):
        _group = super(CommunityHousingDevelopmentFundForm, cls).field_groups()
        _group['CHDF information'] = [
            'city', 'status_of_chdf_city_wise'
        ]

        _group['Borrower information'] = [
            'name', 'is_pg_member', 'pg_member_number', 'pg_name', 'cdc_name', 'cdc_cluster_name',
            'date_of_birth', 'gender', 'borrower_ward', 'contact_number', 'national_id'
        ]

        _group['Disability status of borrower'] = [
            'seeing_difficulty', 'hearing_difficulty', 'walking_difficulty', 'remembering_difficulty',
            'self_care_difficulty', 'communication_difficulty'
        ]

        _group['Loan information'] = [
            'loan_purpose', 'loan_status', 'approved_loan_amount', 'loan_tenure', 'loan_start_date',
            'loan_end_date', 'interest_rate',
        ]

        return _group
