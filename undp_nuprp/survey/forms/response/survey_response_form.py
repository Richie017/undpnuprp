from django import forms
from django.db import transaction

from undp_nuprp.survey.models import SurveyResponse
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = 'Tareq'


class SurveyResponseForm(GenericFormMixin):
    pg_member_id = forms.CharField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SurveyResponseForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        _initial_pg_member_id = None
        if instance:
            _initial_pg_member = instance.respondent_client
            if _initial_pg_member:
                _initial_pg_member_id = _initial_pg_member.assigned_code

        self.fields['pg_member_id'] = forms.CharField(
            label='PG Member ID',
            initial=_initial_pg_member_id
        )

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super(SurveyResponseForm, self).save(commit)
            self.instance.respondent_client.assigned_code = self.cleaned_data['pg_member_id']
            self.instance.save()
            pg_member_id = self.instance.respondent_client.pk
            pg_member = PrimaryGroupMember.objects.filter(pk=pg_member_id).first()
            if pg_member:
                pg_member.assigned_code = self.instance.respondent_client.assigned_code
                pg_member.save()
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = SurveyResponse
        fields = ['pg_member_id', ]
