from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.forms.savings_and_credits.sef_grant_disbursement.sef_grant_disbursement_form import \
    SEFGrantDisbursementForm
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_education_dropout_grant_disbursement import \
    SEFEducationDropoutGrantDisbursement

__author__ = 'Shuvro'


class SEFEducationDropoutGrantDisbursementForm(SEFGrantDisbursementForm):
    education_level = forms.CharField()
    is_still_attending_school = forms.CharField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFEducationDropoutGrantDisbursementForm, self).__init__(
            data=data, files=files, instance=instance.sefeducationdropoutgrantee if instance else None,
            prefix=prefix,
            **kwargs
        )

        self.fields['education_level'] = forms.CharField(
            label='Class',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('One', 'One'),
                    ('Two', 'Two'),
                    ('Three', 'Three'),
                    ('Four', 'Four'),
                    ('Five', 'Five'),
                    ('Six', 'Six'),
                    ('Seven', 'Seven'),
                    ('Eight', 'Eight'),
                    ('Nine', 'Nine'),
                    ('Ten', 'Ten'),
                )
            )
        )

        self.fields['is_still_attending_school'] = forms.CharField(
            label='Is the grantee still attending School?',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Yes', 'Yes'),
                    ('No', 'No'),
                )
            )
        )

    class Meta(GenericFormMixin.Meta):
        model = SEFEducationDropoutGrantDisbursement
        fields = (
            'name', 'contact_number', 'account_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
            'relation_with_pg_member', 'difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking',
            'difficulty_in_remembering', 'difficulty_in_self_care', 'difficulty_in_communicating',
            'education_level', 'is_still_attending_school', 'remarks'
        )
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFEducationDropoutGrantDisbursementForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['name', 'contact_number', 'account_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
             'relation_with_pg_member', 'education_level', 'is_still_attending_school', 'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking', 'difficulty_in_remembering',
             'difficulty_in_self_care', 'difficulty_in_communicating']

        return _group
