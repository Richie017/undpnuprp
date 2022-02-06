"""
Created by tareq on 3/28/18
"""
import time

from django.core.management import BaseCommand

from undp_nuprp.nuprp_admin.models import CDC

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        t1 = time.time()
        CDC.objects.all().count()
        t2 = time.time()
        print(t2 - t1)
