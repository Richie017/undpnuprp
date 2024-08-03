from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from undp_nuprp.nuprp_admin.models import TownManager

__author__ = "Ziaul Haque"


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_names = ['john', 'shaheen', 'masum', 'iqbal', 'palash', 'jahirul', 'mousumi', 'swapan']
        auth_users = User.objects.filter(username__in=user_names)
        console_users = TownManager.objects.filter(user__username__in=user_names)
        _count = console_users.count()

        console_users.delete()
        auth_users.delete()

        print(str(_count) + " Item are deleted")
