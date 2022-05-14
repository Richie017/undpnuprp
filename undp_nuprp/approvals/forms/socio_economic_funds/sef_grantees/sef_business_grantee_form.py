from django import forms
from django.forms import modelformset_factory
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericModelFormSetMixin
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.forms import SEFGranteeForm
from undp_nuprp.approvals.forms import SEFInstallmentForm
from undp_nuprp.approvals.models import SEFBusinessGrantee
from undp_nuprp.approvals.models import SEFInstallment
from undp_nuprp.nuprp_admin.models import BusinessSector, BusinessType

__author__ = 'Ziaul Haque'

contact_address_formset = modelformset_factory(
    SEFInstallment, form=SEFInstallmentForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)


class SEFBusinessGranteeForm(SEFGranteeForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFBusinessGranteeForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        # if instance and instance.pk:
        #     installment_objects = instance.installments.all()
        # else:
        #     installment_objects = SEFInstallment.objects.none()

        self.fields['business_sector'] = GenericModelChoiceField(
                queryset=BusinessSector.objects.all(), label='Sector',
                empty_label='Select One',
                initial=instance.business_sector if instance else None,
                widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
            )

        self.fields['type_of_business'] = GenericModelChoiceField(
            queryset=BusinessType.objects.all(), label='Sub Sector',
            initial=instance.type_of_business if instance else None,
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

        # self.add_child_form("installments", contact_address_formset(
        #     data=data, files=files, queryset=installment_objects,
        #     header='Instalment', add_more=False, **kwargs
        # ))

    class Meta(GenericFormMixin.Meta):
        model = SEFBusinessGrantee
        fields = ('name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
                  'relation_with_pg_member', 'grantee_status', 'has_disability',
                  'business_sector', "type_of_business", 'remarks')
        # fields = ('name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
        #           'relation_with_pg_member', 'grantee_status', 'has_disability', 'difficulty_in_seeing',
        #           'difficulty_in_hearing',
        #           'difficulty_in_walking', 'difficulty_in_remembering', 'difficulty_in_self_care',
        #           'difficulty_in_communicating', 'business_sector', "type_of_business", 'remarks')
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFBusinessGranteeForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
             'relation_with_pg_member', 'business_sector', 'type_of_business', 'grantee_status', 'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['has_disability', 'has_disability_family']
        # _group['Grantee\'s Disability Status'] = \
        #     ['has_disability', 'difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking',
        #      'difficulty_in_remembering', 'difficulty_in_self_care', 'difficulty_in_communicating']

        return _group
