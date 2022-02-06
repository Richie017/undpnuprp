"""
    Created by tareq on 10/2/19
"""
from django.core.management import BaseCommand

from blackwidow.core.models import ConsoleUser
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember

__author__ = "Tareq"


class Command(BaseCommand):
    def handle(self, *args, **options):
        deletable_members = PrimaryGroupMember.objects.filter(surveyresponse__isnull=True)

        deletable_counts = deletable_members.count()
        user = ConsoleUser.objects.filter(is_super=True).first()
        index = 0
        for m in deletable_members:
            m.soft_delete(force_delete=True, user=user)
            print("deleted {}/{}".format(index, deletable_counts))
            index += 1

        print("Deleted {}".format(index, ))
        return
