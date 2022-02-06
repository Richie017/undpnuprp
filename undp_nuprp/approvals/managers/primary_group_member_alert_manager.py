"""
Created by tareq on 4/17/18
"""
import sys

from django.db.models import Max

from blackwidow.core.models import AlertGroup, Organization
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.alerts.duplicate_id_alert import DuplcateIdAlert
from undp_nuprp.reports.config.constants.values import BATCH_SIZE

__author__ = 'Tareq'


class PrimaryGroupMemberAlertManager(object):
    @classmethod
    def generate(cls, batch_count=None, batch_size=BATCH_SIZE):
        max_pg_member_id = cls.get_max_handled_pg_member_id()
        to_be_handled = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).order_by(
            'pk').filter(
            pk__gt=max_pg_member_id).count()
        if batch_count is None:
            batch_count = sys.maxsize
        batch = 0
        total_handled = 0
        last_id = max_pg_member_id

        alert_group, created = AlertGroup.objects.get_or_create(
            organization_id=Organization.get_organization_from_cache().pk,
            name='Duplicate PG Member Related')
        model_name = PrimaryGroupMember.__name__
        app_label = PrimaryGroupMember._meta.app_label
        alert_group_id = alert_group.pk

        while batch < batch_count:
            batch += 1
            print(
                'Handling batch #{}: (starting from {}) {}/{}'.format(batch, last_id, total_handled + batch_size,
                                                                      to_be_handled))
            handled, last_id = cls.handle_alert_creation(max_id=last_id, batch_size=batch_size, model_name=model_name,
                                                         app_label=app_label, alert_group_id=alert_group_id)
            total_handled += handled
            if handled < batch_size:
                break

    @classmethod
    def handle_alert_creation(cls, max_id=0, batch_size=BATCH_SIZE, model_name=None, app_label=None,
                              alert_group_id=None):
        pg_members = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).order_by(
            'pk').filter(pk__gt=max_id)[:batch_size]
        handled = 0
        for pgm in pg_members:
            max_id = pgm.pk

            pgm.create_alert_for_pg_member(object_id=max_id, alert_group_id=alert_group_id, app_label=app_label,
                                           model_name=model_name)
            handled += 1

        return handled, max_id

    @classmethod
    def get_max_handled_pg_member_id(cls):
        _obj_duplicate_id = DuplcateIdAlert.objects.using(BWDatabaseRouter.get_read_database_name()).aggregate(
            Max('object_id'))['object_id__max']
        if _obj_duplicate_id is None:
            _obj_duplicate_id = 0
        return _obj_duplicate_id
