"""
Created by tareq on 3/28/18
"""
from blackwidow.core.models import AlertGroup, Organization
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember

__author__ = 'Tareq'


class PGMemberAlertManager(object):
    @classmethod
    def prepare_alert_group(self):
        alert_group, created = AlertGroup.objects.get_or_create(
            organization_id=Organization.objects.first().pk,
            name='Duplicate PG Member Related')
        model_name = PrimaryGroupMember.__name__
        app_label = PrimaryGroupMember._meta.app_label
        alert_group_id = alert_group.pk

        return alert_group_id, model_name, app_label
    # @classmethod
    # def create_alert_for_duplicate_id(cls, alert_group_id, model_name, app_label, last_run_time=0):
    #     try:
    #         duplicate_id = PrimaryGroupMember.objects.filter(
    #             assigned_code=self.assigned_code
    #         ).exclude(pk=self.pk).last()
    #
    #         is_duplicate_id = duplicate_id is not None
    #
    #         if is_duplicate_id:
    #             model_property = 'assigned_code'
    #             record = DuplcateIdAlert.objects.filter(
    #                 alert_group_id=alert_group_id, model=model_name, app_label=app_label,
    #                 object_id=object_id, model_property=model_property
    #             ).order_by('pk').last()
    #
    #             if record is None:
    #                 record = DuplcateIdAlert()
    #                 record.organization_id = self.organization_id
    #                 record.alert_group_id = alert_group_id
    #                 record.model = model_name
    #                 record.app_label = app_label
    #                 record.object_id = object_id
    #                 record.model_property = model_property
    #                 if is_duplicate_id:
    #                     record.body = 'PG Member' + '\'s ID is ' + \
    #                                   str(self.assigned_code) + ', which is already the ID of, ' + \
    #                                   str(duplicate_id)
    #                     self.is_duplicate_id = True
    #                     record.save()
    #                 else:
    #                     self.is_duplicate_id = False
    #     except Exception as exp:
    #         ErrorLog.log(exp)
