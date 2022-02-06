from django import forms
from django.forms import modelformset_factory
from django.urls import reverse

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin import GenericModelFormSetMixin
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.forms import SEFGranteeForm
from undp_nuprp.approvals.forms import SEFInstallmentForm
from undp_nuprp.approvals.models import SEFApprenticeshipGrantee
from undp_nuprp.approvals.models import SEFInstallment
from undp_nuprp.nuprp_admin.models import TradeType, TradeSector

__author__ = 'Ziaul Haque'

contact_address_formset = modelformset_factory(
    SEFInstallment, form=SEFInstallmentForm, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True, can_delete=True
)


class SEFApprenticeshipGranteeForm(SEFGranteeForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFApprenticeshipGranteeForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs
        )

        self.fields['trade_sector'] = \
            GenericModelChoiceField(
                queryset=TradeSector.objects.all(), label='Sector',
                empty_label='Select One',
                initial=instance.trade_sector if instance else None,
                widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
            )

        self.fields['trade_type'] = GenericModelChoiceField(
            queryset=TradeType.objects.all(), label='Which Trade',
            initial=instance.trade_type if instance else None,
            widget=forms.TextInput(
                attrs={
                    'class': 'select2-input', 'width': '220',
                    'data-depends-on': 'trade_sector',
                    'data-depends-property': 'parent:id',
                    'data-url': reverse(TradeType.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                }
            )
        )

        self.fields['is_still_attending_training'] = forms.CharField(
            label='Is the grantee still attending the training?',
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
        model = SEFApprenticeshipGrantee
        fields = ('name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
                  'relation_with_pg_member', 'grantee_status', 'has_disability', 'difficulty_in_seeing',
                  'difficulty_in_hearing',
                  'difficulty_in_walking', 'difficulty_in_remembering', 'difficulty_in_self_care',
                  'difficulty_in_communicating', 'trade_sector', "trade_type", 'is_still_attending_training', 'remarks')
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFApprenticeshipGranteeForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['name', 'contact_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
             'relation_with_pg_member', 'trade_sector', 'trade_type', 'is_still_attending_training', 'grantee_status',
             'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking', 'difficulty_in_remembering',
             'difficulty_in_self_care', 'difficulty_in_communicating', 'has_disability']

        return _group
