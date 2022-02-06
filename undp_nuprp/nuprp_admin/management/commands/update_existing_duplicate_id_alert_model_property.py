from django.core.management.base import BaseCommand

from undp_nuprp.nuprp_admin.models import DuplcateIdAlert
from undp_nuprp.nuprp_admin.models.alerts.duplicate_id_alert import DuplicateIDAlertEnum

__author__ = 'Ziaul Haque'


class Command(BaseCommand):
    def handle(self, *args, **options):
        alert_for_duplicate_assigned_code = DuplcateIdAlert.objects.filter(
            model='PrimaryGroupMember', model_property='assigned_code'
        )
        _count = alert_for_duplicate_assigned_code.count()
        print("Updating %d alerts for duplicate PG Member ID..." % _count)
        alert_for_duplicate_assigned_code.update(model_property=DuplicateIDAlertEnum.assigned_code.value)
        print("Updated...")

        alert_for_duplicate_phone_number = DuplcateIdAlert.objects.filter(
            model='PrimaryGroupMember', model_property='phone_number.phone'
        )
        _count = alert_for_duplicate_phone_number.count()
        print("Updating %d alerts for duplicate Phone Number..." % _count)
        alert_for_duplicate_phone_number.update(model_property=DuplicateIDAlertEnum.phone_number.value)
        print("Updated...")

        alert_for_duplicate_national_id = DuplcateIdAlert.objects.filter(
            model='PrimaryGroupMember', model_property='client_meta.national_id'
        )
        _count = alert_for_duplicate_national_id.count()
        print("Updating %d alerts for duplicate National ID..." % _count)
        alert_for_duplicate_national_id.update(model_property=DuplicateIDAlertEnum.national_id.value)
        print("Updated...")
