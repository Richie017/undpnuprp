from django import forms
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.approvals.forms.savings_and_credits.sef_grant_disbursement.sef_grant_disbursement_form import \
    SEFGrantDisbursementForm
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_apprenticeship_grant_disbursement import \
    SEFApprenticeshipGrantDisbursement
from undp_nuprp.nuprp_admin.models.descriptors.trade_sector import TradeSector
from undp_nuprp.nuprp_admin.models.descriptors.trade_type import TradeType

__author__ = 'Shuvro'


class SEFApprenticeshipGrantDisbursementForm(SEFGrantDisbursementForm):
    trade_sector = forms.IntegerField()
    trade_type = forms.IntegerField()
    is_still_attending_training = forms.CharField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFApprenticeshipGrantDisbursementForm, self).__init__(
            data=data, files=files, instance=instance.sefapprenticeshipgrantee if instance else None,
            prefix=prefix,
            **kwargs
        )

        self.fields['trade_sector'] = \
            GenericModelChoiceField(
                queryset=TradeSector.objects.all(), label='Sector',
                empty_label='Select One',
                initial=instance.sefapprenticeshipgrantee.trade_sector if instance else None,
                widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
            )

        self.fields['trade_type'] = GenericModelChoiceField(
            queryset=TradeType.objects.all(), label='Which Trade',
            initial=instance.sefapprenticeshipgrantee.trade_type if instance else None,
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

    class Meta(GenericFormMixin.Meta):
        model = SEFApprenticeshipGrantDisbursement
        fields = (
            'name', 'contact_number', 'account_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
            'relation_with_pg_member', 'difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking',
            'difficulty_in_remembering', 'difficulty_in_self_care', 'difficulty_in_communicating', 'trade_sector',
            "trade_type", 'is_still_attending_training', 'remarks'
        )

        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(SEFApprenticeshipGrantDisbursementForm, cls).field_groups()
        _group['Grantee\'s Basic Information'] = \
            ['name', 'contact_number', 'account_number', 'age', 'gender', 'pg_member_assigned_code', 'pg_member_name',
             'relation_with_pg_member', 'trade_sector', 'trade_type', 'is_still_attending_training', 'remarks']

        _group['Grantee\'s Disability Status'] = \
            ['difficulty_in_seeing', 'difficulty_in_hearing', 'difficulty_in_walking', 'difficulty_in_remembering',
             'difficulty_in_self_care', 'difficulty_in_communicating']

        return _group
