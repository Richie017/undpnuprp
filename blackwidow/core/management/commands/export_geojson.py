import json
import math
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import Count, Sum, F

from blackwidow.core.models import GeoJson, Geography
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.engine.extensions.color_code_generator import ColorCode
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from config.aws_s3_config import AWS_LOCATION
from config.model_json_cache import MENU_JSON_DIR_SUFFIX
from undp_nuprp.approvals.models import UrbanPoorSettlementIndicator, WordPrioritizationIndicator

MODEL_JASON_DIR = settings.MODEL_JASON_DIR
S3_STATIC_ENABLED = getattr(settings, 'S3_STATIC_ENABLED', False)

__author__ = "Ziaul Haque, Kaikobud"


class Command(BaseCommand):
    def handle(self, *args, **options):
        queryset = GeoJson.objects.filter(geography__isnull=False)

        cities = queryset.filter(
            geography__level__name='Pourashava/City Corporation'
        ).order_by('geography__level__name').values_list('geography_id', flat=True)
        legend_colors = ColorCode.get_color_code([
            "lush",
            "magenta",
            "maroon",
            "olive",
            "orange",
            "orchid",
            "sienna",
            "turquoise",
            "azure",
            "purple",
            "dark blue",
            "yellow",
            "brown",
            "light red",
            "light blue",
            "grey",
            "light ash",
            "dark white",
            "blue",
            "shed black"
        ])

        colors = {}
        for index, city_id in enumerate(cities):
            colors[city_id] = "#" + legend_colors[index]

        # for country geography data
        q0 = queryset.filter(geography__level__name='Country')
        self.generate_geojson_file(filename='country.json', colors=colors, queryset=q0)

        # for city corporation geography data
        q1 = queryset.filter(geography__level__name='Pourashava/City Corporation')
        self.generate_geojson_file(filename='city.json', colors=colors, queryset=q1)

        # for ward geography data
        q2 = queryset.filter(geography__level__name='Ward')
        self.generate_geojson_file(filename='ward.json', colors=colors, queryset=q2)

        # for mahalla geography data
        q4 = queryset.filter(geography__level__name='Mahalla')
        self.generate_geojson_file(filename='mahalla.json', colors=colors, queryset=q4)

        # for poor settlement geography data
        q5 = queryset.filter(geography__level__name='Poor Settlement')
        self.generate_geojson_file(filename='poor_settlement.json', colors=colors, queryset=q5)

        # generate bounding coord file for all geography (cities and wards)
        q3 = queryset. \
            filter(geography__level__name__in=['Pourashava/City Corporation', 'Ward', 'Mahalla', 'Poor Settlement'])
        self.generate_bounding_coords_file(filename='bounding_coords.json', queryset=q3)

    @classmethod
    def generate_geojson_file(cls, filename, colors, queryset):
        """
        This method is designed to generate geojson file for given GeoJson model queryset
        :param filename: file name of geojson
        :param colors: dictionary of predefined colors (key - city corporation id, value - rgb code of color)
        :param queryset: queryset of GeoJson model
        :return: None
        """
        print("processing data for {0}".format(filename))
        features = []
        poor_settlement_indicator_data = None
        ward_indicator_data = None
        city_wise_settlement_indicator_data = None
        city_wise_ward_prioritization_indicator_data = None
        level_name = queryset.first().geography.level.name
        if level_name == 'Poor Settlement':
            poor_settlement_indicator_data = cls.get_poor_settlement_indicator_data()
        elif level_name == 'Ward':
            ward_indicator_data = cls.get_ward_prioritization_indicator_data()
        elif level_name == 'Pourashava/City Corporation':
            city_wise_settlement_indicator_data = cls.get_city_wise_settlement_indicator_data()
            city_wise_ward_prioritization_indicator_data = cls.get_city_wise_ward_prioritization_indicator_data()
        for geojson_object in queryset:
            geography = geojson_object.geography
            if geography.level.name == 'Ward':
                level = 'ward'
            elif geography.level.name == 'Pourashava/City Corporation':
                level = 'city'
            else:
                level = geography.level.name
            if level == 'ward':
                color_code = colors[geography.parent_id]
            elif level == 'city':
                color_code = colors[geography.id]
            else:
                color_code = ""
            if geojson_object.multi_polygon_medium:
                multipolygon_geojson = geojson_object.multi_polygon_medium.geojson
            else:
                multipolygon_geojson = geojson_object.multi_polygon_actual.geojson
            feature = {
                "type": "Feature",
                "geometry": json.loads(multipolygon_geojson),
                "properties": {
                    "level_name": level,
                    "geography_id": geography.id,
                    "geography_name": geography.name,
                    "color_code": color_code,
                    "parent_name": geography.parent.name if geography.parent else ''
                }
            }
            if poor_settlement_indicator_data:
                feature['properties']. \
                    update(cls.prepare_poor_settlement_meta_info(geography.id, poor_settlement_indicator_data))
            elif ward_indicator_data:
                feature['properties']. \
                    update(cls.prepare_ward_prioritization_meta_info(geography.id, ward_indicator_data))
            elif city_wise_settlement_indicator_data and city_wise_ward_prioritization_indicator_data:
                feature['properties']. \
                    update(cls.prepare_city_wise_settlement_indicator_meta_info(geography.id,
                                                                                city_wise_settlement_indicator_data))
                feature['properties']. \
                    update(cls.prepare_city_wise_ward_prioritization_meta_info(geography.id,
                                                                               city_wise_ward_prioritization_indicator_data))

            features.append(feature)

        context = {
            "type": "FeatureCollection",
            "features": features,
        }
        try:
            # If using s3 as static file server, need to write the JS file in s3 bucket
            if S3_STATIC_ENABLED:
                file_dir = AWS_LOCATION + MENU_JSON_DIR_SUFFIX
                file_name = file_dir + filename
                file_content = json.dumps(context)
                AWSFileWriter.upload_file_with_content(file_name=file_name, content=file_content)
            else:
                _dir_suffix = MODEL_JASON_DIR
                os.makedirs(_dir_suffix, exist_ok=True)
                with open(_dir_suffix + filename, 'w') as f:
                    f.write(json.dumps(context))
        except Exception as exp:
            ErrorLog.log(exp=exp)
        print("completed..")

    @classmethod
    def generate_bounding_coords_file(cls, filename, queryset):
        """
        This method is designed to generate bounding coord file for given GeoJson model queryset
        :param filename: file name of bounding coord
        :param queryset: queryset of GeoJson model
        :return: None
        """

        bound_coords = {}
        for geojson_object in queryset:
            geography = geojson_object.geography
            if geojson_object.multi_polygon_medium:
                coords = list(geojson_object.multi_polygon_medium.extent)
            else:
                coords = list(geojson_object.multi_polygon_actual.extent)
            bound_coords[geography.id] = [
                coords[:len(coords) // 2], coords[len(coords) // 2:]
            ]
        try:
            # If using s3 as static file server, need to write the JS file in s3 bucket
            if S3_STATIC_ENABLED:
                file_dir = AWS_LOCATION + MENU_JSON_DIR_SUFFIX
                file_name = file_dir + filename
                file_content = json.dumps(bound_coords)
                AWSFileWriter.upload_file_with_content(file_name=file_name, content=file_content)
            else:
                _dir_suffix = MODEL_JASON_DIR
                os.makedirs(_dir_suffix, exist_ok=True)
                with open(_dir_suffix + filename, 'w') as f:
                    f.write(json.dumps(bound_coords))
        except Exception as exp:
            ErrorLog.log(exp=exp)

    @classmethod
    def get_poor_settlement_indicator_data(cls):
        """
        This method is designed to generate data dictionary using urban poor settlement indicators data
        (key - settlement id, value - (key - indicator name, value - indicator value, ...))
        :param :
        :return: dictionary of poor settlement indicator data
        """

        indicator_queryset = UrbanPoorSettlementIndicator.objects.values(
            "settlement_id", "household", "population", "settlement_age", "condition_of_access_road",
            "availability_of_drain", "electricity_coverage", "solid_waste_collection_service",
            "access_to_piped_water_supply", "availability_of_hygienic_toilet",
            "street_lighting", "attendance_of_children_at_school", "households_with_employment", "household_income",
            "social_problem", "land_tenure_security", "housing_condition", "risk_of_eviction",
            "land_ownership", "type_of_occupancy", "total_score", "settlement__name", "settlement__parent__name",
            "settlement__parent__parent__name", "settlement__parent__parent__parent__name"
        )
        poor_settlement_indicator_dict = {
            item['settlement_id']: {
                "settlement_name": item['settlement__name'],
                "mahalla_name": item['settlement__parent__name'],
                "ward_name": item['settlement__parent__parent__name'],
                "city_name": item['settlement__parent__parent__parent__name'],
                "household": item["household"],
                "population": item["population"],
                "settlement_age": item["settlement_age"],
                "condition_of_access_road": item["condition_of_access_road"],
                "availability_of_drain": item["availability_of_drain"],
                "electricity_coverage": item["electricity_coverage"],
                "solid_waste_collection_service": item["solid_waste_collection_service"],
                "access_to_piped_water_supply": item["access_to_piped_water_supply"],
                "availability_of_hygienic_toilet": item["availability_of_hygienic_toilet"],
                "street_lighting": item["street_lighting"],
                "attendance_of_children_at_school": item["attendance_of_children_at_school"],
                "households_with_employment": item["households_with_employment"],
                "household_income": item["household_income"],
                "social_problem": item["social_problem"],
                "land_tenure_security": item["land_tenure_security"],
                "housing_condition": item["housing_condition"],
                "risk_of_eviction": item["risk_of_eviction"],
                "land_ownership": item["land_ownership"],
                "type_of_occupancy": item["type_of_occupancy"],
                "total_score": item["total_score"]
            } for item in indicator_queryset
        }
        return poor_settlement_indicator_dict

    @classmethod
    def prepare_poor_settlement_meta_info(cls, geography, indicator_data):
        """
        This method is designed to generate indicator dictionary for specific geography
        :param geography: settlement id
        :param indicator_data: dictionary of urban poor settlement indicator queryset
        :return: indicator data for a single settlement as dictionary
        """

        poor_settlement_meta_info = {
            'Households': 0, 'Population': 0, 'Settlement Age': 0, 'Condition of access roads': 0,
            'Availability of drains': 0, 'Electricity coverage': 0, 'Solid waste collection service': 0,
            'Access to piped water supply': 0, 'Availability of hygienic toilet': 0,
            'Street lighting': 0, 'Attendance of children at school': 0, 'Households with employment': 0,
            'Household income': 0, 'Social problems': 0, 'Land tenure security': 0, 'Housing condition': 0,
            'Risk of eviction': 0, 'Land Ownership': 0, 'Type of Occupancy': 0, 'Total Score': 0,
            'Total Score(actual)': 0, 'Settlement': 'N/A', 'Mahalla': 'N/A', 'ward': 'N/A', 'city': 'N/A'
        }
        if geography in indicator_data.keys():
            indicator_info = indicator_data[geography]
            poor_settlement_meta_info = {
                "Settlement": indicator_info.get('settlement_name', ""),
                "Mahalla": indicator_info.get('mahalla_name', ""),
                "ward": indicator_info.get('ward_name', ""),
                "city": indicator_info.get('city_name', ""),
                'Households': indicator_info.get('household', 0),
                'Population': indicator_info.get('population', 0),
                'Settlement Age': indicator_info.get('settlement_age', 0),
                'Condition of access roads': indicator_info.get('condition_of_access_road', 0),
                'Availability of drains': indicator_info.get('availability_of_drain', 0),
                'Electricity coverage': indicator_info.get('electricity_coverage', 0),
                'Solid waste collection service': indicator_info.get('solid_waste_collection_service', 0),
                'Access to piped water supply': indicator_info.get('access_to_piped_water_supply', 0),
                'Availability of hygienic toilet': indicator_info.get('availability_of_hygienic_toilet', 0),
                'Street lighting': indicator_info.get('street_lighting', 0),
                'Attendance of children at school': indicator_info.get('attendance_of_children_at_school', 0),
                'Households with employment': indicator_info.get('households_with_employment', 0),
                'Household income': indicator_info.get('household_income', 0),
                'Social problems': indicator_info.get('social_problem', 0),
                'Land tenure security': indicator_info.get('land_tenure_security', 0),
                'Housing condition': indicator_info.get('housing_condition', 0),
                'Risk of eviction': indicator_info.get('risk_of_eviction', 0),
                'Land Ownership': indicator_info.get('land_ownership', 0),
                'Type of Occupancy': indicator_info.get('type_of_occupancy', 0),
                'Total Score(actual)': indicator_info.get('total_score', 0),
                'Total Score': math.ceil(indicator_info.get('total_score', 0) / 16)
            }
        else:
            settlement_instance = Geography.objects.filter(pk=geography, level__name="Poor Settlement").first()
            if settlement_instance:
                poor_settlement_meta_info['Settlement'] = settlement_instance.name
                poor_settlement_meta_info['Mahalla'] = settlement_instance.parent.name
                poor_settlement_meta_info['ward'] = settlement_instance.parent.parent.name
                poor_settlement_meta_info['city'] = settlement_instance.parent.parent.parent.name
        return poor_settlement_meta_info

    @classmethod
    def get_ward_prioritization_indicator_data(cls):
        """
        This method is designed to generate data dictionary using urban Ward Prioritization indicators data
        (key - settlement id, value - (key - indicator name, value - indicator value, ...))
        :param :
        :return: dictionary of Ward Prioritization indicator data
        """

        indicator_queryset = WordPrioritizationIndicator.objects.values(
            "Ward_id", "poverty_index_score", "poverty_index_quantile", "infrastructure_index_score",
            "infrastructure_index_quantile", "livelihood_index_score", "livelihood_index_quantile",
            "land_tenure_and_housing_index_score", "land_tenure_and_housing_index_quantile",
            "total_population"
        )
        ward_prioritization_indicator_dict = {
            item['Ward_id']: {
                "poverty_index_score": item['poverty_index_score'],
                "poverty_index_quantile": item['poverty_index_quantile'],
                "infrastructure_index_score": item['infrastructure_index_score'],
                "infrastructure_index_quantile": item['infrastructure_index_quantile'],
                "livelihood_index_score": item['livelihood_index_score'],
                "livelihood_index_quantile": item['livelihood_index_quantile'],
                "land_tenure_and_housing_index_score": item["land_tenure_and_housing_index_score"],
                "land_tenure_and_housing_index_quantile": item["land_tenure_and_housing_index_quantile"],
                "total_population": item["total_population"]
            } for item in indicator_queryset
        }
        return ward_prioritization_indicator_dict

    @classmethod
    def prepare_ward_prioritization_meta_info(cls, geography, indicator_data):
        """
        This method is designed to generate indicator dictionary for specific geography
        :param geography: ward id
        :param indicator_data: dictionary of ward prioritization indicator queryset
        :return: indicator data for a single ward as dictionary
        """

        ward_prioritization_meta_info = {
            'Poverty Index': 0,
            'Poverty Index Score': 0,
            'Infrastructure Index': 0,
            'Infrastructure Index Score': 0,
            'Livelihood Index': 0,
            'Livelihood Index Score': 0,
            'Land Tenure and Housing Index': 0,
            'Land Tenure and Housing Index Score': 0,
            'Total Population': 0,
            'Total Population(actual)': 0,
        }
        population_indicator_mapping = {
            1: 4,
            2: 3,
            3: 2,
            4: 1
        }
        if geography in indicator_data.keys():
            indicator_info = indicator_data[geography]
            population_indicator = math.ceil(indicator_info.get('total_population', 0) / 31250)
            ward_prioritization_meta_info = {
                "Poverty Index Score": math.ceil(indicator_info.get('poverty_index_score', 0)),
                "Poverty Index": math.ceil(indicator_info.get('poverty_index_quantile', 0)),
                "Infrastructure Index Score": math.ceil(indicator_info.get('infrastructure_index_score', 0)),
                "Infrastructure Index": math.ceil(indicator_info.get('infrastructure_index_quantile', 0)),
                "Livelihood Index Score": math.ceil(indicator_info.get('livelihood_index_score', 0)),
                "Livelihood Index": math.ceil(indicator_info.get('livelihood_index_quantile', 0)),
                'Land Tenure and Housing Index Score': math.ceil(indicator_info.get('land_tenure_and_housing_index_score', 0)),
                'Land Tenure and Housing Index': math.ceil(indicator_info.get('land_tenure_and_housing_index_quantile', 0)),
                'Total Population': population_indicator_mapping.get(population_indicator, 0),
                'Total Population(actual)': indicator_info.get('total_population', 0),
            }
        return ward_prioritization_meta_info

    @classmethod
    def get_city_wise_settlement_indicator_data(cls):
        """
        This method is designed to generate data dictionary using urban poor settlement indicators data
        (key - city id, value - (key - total population, value - sum of total population(per city),
                                 key - total poor settlement, value - poor settlement count(per city)))
        """

        indicator_queryset = UrbanPoorSettlementIndicator.objects.\
            values('settlement__parent__parent__parent_id').annotate(Count(F('id')),Sum(F('population')))
        city_wise_indicator_dict = {
            item['settlement__parent__parent__parent_id']: {
                "population__sum": item['population__sum'],
                "id__count": item['id__count'],
            } for item in indicator_queryset
        }
        return city_wise_indicator_dict

    @classmethod
    def prepare_city_wise_settlement_indicator_meta_info(cls, geography, indicator_data):
        """
        This method is designed to generate indicator dictionary for specific geography
        :param geography: city id
        :param indicator_data: dictionary of city wise urban poor settlement indicator queryset
        :return: indicator data for a single city as dictionary
        """

        city_wise_poor_settlement_meta_info = {
            'Total Population': 0,
            'Number of Poor Settlement': 0
        }
        if geography in indicator_data.keys():
            indicator_info = indicator_data[geography]
            city_wise_poor_settlement_meta_info = {
                "Total Population": indicator_info.get('population__sum', ""),
                "Number of Poor Settlement": indicator_info.get('id__count', "")
            }
        return city_wise_poor_settlement_meta_info

    @classmethod
    def get_city_wise_ward_prioritization_indicator_data(cls):
        """
        This method is designed to generate data dictionary using ward prioritization indicators data
        (key - city id, value - (key - total population, value - sum of total population(per city)))
        """

        indicator_queryset = WordPrioritizationIndicator.objects. \
            values('Ward__parent_id').annotate(Sum(F('total_population')))
        city_wise_indicator_dict = {
            item['Ward__parent_id']: {
                "total_population__sum": item['total_population__sum']
            } for item in indicator_queryset
        }
        return city_wise_indicator_dict

    @classmethod
    def prepare_city_wise_ward_prioritization_meta_info(cls, geography, indicator_data):
        """
        This method is designed to generate indicator dictionary for specific geography
        :param geography: city id
        :param indicator_data: dictionary of city wise ward prioritization indicator queryset
        :return: indicator data for a single city as dictionary
        """

        city_wise_ward_prioritization_meta_info = {
            'Total Population(ward prioritization)': 0,
        }
        if geography in indicator_data.keys():
            indicator_info = indicator_data[geography]
            city_wise_ward_prioritization_meta_info = {
                'Total Population(ward prioritization)': indicator_info.get('total_population__sum', ""),
            }
        return city_wise_ward_prioritization_meta_info

