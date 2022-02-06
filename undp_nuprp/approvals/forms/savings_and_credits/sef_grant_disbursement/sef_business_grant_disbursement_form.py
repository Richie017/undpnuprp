from django import forms
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.forms.savings_and_credits.sef_grant_disbursement.sef_grant_disbursement_form import \
    SEFGrantDisbursementForm
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_business_grant_disbursement import \
    SEFBusinessGrantDisbursement
from undp_nuprp.nuprp_admin.models.descriptors.business_sector import BusinessSector
from undp_nuprp.nuprp_admin.models.descriptors.business_type import BusinessType

__author__ = 'Shuvro'


class SEFBusinessGrantDisbursementForm(SEFGrantDisbursementForm):
    business_sector = forms.IntegerField()
    type_of_business = forms.IntegerField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFBusinessGrantDisbursementForm, self).__init__(data=data, files=files,
                                                               instance=instance.sefbusinessgrantee if instance else None,
                                                               prefix=prefix,
                                                               **kwargs)

        self.fields['business_sector'] = \
            GenericModelChoiceField(
                queryset=BusinessSector.objects.all(), label='Sector',
                empty_label='Select One',
                initial=instance.sefbusinessgrantee.business_sector if instance else None,
                widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
            )

        self.fields['type_of_business'] = GenericModelChoiceField(
            queryset=BusinessType.objects.all(), label='Sub Sector',
            initial=instance.sefbusinessgrantee.type_of_business if instance else None,
            widget=forms.TextInput(
                attrs={
                    'class': 'select2-input', 'width': '220',
                    'data-depends-on': 'business_sector',
                    'data-depends-property': 'parent:id',
                    'data-url': reverse(BusinessType.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                }
            )
        )

    class Meta(GenericFormMixin.Meta):
        model = SEFBusinessGrantDisbursement
        fields = ('name', 'contact_number', 'account_number',
                  'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
                  'relation_with_pg_member', 'difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking',
                  'difficulty_in_remembering', 'difficulty_in_self_care', 'difficulty_in_communicating',
                  'business_sector', "type_of_business", 'remarks')

        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFBusinessGrantDisbursementForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['name', 'contact_number', 'account_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
             'relation_with_pg_member', 'business_sector', 'type_of_business', 'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking', 'difficulty_in_remembering',
             'difficulty_in_self_care', 'difficulty_in_communicating']

        return _group
