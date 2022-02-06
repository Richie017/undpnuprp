import csv
import json
import os

from django.contrib.postgres.search import TrigramSimilarity
from django.core.management import BaseCommand
from django.db.models import Q

from blackwidow.core.models import Geography
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
        # prepare mapping file only for those cities in the production server which has no mahalla
        cities = [
            # "Cumilla", "DNCC", "Faridpur", "Gazipur", "Gopalganj", "Kushtia", "Noakhali", "Patuakhali", "Rangpur",
            # "Saidpur", "Chittagong city corporation",

            "Narayanganj",
            "Cox's Bazar",
            "Dhaka South",
            "Rajshahi",
            "Sylhet City Corporation"
        ]
        for city in cities:
            self.generate_mahalla_likelihood_estimation(city_name=city)
            # if city == "Rangpur":
            #     self.generate_csv_for_rangpur_poor_settlement()
            # else:
            #     self.generate_poor_settlement_likelihood_estimation(city_name=city)
            self.generate_poor_settlement_likelihood_estimation(city_name=city)

    @classmethod
    def generate_ward_likelihood_estimation(cls, city_name):
        print("generating likelihood estimation of ward, city - {0}".format(city_name))
        filename = city_name.replace(' ', '_') + '_ward.csv'
        filepath = os.path.join(STATIC_ROOT, 'data', filename)
        generated_filepath = os.path.join(STATIC_ROOT, 'data', 'mapping_of_' + filename)
        header = cls.load_data_from_csv(filepath)[0]
        data_rows = cls.load_data_from_csv(filepath)[1:]

        queryset = Geography.objects.filter(
            parent__name__iexact=city_name,
            level__name="Ward",
        )

        if city_name in ["chandpur", "barisal", ]:
            queryset = queryset.filter(geography__isnull=False)

        csv_file = open(generated_filepath, "w", encoding='utf-8')
        csv_file.write(
            "{0};{1};{2};{3}\n".format(
                ";".join(header, ),
                "Ward-ID (DB)",
                "Ward Name (DB)",
                "Similarity (%)"
            ))
        for row in data_rows:
            ward_name = row[0]
            geography = queryset.annotate(
                similarity=TrigramSimilarity('name', ward_name),
            ).filter(similarity__gt=0).order_by('-similarity').values('id', 'name', 'similarity').first()

            csv_file.write(
                "{0};{1};{2};{3}\n".format(
                    ";".join(row, ),
                    geography['id'] if geography else "",
                    geography['name'] if geography else "",
                    round(geography["similarity"], 2) * 100 if geography else ""
                ))

        csv_file.close()
        print("completed...")

    @classmethod
    def generate_mahalla_likelihood_estimation(cls, city_name):
        print("generating likelihood estimation of mahalla, city - {0}".format(city_name))
        filename = city_name.replace(' ', '_').replace("'", "555") + '_Mahalla.json'
        file_path = os.path.join(STATIC_ROOT, 'data', filename)
        generated_filepath = os.path.join(STATIC_ROOT, 'data',
                                          'mapping_of_' + city_name.replace(' ', '_').replace("'", "555") + '_Mahalla.csv')

        json_object = json.loads(open(file_path, 'r').read())
        data_rows = json_object['features']

        queryset = Geography.objects.filter(
            parent__parent__name__iexact=city_name,
            level__name="Mahalla"
        )

        csv_file = open(generated_filepath, "w", encoding='utf-8')
        csv_file.write(
            "{0};{1};{2};{3};{4};{5};{6}\n".format(
                "Mahalla Name",
                "Mahalla-ID (DB)",
                "Mahalla Name (DB)",
                "Ward-ID (DB)",
                "Ward Name (DB)",
                "Similarity (%)",
                "Coordinates"
            ))
        for row in data_rows:
            coordinates = ''
            if row['geometry']:
                coordinates = row['geometry']
            mahalla_name = row['properties']['Mahalla_Na']
            ward = str(row['properties']['Ward_No'])
            geography = queryset.filter(
                Q(parent__name__iexact=ward) | Q(parent__name__iexact=ward.zfill(2))
            ).annotate(similarity=TrigramSimilarity('name', mahalla_name),
                       ).filter(similarity__gt=0).order_by('-similarity').values(
                'id', 'name', 'parent_id', 'parent__name', 'similarity'
            ).first()

            if mahalla_name:
                csv_file.write(
                    "{0};{1};{2};{3};{4};{5};{6}\n".format(
                        mahalla_name,
                        geography['id'] if geography else "",
                        geography['name'] if geography else "",
                        geography['parent_id'] if geography else "",
                        geography['parent__name'] if geography else "",
                        round(geography["similarity"], 2) * 100 if geography else "",
                        coordinates if geography else ""
                    ))

        csv_file.close()
        print("completed...")

    @classmethod
    def generate_poor_settlement_likelihood_estimation(cls, city_name):
        print("generating likelihood estimation of poor settlement, city - {0}".format(city_name))
        filename = city_name.replace(' ', '_').replace("'", "555") + '_Poor_Settlement.json'
        filepath = os.path.join(STATIC_ROOT, 'data', filename)
        generated_filepath = os.path.join(
            STATIC_ROOT, 'data', 'mapping_of_' + city_name.replace(' ', '_').replace("'", "555") + '_Poor_Settlement.csv')

        json_object = json.loads(open(filepath, 'r').read())
        data_rows = json_object['features']

        queryset = Geography.objects.filter(
            parent__parent__parent__name__iexact=city_name,
            level__name="Poor Settlement"
        )

        csv_file = open(generated_filepath, "w", encoding='utf-8')
        csv_file.write(
            "{0};{1};{2};{3};{4};{5};{6};{7};{8}\n".format(
                "Poor Settlement Name",
                "Poor Settlement-ID (DB)",
                "Poor Settlement Name (DB)",
                "Mahalla-ID (DB)",
                "Mahalla Name (DB)",
                "Ward-ID (DB)",
                "Ward Name (DB)",
                "Similarity (%)",
                "Coordinates"
            ))
        for row in data_rows:
            coordinates = ''
            if row['geometry']:
                coordinates = row['geometry']
            poor_settlement_name = row['properties']['settl_nam']
            ward = str(row['properties']['ward'])
            geography = queryset.filter(
                Q(parent__parent__name__iexact=ward) | Q(parent__parent__name__iexact=ward.zfill(2))
            ).annotate(similarity=TrigramSimilarity('name', poor_settlement_name),
                       ).filter(similarity__gt=0).order_by('-similarity').values(
                'id', 'name', 'parent_id', 'parent__name',
                'parent__parent_id', 'parent__parent__name', 'similarity'
            ).first()

            if poor_settlement_name:
                csv_file.write(
                    "{0};{1};{2};{3};{4};{5};{6};{7};{8}\n".format(
                        poor_settlement_name,
                        geography['id'] if geography else "",
                        geography['name'] if geography else "",
                        geography['parent_id'] if geography else "",
                        geography['parent__name'] if geography else "",
                        geography['parent__parent_id'] if geography else "",
                        geography['parent__parent__name'] if geography else "",
                        round(geography["similarity"], 2) * 100 if geography else "",
                        coordinates if geography else "",
                    ))

        csv_file.close()
        print("completed...")

    @classmethod
    def generate_csv_for_rangpur_poor_settlement(cls):
        print("generating csv for rangpur")
        geojson_dict = dict()

        # read json to create geojson dict
        json_file_path = os.path.join(STATIC_ROOT, 'data', 'Rangpur_Poor_Settlement.json')
        json_object = json.loads(open(json_file_path, 'r').read())
        json_data_rows = json_object['features']

        # read csv to create settlement id dict
        csv_filepath = os.path.join(STATIC_ROOT, 'data', 'Rangpur_Poor_Settlement.csv')
        csv_data_rows = cls.load_data_from_csv(csv_filepath)[1:]

        generated_filepath = os.path.join(STATIC_ROOT, 'data',
                                          'mapping_of_Rangpur_Poor_Settlement.csv')

        poor_settlement_queryset = Geography.objects.filter(
            parent__parent__parent__name__iexact="Rangpur",
            level__name="Poor Settlement"
        ).values('parent__parent__name', 'parent__name', 'name', 'id')
        settlement_dict = {(item['parent__parent__name'], item['parent__name'], item['name']): item['id']
                           for item in poor_settlement_queryset}

        csv_file = open(generated_filepath, "w", encoding='utf-8')
        csv_file.write(
            "{0};{1}\n".format(
                "Poor Settlement id",
                "Coordinates"
            ))

        for row in json_data_rows:
            if row['geometry']:
                coordinates = row['geometry']
                match_id = str(row['properties']['match_id'])
                geojson_dict[match_id] = coordinates

        for row in csv_data_rows:
            print(row)
            ward_name = str(row[0])
            mahalla_name = str(row[1])
            poor_settlement_name = str(row[2])
            match_id = str(row[3])

            settlement_id = settlement_dict.get((ward_name, mahalla_name, poor_settlement_name), None) or \
                            settlement_dict.get(((ward_name.zfill(2)), mahalla_name, poor_settlement_name), None)
            if settlement_id:
                csv_file.write(
                    "{0};{1}\n".format(
                        settlement_id,
                        geojson_dict.get(match_id, "")
                    ))
        csv_file.close()
        print("completed...")
