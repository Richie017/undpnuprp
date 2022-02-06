from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.approvals.forms import SEFGranteeForm
from undp_nuprp.approvals.models import SEFNutritionGrantee

__author__ = 'Ziaul Haque'


class SEFNutritionGranteeForm(SEFGranteeForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFNutritionGranteeForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs
        )

        self.fields['is_still_pregnant_or_lactating'] = forms.CharField(
            label='Is the grantee still pregnant or lactating?',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Pregnant', 'Pregnant'),
                    ('Lactating', 'Lactating'),
                )
            )
        )

        self.fields['relation_with_pg_member'] = forms.CharField(
            label="Relationship of grantee to PG member",
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('PG Member', 'PG Member'),
                    ('Daughter', 'Daughter'),
                    ('Daughter in law', 'Daughter in law'),
                    ('Son in law', 'Son in law'),
                    ('Brother in law', 'Brother in law'),
                    ('Sister in law', 'Sister in law'),
                    ('Other', 'Other')
                )
            )
        )

        _choices = [('', 'Select One'), ]
        for i in range(2019, 2031):
            _choices.append((str(i), str(i)))
        self.fields['grant_received_year'] = forms.CharField(
            label="Grant Received-Year", required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=_choices
            )
        )

        self.fields['grant_received_month'] = forms.CharField(
            label="Grant Received-Month", required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('January', 'January'),
                    ('February', 'February'),
                    ('March', 'March'),
                    ('April', 'April'),
                    ('May', 'May'),
                    ('June', 'June'),
                    ('July', 'July'),
                    ('August', 'August'),
                    ('September', 'September'),
                    ('October', 'October'),
                    ('November', 'November'),
                    ('December', 'December'),
                )
            )
        )

        _choices = [('', 'Select One'), ]
        for i in range(3, 10):
            _choices.append((i, i))
        self.fields['number_of_pregnancy_month'] = forms.IntegerField(
            label="Number of Months (Pregnancy)", required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=_choices
            )
        )

        _choices = [('', 'Select One'), ]
        for i in range(1, 25):
            _choices.append((i, i))
        self.fields['age_of_child_in_month'] = forms.IntegerField(
            label="Age of Child in Month (if Lactating)", required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=_choices
            )
        )

        del self.fields['gender']

    class Meta(GenericFormMixin.Meta):
        model = SEFNutritionGrantee
        fields = [
            'pg_member_assigned_code', 'pg_member_name', 'age', 'name', 'grant_received_year',
            'grant_received_month', 'contact_number',
            'relation_with_pg_member', 'is_still_pregnant_or_lactating', 'number_of_pregnancy_month',
            'age_of_child_in_month',
            'has_disability', 'difficulty_in_seeing', 'difficulty_in_hearing',
            'difficulty_in_walking', 'difficulty_in_remembering', 'difficulty_in_self_care',
            'difficulty_in_communicating', 'remarks'
        ]
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFNutritionGranteeForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['pg_member_assigned_code', 'pg_member_name', 'age', 'name', 'grant_received_year', 'grant_received_month',
             'contact_number', 'relation_with_pg_member', 'is_still_pregnant_or_lactating', 'number_of_pregnancy_month',
             'age_of_child_in_month', 'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking', 'difficulty_in_remembering',
             'difficulty_in_self_care', 'difficulty_in_communicating', 'has_disability']

        return _group
