import csv
import os
from datetime import datetime

from django.core.management import BaseCommand
from django.db.models import Q

from blackwidow.core.models import Geography, Organization
from settings import STATIC_ROOT
from undp_nuprp.approvals.models.interactive_maps.output_one.urban_poor_settlement_indicator import \
    UrbanPoorSettlementIndicator


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
        cities = [
            # "Barisal", "Chandpur", "Chittagong city corporation", "Cumilla", "DNCC", "Faridpur", "Gazipur",
            # "Gopalganj", "Khulna", "Kushtia", "Mymensingh", "Noakhali", "Patuakhali", "Rangpur", "Saidpur",

            "Narayanganj",
            "Cox's Bazar",
            "Dhaka South",
            "Rajshahi",
            "Sylhet City Corporation"
        ]
        for city in cities:
            self.import_city_wise_data(city_name=city)

    @classmethod
    def import_city_wise_data(cls, city_name):
        print("Importing data, city - {0}".format(city_name))
        filename = city_name.replace(' ', '_').replace("'", "555") + '_Indicator.csv'
        filepath = os.path.join(STATIC_ROOT, 'data', filename)
        data_rows = cls.load_data_from_csv(filepath)[1:]

        queryset = Geography.objects.filter(
            parent__parent__parent__name__iexact=city_name,
            level__name="Poor Settlement"
        )
        organization = Organization.objects.filter(is_master=True).first()
        current_timestamp = int(datetime.now().timestamp()) * 1000
        creatable_list = list()
        for row in data_rows:
            ward = row[1]
            settlement_name = row[5]
            geography = queryset.filter(
                Q(parent__parent__name__iexact=ward) | Q(parent__parent__name__iexact=ward.zfill(2)),
                name__iexact=settlement_name
            ).first()
            if geography:
                has_indicator = UrbanPoorSettlementIndicator.objects. \
                    filter(settlement=geography).exists()
                if has_indicator:
                    continue
                _indicator_object = UrbanPoorSettlementIndicator(
                    settlement=geography,
                    household=cls.to_int(row[6], 0),
                    population=cls.to_int(row[7], 0),
                    settlement_age=cls.to_int(row[8], 0),
                    condition_of_access_road=cls.to_int(row[9], 0),
                    availability_of_drain=cls.to_int(row[10], 0),
                    electricity_coverage=cls.to_int(row[11], 0),
                    solid_waste_collection_service=cls.to_int(row[12], 0),
                    access_to_piped_water_supply=cls.to_int(row[13], 0),
                    availability_of_hygienic_toilet=cls.to_int(row[14], 0),
                    street_lighting=cls.to_int(row[15], 0),
                    attendance_of_children_at_school=cls.to_int(row[16], 0),
                    households_with_employment=cls.to_int(row[17], 0),
                    household_income=cls.to_int(row[18], 0),
                    social_problem=cls.to_int(row[19], 0),
                    land_tenure_security=cls.to_int(row[20], 0),
                    housing_condition=cls.to_int(row[21], 0),
                    risk_of_eviction=cls.to_int(row[22], 0),
                    land_ownership=cls.to_int(row[23], 0),
                    type_of_occupancy=cls.to_int(row[24], 0),
                    total_score=cls.to_int(row[25], 0),
                    organization=organization,
                    date_created=current_timestamp,
                    last_updated=current_timestamp
                )
                current_timestamp += 1
                creatable_list.append(_indicator_object)
        print(str(len(creatable_list)) + ' ' + 'Objects are being created')
        UrbanPoorSettlementIndicator.objects.bulk_create(creatable_list)
        print("Successfully created")
