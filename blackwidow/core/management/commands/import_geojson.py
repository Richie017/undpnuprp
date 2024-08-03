import csv
import json
import os

from django.conf import settings
from django.contrib.gis.geos import Polygon, MultiPolygon
from django.core.management import BaseCommand

from blackwidow.core.models import Geography, Organization, GeoJson

__author__ = "Ziaul Haque"

STATIC_ROOT = settings.STATIC_ROOT
cities_with_no_verification = [
    # "Cumilla", "DNCC", "Faridpur", "Gazipur", "Gopalganj", "Kushtia", "Noakhali", "Patuakhali", "Rangpur",
    # "Saidpur", "Chittagong city corporation",

    "Narayanganj",
    "Cox's Bazar",
    "Dhaka South",
    "Rajshahi",
    "Sylhet City Corporation"
]


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
            # ('Barisal', 'Barisal'),
            # ('Chandpur', 'Chandpur'),
            # ('Chittagong', 'Chittagong city corporation'),
            # ('DNCC', 'DNCC'),
            # ('Faridpur', 'Faridpur'),
            # ('Gopalganj', 'Gopalganj'),
            # ('Khulna', 'Khulna'),
            # ('Kushtia', 'Kushtia'),
            # ('Mymensingh', 'Mymensingh'),
            # ('Noakhali', 'Noakhali'),
            # ('Patuakhali', 'Patuakhali'),
            # ('Saidpur', 'Saidpur'),
            # ('Gazipur', 'Gazipur'),
            # ('Cumilla', 'Cumilla'),
            # ('Rangpur', 'Rangpur'),

            ("Narayanganj", "Narayanganj"),
            ("Coxs_Bazar", "Cox's Bazar"),
            ("Dhaka_South", "Dhaka South"),
            ("Rajshahi", "Rajshahi"),
            ("Sylhet", "Sylhet City Corporation"),
        ]
        cities_for_mahalla = [
            # "DNCC", "Faridpur", "Gazipur", "Gopalganj", "Khulna", "Kushtia", "Mymensingh",
            # "Noakhali", "Patuakhali", "Rangpur", "Saidpur", "Barisal", "Cumilla", "Chandpur",
            # "Chittagong city corporation",

            "Narayanganj",
            "Cox's Bazar",
            "Dhaka South",
            "Rajshahi",
            "Sylhet City Corporation"
        ]

        organization = Organization.objects.first()

        country_file = 'Bangladesh_Country.json'
        # self.import_country_boundary_data(filename=country_file, country_name='Bangladesh', organization=organization)

        for file_prefix, city_name in cities:
            city_file = file_prefix + '_City.json'
            ward_file = file_prefix + '_Ward.json'
            self.import_city_boundary_data(filename=city_file, city_name=city_name, organization=organization)
            self.import_ward_boundary_data(filename=ward_file, city_name=city_name, organization=organization)
            if city_name != "Rangpur":
                self.import_poor_settlement_boundary_data(
                    city_name=city_name.replace(' ', '_').replace("'", "555"),
                    organization=organization
                )
        # self.import_rangpur_poor_settlement_boundary_data(city_name="Rangpur", organization=organization)

        for city in cities_for_mahalla:
            self.import_mahalla_boundary_data(
                city_name=city.replace(' ', '_').replace("'", "555"),
                organization=organization
            )

    @classmethod
    def import_country_boundary_data(cls, filename, country_name, organization):
        file_path = os.path.join(STATIC_ROOT, 'data', filename)
        json_object = json.loads(open(file_path, 'r').read())
        polygons = []
        for coordinates in json_object['features'][0]['geometry']['coordinates']:
            polygon = Polygon(coordinates[0])
            polygons.append(polygon)
        mp = MultiPolygon(polygons)
        geography = Geography.objects.filter(
            level__name='Country',
            name=country_name
        ).first()
        geojson = GeoJson.objects.filter(organization=organization, geography=geography).first()
        if not geojson:
            geojson = GeoJson(organization=organization)
            geojson.geography = geography
        geojson.multi_polygon_actual = mp
        geojson.save()
        print("imported country boundary for {0} Country, geojson_id: {1}".format(country_name, geojson.pk))

    @classmethod
    def import_city_boundary_data(cls, filename, city_name, organization):
        file_path = os.path.join(STATIC_ROOT, 'data', filename)
        json_object = json.loads(open(file_path, 'r').read())
        polygons = []
        for coordinates in json_object['features'][0]['geometry']['coordinates']:
            polygon = Polygon(coordinates[0])
            polygons.append(polygon)
        mp = MultiPolygon(polygons)
        geography = Geography.objects.filter(
            level__name='Pourashava/City Corporation',
            name=city_name
        ).first()
        geojson = GeoJson.objects.filter(organization=organization, geography=geography).first()
        if not geojson:
            geojson = GeoJson(organization=organization)
            geojson.geography = geography
        geojson.multi_polygon_actual = mp
        geojson.save()
        print("imported city boundary for {0} City, geojson_id: {1}".format(city_name, geojson.pk))

    @classmethod
    def import_ward_boundary_data(cls, filename, city_name, organization):
        file_path = os.path.join(STATIC_ROOT, 'data', filename)
        json_object = json.loads(open(file_path, 'r').read())
        city_object = Geography.objects.filter(
            level__name='Pourashava/City Corporation',
            name=city_name
        ).first()

        for feature in json_object['features']:
            ward_name = str(feature['properties']['Ward_NO'])
            if len(ward_name) == 1:
                geography = Geography.objects.filter(parent=city_object, name=ward_name).first()
                if not geography:
                    geography = Geography.objects.filter(parent=city_object, name="0{}".format(ward_name)).first()
            else:
                geography = Geography.objects.filter(parent=city_object, name=ward_name).first()
            polygons = []
            if feature['geometry']['type'] == 'Polygon':
                for coordinates in feature['geometry']['coordinates']:
                    polygon = Polygon(coordinates)
                    polygons.append(polygon)
            else:
                for coordinates in feature['geometry']['coordinates']:
                    polygon = Polygon(coordinates[0])
                    polygons.append(polygon)
            mp = MultiPolygon(polygons)
            if not geography:
                print(ward_name + ' not found')
                continue
            geojson = GeoJson.objects.filter(organization=organization, geography=geography).first()
            if not geojson:
                geojson = GeoJson(organization=organization)
                geojson.geography = geography
            geojson.multi_polygon_actual = mp
            geojson.save()
            print("imported ward boundary for {0} City, ward name: {1}, geojson_id: {2}".format(
                city_name, ward_name, geojson.pk
            ))

    @classmethod
    def import_mahalla_boundary_data(cls, city_name, organization):
        filename = 'mapping_of_' + str(city_name) + '_Mahalla.csv'
        filepath = os.path.join(STATIC_ROOT, 'data', filename)
        data_rows = cls.load_data_from_csv(filepath)[1:]
        for row in data_rows:
            # no need to add and check verify status column for those cities data which has no mahalla
            if str(city_name.replace('_', ' ').replace("555", "'")) in cities_with_no_verification:
                verify_status = 1
                _coordinates = row[6]
                print("No verification is needed for " + str(city_name))
            else:
                verify_status = row[6]
                _coordinates = row[7]
            if int(verify_status) and _coordinates != "":
                mahalla_id = row[1]
                geography_coords = json.loads(_coordinates.replace("'", '"'))
                geography = Geography.objects.filter(id=mahalla_id).first()
                polygons = []
                if geography:
                    if geography_coords['type'] == 'Polygon':
                        for coordinates in geography_coords['coordinates']:
                            polygon = Polygon(coordinates)
                            polygons.append(polygon)
                    else:
                        for coordinates in geography_coords['coordinates']:
                            polygon = Polygon(coordinates[0])
                            polygons.append(polygon)
                    mp = MultiPolygon(polygons)
                    geojson = GeoJson.objects.filter(organization=organization, geography=geography).first()
                    if not geojson:
                        geojson = GeoJson(organization=organization)
                        geojson.geography = geography
                    geojson.multi_polygon_actual = mp
                    geojson.save()
                    print("imported Mahalla boundary for {0} City, Mahalla name: {1}, geojson_id: {2}".format(
                        city_name, row[2], geojson.pk
                    ))

    @classmethod
    def import_poor_settlement_boundary_data(cls, city_name, organization):
        filename = 'mapping_of_' + str(city_name) + '_Poor_Settlement.csv'
        filepath = os.path.join(STATIC_ROOT, 'data', filename)
        data_rows = cls.load_data_from_csv(filepath)[1:]
        for row in data_rows:
            # no need to add and check verify status column for those cities data which has no poor settlement
            if str(city_name.replace('_', ' ').replace("555", "'")) in cities_with_no_verification:
                verify_status = 1
                _coordinates = row[8]
                print("No verification is needed for " + str(city_name))
            else:
                verify_status = row[8]
                _coordinates = row[9]
            if verify_status and _coordinates != "":
                poor_settlement_id = row[1]
                geography_coords = json.loads(_coordinates.replace("'", '"'))
                geography = Geography.objects.filter(id=poor_settlement_id).first()
                polygons = []
                if geography:
                    if geography_coords['type'] == 'Polygon':
                        for coordinates in geography_coords['coordinates']:
                            polygon = Polygon(coordinates)
                            polygons.append(polygon)
                    else:
                        for coordinates in geography_coords['coordinates']:
                            polygon = Polygon(coordinates[0])
                            polygons.append(polygon)
                    mp = MultiPolygon(polygons)
                    geojson = GeoJson.objects.filter(organization=organization, geography=geography).first()
                    if not geojson:
                        geojson = GeoJson(organization=organization)
                        geojson.geography = geography
                    geojson.multi_polygon_actual = mp
                    geojson.save()
                    print(
                        "imported Poor Settlement boundary for {0} City, Poor Settlement name: {1}, geojson_id: {2}".format(
                            city_name, row[2], geojson.pk
                        ))

    @classmethod
    def import_rangpur_poor_settlement_boundary_data(cls, city_name, organization):
        filename = 'mapping_of_Rangpur_Poor_Settlement.csv'
        filepath = os.path.join(STATIC_ROOT, 'data', filename)
        data_rows = cls.load_data_from_csv(filepath)[1:]
        for row in data_rows:
            if row[0] and row[1]:
                poor_settlement_id = row[0]
                geography_coords = json.loads(row[1].replace("'", '"'))
                geography = Geography.objects.filter(id=poor_settlement_id).first()
                polygons = []
                if geography:
                    if geography_coords['type'] == 'Polygon':
                        for coordinates in geography_coords['coordinates']:
                            polygon = Polygon(coordinates)
                            polygons.append(polygon)
                    else:
                        for coordinates in geography_coords['coordinates']:
                            polygon = Polygon(coordinates[0])
                            polygons.append(polygon)
                    mp = MultiPolygon(polygons)
                    geojson = GeoJson.objects.filter(organization=organization, geography=geography).first()
                    if not geojson:
                        geojson = GeoJson(organization=organization)
                        geojson.geography = geography
                    geojson.multi_polygon_actual = mp
                    geojson.save()
                    print(
                        "imported Poor Settlement boundary for {0} City, Poor Settlement id: {1}, geojson_id: {2}".format(
                            city_name, row[0], geojson.pk
                        ))
