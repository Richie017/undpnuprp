"""
Created by tareq on 4/20/17
"""
from django.core.management.base import BaseCommand

from undp_nuprp.nuprp_admin.models.users.enumerator import Enumerator

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        for enumerator in Enumerator.objects.filter(assigned_code__isnull=True):
            try:
                ward = enumerator.addresses.first().geography
                city = ward.parent
                index = Enumerator.all_objects.filter(addresses__geography_id=ward.pk,
                                                      id__lte=enumerator.pk).count()
                ward_name = ward.name
                if len(ward.name) < 2:
                    ward_name = '0' + ward.name
                elif len(ward.name) > 2:
                    ward_name = ward.name[:2]
                city_name = city.short_code
                enumerator.assigned_code = '%2s%2s%02d' % (city_name, ward_name, index)
                enumerator.save()

                print('%s - %s' % (enumerator.assigned_code, enumerator.name))
            except:
                print("Canno generate for %s" % enumerator.name)
