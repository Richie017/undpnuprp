import csv
import json
import os
from datetime import datetime

from django.core.management import BaseCommand

from blackwidow.core.models import Geography, Organization
from blackwidow.core.models.geography.geography_level import GeographyLevel
from settings import STATIC_ROOT


class Command(BaseCommand):

    @classmethod
    def load_data_from_csv(cls, csv_path):
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            data = []
            for row in csv_reader:
                data.append(row)
            return data

    def handle(self, *args, **options):
        cities = [
            # "Cumilla", "DNCC", "Faridpur", "Gazipur", "Gopalganj", "Kushtia", "Noakhali", "Patuakhali",
            # "Saidpur", "Chittagong city corporation",

            "Narayanganj",
            "Cox's Bazar",
            "Dhaka South",
            "Rajshahi",
            "Sylhet City Corporation"
        ]

        organization = Organization.objects.filter(is_master=True).first()
        geography_level = GeographyLevel.objects.filter(name='Poor Settlement').values('id', 'name').first()
        mahalla_level = GeographyLevel.objects.filter(name='Mahalla').values('id', 'name').first()
        current_timestamp = int(datetime.now().timestamp()) * 1000
        for city in cities:
            print("generating Poor Settlement, city - {0}".format(city))
            filename = city.replace(' ', '_').replace("'", "555") + '_Poor_Settlement.json'
            file_path = os.path.join(STATIC_ROOT, 'data', filename)
            json_object = json.loads(open(file_path, 'r').read())
            data_rows = json_object['features']

            poor_settlement_queryset = Geography.objects.filter(
                parent__parent__parent__name__iexact=city,
                level__name="Poor Settlement"
            ).values('parent__parent__name', 'parent__name', 'name')
            poor_settlement_list = [
                (item['parent__parent__name'].lower(), item['parent__name'].lower(), item['name'].lower()) for item in
                poor_settlement_queryset
            ]

            mahalla_queryset = Geography.objects.filter(
                parent__parent__name__iexact=city,
                level__name="Mahalla"
            ).values('id', 'name', 'parent__name')

            mahalla_dict = {(item['parent__name'].lower(), item['name'].lower()): item['id'] for item in
                            mahalla_queryset}

            ward_queryset = Geography.objects.filter(
                parent__name__iexact=city,
                level__name="Ward"
            ).values('id', 'name')
            ward_dict = {item['name'].lower(): item['id'] for item in ward_queryset}

            creatable_list = list()
            for row in data_rows:
                ward_name = str(row['properties']['ward'])
                mahalla_name = row['properties']['mahalla_na']
                poor_settlement_name = row['properties']['settl_nam']
                if (ward_name, mahalla_name.lower(), poor_settlement_name.lower()) in poor_settlement_list \
                        or (
                ward_name.zfill(2), mahalla_name.lower(), poor_settlement_name.lower()) in poor_settlement_list:
                    continue

                mahalla_id = mahalla_dict.get((ward_name, mahalla_name.lower())) or \
                             mahalla_dict.get(((ward_name.zfill(2)), mahalla_name.lower()))

                ward_id = ward_dict.get(ward_name) or ward_dict.get(ward_name.zfill(2))
                if not mahalla_id and ward_id:
                    _geography = Geography(
                        name=mahalla_name,
                        parent_id=ward_id,
                        level_id=mahalla_level['id'],
                        type=mahalla_level['name'],
                        organization=organization,
                        date_created=current_timestamp,
                        last_updated=current_timestamp
                    )
                    print("mahalla created. {}".format(_geography))
                    _geography.save()
                    mahalla_dict[(_geography.parent.name, _geography.name.lower())] = _geography.pk
                    mahalla_id = _geography.pk

                if mahalla_id:
                    _geography = Geography(name=poor_settlement_name, parent_id=mahalla_id,
                                           level_id=geography_level['id'],
                                           type=geography_level['name'], organization=organization,
                                           date_created=current_timestamp, last_updated=current_timestamp)
                    current_timestamp += 1
                    creatable_list.append(_geography)
                else:
                    print((ward_name, mahalla_name, poor_settlement_name))
            print(str(len(creatable_list)) + ' ' + 'geographies are being created')
            Geography.objects.bulk_create(creatable_list)
            print("Successfully created")

        # need to handle Rangpur city seperately as we are using different file format here
        # self.generate_rangpur_poor_settlement_geography(organization, geography_level, current_timestamp)

    @classmethod
    def generate_rangpur_poor_settlement_geography(cls, organization, geography_level, current_timestamp):
        city_name = 'Rangpur'
        print("generating Poor Settlement, city - {0}".format(city_name))
        filename = str(city_name) + '_Poor_Settlement.csv'
        filepath = os.path.join(STATIC_ROOT, 'data', filename)
        data_rows = cls.load_data_from_csv(filepath)[1:]

        poor_settlement_queryset = Geography.objects.filter(
            parent__parent__parent__name__iexact=city_name,
            level__name="Poor Settlement"
        ).values('parent__parent__name', 'parent__name', 'name')
        poor_settlement_list = [(item['parent__parent__name'], item['parent__name'], item['name']) for item in
                                poor_settlement_queryset]
        mahalla_queryset = Geography.objects.filter(
            parent__parent__name__iexact=city_name,
            level__name="Mahalla"
        ).values('id', 'name', 'parent__name')
        mahalla_dict = {(item['parent__name'], item['name']): item['id'] for item in mahalla_queryset}

        creatable_list = list()
        for row in data_rows:
            ward_name = str(row[0])
            mahalla_name = str(row[1])
            poor_settlement_name = str(row[2])
            if (ward_name, mahalla_name, poor_settlement_name) in poor_settlement_list \
                    or (ward_name.zfill(2), mahalla_name, poor_settlement_name) in poor_settlement_list:
                continue
            mahalla_id = mahalla_dict.get((ward_name, mahalla_name)) or \
                         mahalla_dict.get(((ward_name.zfill(2)), mahalla_name))
            if mahalla_id:
                _geography = Geography(name=poor_settlement_name, parent_id=mahalla_id,
                                       level_id=geography_level['id'],
                                       type=geography_level['name'], organization=organization,
                                       date_created=current_timestamp, last_updated=current_timestamp)
                current_timestamp += 1
                creatable_list.append(_geography)
        print(str(len(creatable_list)) + ' ' + 'geographies are being created')
        Geography.objects.bulk_create(creatable_list)
        print("Successfully created")
