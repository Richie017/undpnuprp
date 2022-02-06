import csv
import os
from datetime import datetime

from django.core.management import BaseCommand
from django.db.models import Q

from blackwidow.core.models import Geography, Organization
from settings import STATIC_ROOT
from undp_nuprp.approvals.models import WordPrioritizationIndicator


class Command(BaseCommand):

    @classmethod
    def load_data_from_csv(cls, csv_path):
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            data = []
            for row in csv_reader:
                data.append(row)
            return data

    @staticmethod
    def to_int(value, default):
        int_ = value
        try:
            int_ = int(int_)
        except:
            return default
        return int_

    def handle(self, *args, **options):
        self.import_indicators_data()

    @classmethod
    def import_indicators_data(cls):
        filepath = os.path.join(STATIC_ROOT, 'data', 'word_prioritization_indicator_v3.csv')
        data_rows = cls.load_data_from_csv(filepath)[1:]

        cities = [
            "Barisal", "Chandpur", "Chittagong city corporation", "Cumilla", "DNCC", "Faridpur", "Gazipur",
            "Gopalganj", "Khulna", "Kushtia", "Mymensingh", "Noakhali", "Patuakhali", "Rangpur", "Saidpur",
            "Narayanganj",
            "Cox's Bazar",
            "Dhaka South",
            "Rajshahi",
            "Sylhet City Corporation"
        ]

        queryset = Geography.objects.filter(
            parent__name__in=cities,
            level__name="Ward"
        )

        organization = Organization.objects.filter(is_master=True).first()
        current_timestamp = int(datetime.now().timestamp()) * 1000
        creatable_list = list()
        for index, row in enumerate(data_rows, 1):
            city = row[0]
            ward = row[1]
            geography = queryset.filter(
                Q(name__iexact=ward) | Q(name__iexact=ward.zfill(2)),
                parent__name__iexact=city
            ).first()
            if geography:
                print("Importing data, city - {0}, ward - {1}".format(city, ward))
                _indicator_object = WordPrioritizationIndicator(
                    Ward=geography,
                    poverty_index_score=cls.to_int(row[2], 0),
                    poverty_index_quantile=cls.to_int(row[3], 0),
                    infrastructure_index_score=cls.to_int(row[4], 0),
                    infrastructure_index_quantile=cls.to_int(row[5], 0),
                    livelihood_index_score=cls.to_int(row[6], 0),
                    livelihood_index_quantile=cls.to_int(row[7], 0),
                    land_tenure_and_housing_index_score=cls.to_int(row[8], 0),
                    land_tenure_and_housing_index_quantile=cls.to_int(row[9], 0),
                    total_population=cls.to_int(row[10], 0),
                    organization=organization,
                    date_created=current_timestamp,
                    last_updated=current_timestamp
                )
                current_timestamp += 1
                creatable_list.append(_indicator_object)
            else:
                print("Not found, city - {0}, ward - {1}".format(city, ward))

        # delete existing items first
        print("{} items deleted".format(WordPrioritizationIndicator.objects.all().delete()))

        print(str(len(creatable_list)) + ' ' + 'Objects are being created')
        WordPrioritizationIndicator.objects.bulk_create(creatable_list)
        print("Successfully created")
