from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.forms.savings_and_credits.sef_grant_disbursement.sef_grant_disbursement_form import \
    SEFGrantDisbursementForm
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_nutrition_grant_disbursement import \
    SEFNutritionGrantDisbursement

__author__ = 'Shuvro'


class SEFNutritionGrantDisbursementForm(SEFGrantDisbursementForm):
    is_still_pregnant_or_lactating = forms.CharField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFNutritionGrantDisbursementForm, self).__init__(
            data=data, files=files, instance=instance.sefnutritiongrantee if instance else None,
            prefix=prefix,
            **kwargs
        )

        self.fields['is_still_pregnant_or_lactating'] = forms.CharField(
            label='Is the grantee still pregnant or lactating?',
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
        model = SEFNutritionGrantDisbursement
        fields = (
            'name', 'contact_number', 'account_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
            'relation_with_pg_member', 'difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking',
            'difficulty_in_remembering', 'difficulty_in_self_care', 'difficulty_in_communicating',
            'is_still_pregnant_or_lactating', 'remarks'
        )
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFNutritionGrantDisbursementForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['name', 'contact_number', 'account_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
             'relation_with_pg_member', 'is_still_pregnant_or_lactating', 'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking', 'difficulty_in_remembering',
             'difficulty_in_self_care', 'difficulty_in_communicating']

        return _group
