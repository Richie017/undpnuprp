from django import forms

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.engine.exceptions import BWException
from undp_nuprp.approvals.models import SEFGrantee
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember

__author__ = 'Ziaul Haque'


class SEFGranteeForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFGranteeForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['name'].label = "Beneficiary's Name"

        self.fields['gender'] = forms.CharField(
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Male', 'Male'),
                    ('Female', 'Female'),
                    ('Hijra', 'Hijra'),
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
            label='PG Member ID', required=True
        )

        self.fields['pg_member_name'] = forms.CharField(label='PG member\'s name', required=True)

        self.fields['has_disability'] = forms.CharField(
            label='Has disability-PG Member',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Yes', 'Yes'),
                    ('No', 'No')
                )
            ),
            required=False
        )
        self.fields['has_disability_family'] = forms.CharField(
            label='Has disability-Family Member',
            widget=forms.Select(
                attrs={'class': 'select2', 'width': 'width'},
                choices=(
                    ('', 'Select One'),
                    ('Yes', 'Yes'),
                    ('No', 'No')
                )
            ),
            required=False
        )

        # self.fields['difficulty_in_seeing'] = forms.CharField(
        #     label='Difficulty seeing, even if wearing glasses',
        #     widget=forms.Select(
        #         attrs={'class': 'select2', 'width': 'width'},
        #         choices=(
        #             ('', 'Select One'),
        #             ('No difficulty', 'No difficulty'),
        #             ('Some difficulty', 'Some difficulty'),
        #             ('A lot of difficulty', 'A lot of difficulty'),
        #             ('Cannot do at all', 'Cannot do at all'),
        #         )
        #     )
        # )

        # self.fields['difficulty_in_hearing'] = forms.CharField(
        #     label='Difficulty hearing, even if using a hearing aid',
        #     widget=forms.Select(
        #         attrs={'class': 'select2', 'width': 'width'},
        #         choices=(
        #             ('', 'Select One'),
        #             ('No difficulty', 'No difficulty'),
        #             ('Some difficulty', 'Some difficulty'),
        #             ('A lot of difficulty', 'A lot of difficulty'),
        #             ('Cannot do at all', 'Cannot do at all'),
        #         )
        #     )
        # )

        # self.fields['difficulty_in_walking'] = forms.CharField(
        #     label='Difficulty walking or climbing steps',
        #     widget=forms.Select(
        #         attrs={'class': 'select2', 'width': 'width'},
        #         choices=(
        #             ('', 'Select One'),
        #             ('No difficulty', 'No difficulty'),
        #             ('Some difficulty', 'Some difficulty'),
        #             ('A lot of difficulty', 'A lot of difficulty'),
        #             ('Cannot do at all', 'Cannot do at all'),
        #         )
        #     )
        # )

        # self.fields['difficulty_in_remembering'] = forms.CharField(
        #     label='Difficulty remembering or concentrating',
        #     widget=forms.Select(
        #         attrs={'class': 'select2', 'width': 'width'},
        #         choices=(
        #             ('', 'Select One'),
        #             ('No difficulty', 'No difficulty'),
        #             ('Some difficulty', 'Some difficulty'),
        #             ('A lot of difficulty', 'A lot of difficulty'),
        #             ('Cannot do at all', 'Cannot do at all'),
        #         )
        #     )
        # )

        # self.fields['difficulty_in_self_care'] = forms.CharField(
        #     label='Difficulty with self-care such as washing all over or dressing',
        #     widget=forms.Select(
        #         attrs={'class': 'select2', 'width': 'width'},
        #         choices=(
        #             ('', 'Select One'),
        #             ('No difficulty', 'No difficulty'),
        #             ('Some difficulty', 'Some difficulty'),
        #             ('A lot of difficulty', 'A lot of difficulty'),
        #             ('Cannot do at all', 'Cannot do at all'),
        #         )
        #     )
        # )

        # self.fields['difficulty_in_communicating'] = forms.CharField(
        #     label='Difficulty communicating, for example understanding or being understood',
        #     widget=forms.Select(
        #         attrs={'class': 'select2', 'width': 'width'},
        #         choices=(
        #             ('', 'Select One'),
        #             ('No difficulty', 'No difficulty'),
        #             ('Some difficulty', 'Some difficulty'),
        #             ('A lot of difficulty', 'A lot of difficulty'),
        #             ('Cannot do at all', 'Cannot do at all'),
        #         )
        #     )
        # )

        self.fields['pg_member_name'] = forms.CharField(label='PG member\'s name', required=True)
        # self.fields['difficulty_in_seeing'].required = False
        # self.fields['difficulty_in_hearing'].required = False
        # self.fields['difficulty_in_walking'].required = False
        # self.fields['difficulty_in_remembering'].required = False
        # self.fields['difficulty_in_self_care'].required = False
        # self.fields['difficulty_in_communicating'].required = False

    def clean(self):
        cleaned_data = super(SEFGranteeForm, self).clean()

        if 'pg_member_assigned_code' in cleaned_data:
            pg_member_assigned_code = cleaned_data['pg_member_assigned_code'].strip('\'')
            if not PrimaryGroupMember.objects.filter(assigned_code=pg_member_assigned_code).exists():
                pg_member_assigned_code = '0' + pg_member_assigned_code
                if not PrimaryGroupMember.objects.filter(assigned_code=pg_member_assigned_code).exists():
                    raise BWException("Primary Group Member with this Assigned Code doesn't exists.")
            cleaned_data['pg_member_assigned_code'] = pg_member_assigned_code
        return cleaned_data

    def save(self, commit=True):
        _assigned_code = self.cleaned_data['pg_member_assigned_code']
        self.instance.pg_member_id = PrimaryGroupMember.objects.filter(assigned_code=_assigned_code).first().id
        self.instance.ward = _assigned_code[3:5] if len(_assigned_code) > 4 else ""
        if len(self.instance.ward) == 1:
            self.instance.ward = "0" + str(self.instance.ward)
        return super(SEFGranteeForm, self).save(commit=commit)

    class Meta(GenericFormMixin.Meta):
        model = SEFGrantee
        fields = ('name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
                  'relation_with_pg_member', 'has_disability', 'difficulty_in_seeing',
                  'difficulty_in_hearing',
                  'difficulty_in_walking', 'difficulty_in_remembering', 'difficulty_in_self_care',
                  'difficulty_in_communicating', 'remarks')
        widgets = {
            'remarks': forms.Textarea
        }
