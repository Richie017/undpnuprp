import json
import os
from datetime import datetime

from django.core.management import BaseCommand

from blackwidow.core.models import Geography, Organization
from blackwidow.core.models.geography.geography_level import GeographyLevel
from settings import STATIC_ROOT


class Command(BaseCommand):

    def handle(self, *args, **options):
        cities = [
            # "Cumilla", "DNCC", "Faridpur", "Gazipur", "Gopalganj", "Kushtia", "Noakhali", "Patuakhali", "Rangpur",
            # "Saidpur", "Chittagong city corporation",

            "Narayanganj",
            "Cox's Bazar",
            "Dhaka South",
            "Rajshahi",
            "Sylhet City Corporation"
        ]
        organization = Organization.objects.filter(is_master=True).first()
        geography_level = GeographyLevel.objects.filter(name='Mahalla').values('id', 'name').first()
        current_timestamp = int(datetime.now().timestamp()) * 1000
        for city in cities:
            print("generating Mahalla, city - {0}".format(city))
            filename = city.replace(' ', '_').replace("'", "555") + '_Mahalla.json'
            file_path = os.path.join(STATIC_ROOT, 'data', filename)
            json_object = json.loads(open(file_path, 'r').read())
            data_rows = json_object['features']

            mahalla_queryset = Geography.objects.filter(
                parent__parent__name__iexact=city,
                level__name="Mahalla"
            ).values('parent__name', 'name')
            mahalla_list = [(item['parent__name'], item['name']) for item in mahalla_queryset]

            ward_queryset = Geography.objects.filter(
                parent__name__iexact=city,
                level__name="Ward"
            ).values('id', 'name')

            wards_dict = {item['name']: item['id'] for item in ward_queryset}

            creatable_list = list()
            for row in data_rows:
                mahalla_name = row['properties']['Mahalla_Na']
                ward_name = str(row['properties']['Ward_No'])
                if (ward_name, mahalla_name) in mahalla_list or (ward_name.zfill(2), mahalla_name) \
                        in mahalla_list:
                    continue
                ward_id = wards_dict.get(ward_name) or wards_dict.get(ward_name.zfill(2))
                if ward_id:
                    _geography = Geography(name=mahalla_name, parent_id=ward_id, level_id=geography_level['id'],
                                           type=geography_level['name'], organization=organization,
                                           date_created=current_timestamp, last_updated=current_timestamp)
                    current_timestamp += 1
                    creatable_list.append(_geography)
            print(str(len(creatable_list)) + ' ' + 'geographies are being created')
            Geography.objects.bulk_create(creatable_list, batch_size=1000)
            print("Successfully created")
