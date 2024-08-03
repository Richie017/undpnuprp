from django import forms
from django.forms.models import modelformset_factory

from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.engine.exceptions.exceptions import BWException
from undp_nuprp.approvals.forms.sef_grant_instalment.sef_grant_instalment_form import SEFGrantInstalmentForm
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_disbursement import SEFGrantDisbursement
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_grant_instalment import SEFGrantInstalment
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = 'Shuvro'

instalment_formset = modelformset_factory(
    SEFGrantInstalment, form=SEFGrantInstalmentForm, formset=GenericModelFormSetMixin, validate_min=True,
    can_delete=True
)


class SEFGrantDisbursementForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SEFGrantDisbursementForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                       **kwargs)

        if instance and instance.pk:
            installment_objects = instance.instalments.all()
        else:
            installment_objects = SEFGrantInstalment.objects.none()

        self.fields['pg_member_name'] = forms.CharField(label='PG member\'s name', required=False)

        self.add_child_form("instalments", instalment_formset(
            data=data, files=files, queryset=installment_objects, prefix='instalments', header='Instalments',
            add_more=True, **kwargs
        ))

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
        super(SEFGrantDisbursementForm, self).save(commit=True)
        _assigned_code = self.cleaned_data['pg_member_assigned_code']
        self.instance.pg_member_id = PrimaryGroupMember.objects.filter(assigned_code=_assigned_code).first().id
        _city = self.instance.pg_member.assigned_to.parent.address.geography.parent.name
        _cdc = self.instance.pg_member.assigned_to.parent
        self.instance.assigned_city = _city
        self.instance.cdc = _cdc
        self.instance.save()
        return self.instance

    class Meta(GenericFormMixin.Meta):
        model = SEFGrantDisbursement
        fields = 'name', 'pg_member_assigned_code', 'pg_member_name', 'account_number'
        labels = {
            'name': 'Beneficiary name',
            'pg_member_assigned_code': 'PG member\'s ID',
            'pg_member_name': 'PG member\'s name',
            'account_number': 'Rocket account number'
        }
