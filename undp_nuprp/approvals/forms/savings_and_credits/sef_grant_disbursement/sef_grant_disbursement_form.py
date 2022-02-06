from django import forms
from django.db import transaction

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.engine.exceptions import BWException
from undp_nuprp.approvals.models import SEFGrantee
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember

__author__ = 'Shuvro'


class SEFGrantDisbursementForm(GenericFormMixin):
    name = forms.CharField()
    contact_number = forms.CharField()
    age = forms.CharField()
    gender = forms.CharField()
    pg_member_assigned_code = forms.CharField()
    pg_member_name = forms.CharField(disabled=True)
    relation_with_pg_member = forms.CharField()
    difficulty_in_seeing = forms.CharField()
    difficulty_in_hearing = forms.CharField()
    difficulty_in_walking = forms.CharField()
    difficulty_in_remembering = forms.CharField()
    difficulty_in_self_care = forms.CharField()
    difficulty_in_communicating = forms.CharField()
    remarks = forms.CharField(widget=forms.Textarea)

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFGrantDisbursementForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                       **kwargs)

        self.fields['name'].label = "Beneficiary's Name"
        self.fields['name'].widget.attrs['readonly'] = True

        self.fields['gender'] = forms.CharField(
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Male', 'Male'),
                    ('Female', 'Female'),
                    ('Hijra', 'Hijra'),
                )
            ),
        )

        self.fields['relation_with_pg_member'] = forms.CharField(
            label="Relationship of grantee to PG member",
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('PG Member', 'PG Member'),
                    ('Spouse', 'Spouse'),
                    ('Son', 'Son'),
                    ('Daughter', 'Daughter'),
                    ('Mother', 'Mother'),
                    ('Father', 'Father'),
                    ('Uncle', 'Uncle'),
                    ('Aunt', 'Aunt'),
                    ('Other', 'Other')
                )
            )
        )

        self.fields['pg_member_assigned_code'] = forms.CharField(
            label='PG Member ID', required=True,
        )
        self.fields['pg_member_assigned_code'].widget.attrs['readonly'] = True

        self.fields['pg_member_name'] = forms.CharField(
            label='PG member\'s name', required=True,
            widget=forms.TextInput(attrs={'readonly': 'readonly'})
        )

        self.fields['difficulty_in_seeing'] = forms.CharField(
            label='Difficulty seeing, even if wearing glasses',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('No difficulty', 'No difficulty'),
                    ('Some difficulty', 'Some difficulty'),
                    ('A lot of difficulty', 'A lot of difficulty'),
                    ('Cannot do at all', 'Cannot do at all'),
                )
            )
        )

        self.fields['difficulty_in_hearing'] = forms.CharField(
            label='Difficulty hearing, even if using a hearing aid',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('No difficulty', 'No difficulty'),
                    ('Some difficulty', 'Some difficulty'),
                    ('A lot of difficulty', 'A lot of difficulty'),
                    ('Cannot do at all', 'Cannot do at all'),
                )
            )
        )

        self.fields['difficulty_in_walking'] = forms.CharField(
            label='Difficulty walking or climbing steps',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('No difficulty', 'No difficulty'),
                    ('Some difficulty', 'Some difficulty'),
                    ('A lot of difficulty', 'A lot of difficulty'),
                    ('Cannot do at all', 'Cannot do at all'),
                )
            )
        )

        self.fields['difficulty_in_remembering'] = forms.CharField(
            label='Difficulty remembering or concentrating',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('No difficulty', 'No difficulty'),
                    ('Some difficulty', 'Some difficulty'),
                    ('A lot of difficulty', 'A lot of difficulty'),
                    ('Cannot do at all', 'Cannot do at all'),
                )
            )
        )

        self.fields['difficulty_in_self_care'] = forms.CharField(
            label='Difficulty with self-care such as washing all over or dressing',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('No difficulty', 'No difficulty'),
                    ('Some difficulty', 'Some difficulty'),
                    ('A lot of difficulty', 'A lot of difficulty'),
                    ('Cannot do at all', 'Cannot do at all'),
                )
            )
        )

        self.fields['difficulty_in_communicating'] = forms.CharField(
            label='Difficulty communicating, for example understanding or being understood',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('No difficulty', 'No difficulty'),
                    ('Some difficulty', 'Some difficulty'),
                    ('A lot of difficulty', 'A lot of difficulty'),
                    ('Cannot do at all', 'Cannot do at all'),
                )
            )
        )

        self.fields['account_number'] = forms.CharField(
            initial=instance.sef_grant_disbursement.account_number if instance else None,
            required=True
        )
        self.fields['remarks'].required = False

    def clean(self):
        cleaned_data = super(SEFGrantDisbursementForm, self).clean()

        if 'pg_member_assigned_code' in cleaned_data:
            pg_member_assigned_code = cleaned_data['pg_member_assigned_code'].strip('\'')
            if not PrimaryGroupMember.objects.filter(assigned_code=pg_member_assigned_code).exists():
                pg_member_assigned_code = '0' + pg_member_assigned_code
                if not PrimaryGroupMember.objects.filter(assigned_code=pg_member_assigned_code).exists():
                    raise BWException("Primary Group Member with this Assigned Code doesn't exists.")
            cleaned_data['pg_member_assigned_code'] = pg_member_assigned_code
        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            _assigned_code = self.cleaned_data['pg_member_assigned_code']
            self.instance.pg_member_id = PrimaryGroupMember.objects.filter(assigned_code=_assigned_code).first().id
            sef_grantee = super(SEFGrantDisbursementForm, self).save(commit=commit)
            self.instance.sef_grant_disbursement.name = sef_grantee.name
            self.instance.sef_grant_disbursement.account_number = self.cleaned_data['account_number']
            self.instance.sef_grant_disbursement.pg_member = sef_grantee.pg_member
            self.instance.sef_grant_disbursement.pg_member_assigned_code = sef_grantee.pg_member_assigned_code
            self.instance.sef_grant_disbursement.pg_member_name = sef_grantee.pg_member_name
            self.instance.sef_grant_disbursement.save()
            return sef_grantee

    class Meta(GenericFormMixin.Meta):
        model = SEFGrantee
        fields = (
            'name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
            'relation_with_pg_member', 'difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking',
            'difficulty_in_remembering', 'difficulty_in_self_care', 'difficulty_in_communicating', 'remarks')
        widgets = {
            'remarks': forms.Textarea
        }
