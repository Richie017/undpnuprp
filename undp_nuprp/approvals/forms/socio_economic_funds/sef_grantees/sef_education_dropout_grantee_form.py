from django import forms
from django.forms import modelformset_factory

from blackwidow.core.mixins.formmixin import GenericModelFormSetMixin
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.forms import SEFGranteeForm
from undp_nuprp.approvals.forms import SEFInstallmentForm
from undp_nuprp.approvals.models import SEFEducationDropoutGrantee
from undp_nuprp.approvals.models import SEFInstallment

__author__ = 'Ziaul Haque'

contact_address_formset = modelformset_factory(
    SEFInstallment, form=SEFInstallmentForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)


class SEFEducationDropoutGranteeForm(SEFGranteeForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFEducationDropoutGranteeForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs
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

        self.fields['grantee_status'] = forms.CharField(
            label='Grantee status',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Functional', 'Functional'),
                    ('Migrated', 'Migrated'),
                    ('deceased', 'deceased'),
                    ('drop out', 'drop out')
                )
            ),
            required=False
        )

    class Meta(GenericFormMixin.Meta):
        model = SEFEducationDropoutGrantee
        fields = ('name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
                  'relation_with_pg_member', 'grantee_status', 'has_disability', 'difficulty_in_seeing',
                  'difficulty_in_hearing',
                  'difficulty_in_walking', 'difficulty_in_remembering', 'difficulty_in_self_care',
                  'difficulty_in_communicating', 'education_level', 'is_still_attending_school', 'remarks')
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFEducationDropoutGranteeForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
             'relation_with_pg_member', 'education_level', 'is_still_attending_school', 'grantee_status', 'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['has_disability', 'difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking',
             'difficulty_in_remembering', 'difficulty_in_self_care', 'difficulty_in_communicating']

        return _group
