from collections import OrderedDict

from django.db.models.aggregates import Count, Avg

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models.benificieries.grantee import Grantee
from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator

__author__ = "Shama"


def get_grantees_indicator_table_data(towns=list):
    queryset = Grantee.objects.filter(is_deleted=False).using(BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(town_id__in=towns)
    queryset = queryset.values('town__name', 'type_of_grant').order_by('town__name'). \
        annotate(count=Count('type_of_grant'))

    city_dict = OrderedDict()
    for data in queryset:
        g_type = data.get('type_of_grant')
        if g_type not in city_dict.keys():
            city_dict[g_type] = 0
        city_dict[g_type] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        g_type = data.get('type_of_grant')
        city = data.get('town__name')
        count = data.get('count')

        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        table_data[city][g_type] = "{0}".format(count)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def get_grantees_gender_indicator_table_data(towns=list):
    queryset = Grantee.objects.filter(is_deleted=False).using(BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(town_id__in=towns)
    queryset = queryset.values('town__name', 'type_of_grant', 'gender').order_by(
        'town__name', 'type_of_grant', 'gender').annotate(count=Count('pk', distinct=True))

    city_dict = OrderedDict()
    grant_types = list()
    gender_types = list()
    for data in queryset:
        city = data.get('town__name')
        if city not in city_dict.keys():
            city_dict[city] = OrderedDict()
        g_type = data.get('type_of_grant')
        if g_type not in city_dict[city].keys():
            city_dict[city][g_type] = OrderedDict()
        gender = data.get('gender')
        if gender not in city_dict[city][g_type].keys():
            city_dict[city][g_type][gender] = 0
        city_dict[city][g_type][gender] += data.get('count')

        if g_type not in grant_types:
            grant_types.append(g_type)
        if gender not in gender_types:
            gender_types.append(gender)

    response_data = list()
    headers = ['City Corporation']
    for g_type in grant_types:
        for gender in gender_types:
            headers += ['{} ({})'.format(g_type, gender)]
    response_data.append(headers)
    for city, city_data in city_dict.items():
        li = [str(city)]
        for g_type in grant_types:
            for gender in gender_types:
                li.append(city_data[g_type][gender] if g_type in city_data.keys() and gender in city_data[
                    g_type].keys() else 0)
        response_data.append(li)
    return response_data


def get_ap_grantees_business_area_indicator_table_data(towns=list):
    queryset = Grantee.objects.filter(is_deleted=False, type_of_grant='Apprenticeship grant').using(
        BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(town_id__in=towns)
    queryset = queryset.values('town__name', 'area_of_business').order_by('town__name'). \
        annotate(count=Count('area_of_business'))

    city_dict = OrderedDict()
    for data in queryset:
        g_type = data.get('area_of_business')
        if g_type not in city_dict.keys():
            city_dict[g_type] = 0
        city_dict[g_type] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        g_type = data.get('area_of_business')
        city = data.get('town__name')
        count = data.get('count')

        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        table_data[city][g_type] = "{0}".format(count)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def get_bg_grantees_business_area_indicator_table_data(towns=list):
    queryset = Grantee.objects.filter(is_deleted=False, type_of_grant='Business grant').using(
        BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(town_id__in=towns)
    queryset = queryset.values('town__name', 'area_of_business').order_by('town__name'). \
        annotate(count=Count('area_of_business'))

    city_dict = OrderedDict()
    for data in queryset:
        g_type = data.get('area_of_business')
        if g_type not in city_dict.keys():
            city_dict[g_type] = 0
        city_dict[g_type] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        g_type = data.get('area_of_business')
        city = data.get('town__name')
        count = data.get('count')

        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        table_data[city][g_type] = "{0}".format(count)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def get_grantees_percent_with_disability_indicator_table_data(towns=list):
    queryset = Grantee.objects.filter(is_deleted=False).using(BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(town_id__in=towns)
    queryset = queryset.values('town__name', 'referred_pg_member__client_meta__is_disabled').order_by('town__name'). \
        annotate(count=Count('referred_pg_member__pk', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        g_type = data.get('town__name')
        if g_type not in city_dict.keys():
            city_dict[g_type] = 0
        city_dict[g_type] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        g_type = data.get('referred_pg_member__client_meta__is_disabled')
        city = data.get('town__name')
        count = data.get('count')

        if city not in table_data.keys():
            table_data[city] = 0

        if g_type:
            table_data[city] += (100.0 * count / float(city_dict[city]))

    response_data = list()
    response_data.append((['City Corporation', '% of Disabled']))
    for key, value in table_data.items():
        li = [str(key), '%.2f%%' % (value,)]
        response_data.append(li)
    return response_data


def get_grantees_education_indicator_table_data(towns=list):
    queryset = Grantee.objects.filter(is_deleted=False, type_of_grant='Education grant').using(
        BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(town_id__in=towns)
    queryset = queryset.values('town__name', 'highest_level_of_education').order_by('town__name'). \
        annotate(count=Count('highest_level_of_education'), total=Count('pk', distinct=True))
    total_queryset = queryset.values('town__name', 'highest_level_of_education').order_by('town__name'). \
        annotate(total=Count('pk', distinct=True))

    total_dict = OrderedDict()
    for data in total_queryset:
        city = data.get('town__name')
        if city not in total_dict.keys():
            total_dict[city] = 0
        total_dict[city] += data.get('total')

    city_dict = OrderedDict()
    for data in queryset:
        g_type = data.get('highest_level_of_education')
        if g_type not in city_dict.keys():
            city_dict[g_type] = 0
        city_dict[g_type] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        g_type = data.get('highest_level_of_education')
        city = data.get('town__name')
        count = data.get('count')

        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        table_data[city][g_type] = "{0:.2f}%".format((count / total_dict[city]) * 100)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def get_grantees_mpi_indicator_table_data(towns=list):
    queryset = PGMPIIndicator.objects.filter(survey_response__survey__name='PG Member Survey Questionnaire').using(
        BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(primary_group_member__assigned_to__parent__address__geography__parent_id__in=towns)
    queryset = queryset.values('primary_group_member__assigned_to__parent__address__geography__parent__name',
                               'primary_group_member__grantee__type_of_grant').order_by(
        'primary_group_member__assigned_to__parent__address__geography__parent__name'). \
        annotate(average=Avg('mpi_score'))

    city_dict = OrderedDict()
    for data in queryset:
        g_type = data.get('primary_group_member__grantee__type_of_grant')
        if g_type:
            if g_type not in city_dict.keys():
                city_dict[g_type] = 0
            city_dict[g_type] += data.get('average')

    table_data = OrderedDict()
    for data in queryset:
        g_type = data.get('primary_group_member__grantee__type_of_grant')
        city = data.get('primary_group_member__assigned_to__parent__address__geography__parent__name')
        avg = data.get('average')

        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        if g_type:
            table_data[city][g_type] = "{0:.2f}".format(avg)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def get_age_indicator_table_data(towns=list):
    queryset = Grantee.objects.filter(is_deleted=False).using(BWDatabaseRouter.get_read_database_name())
    if towns:
        queryset = queryset.filter(town_id__in=towns)
    queryset = queryset.values('town__name', 'age').order_by('town__name'). \
        annotate(count=Count('pk', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        age = data.get('age')
        g_age = ''
        if 11 <= age <= 15:
            g_age = 'Between 11 and 15'
        elif 16 <= age <= 20:
            g_age = 'Between 16 and 20'
        elif 21 <= age <= 25:
            g_age = 'Between 21 and 25'
        elif 26 <= age <= 30:
            g_age = 'Between 26 and 30'
        elif 31 <= age <= 35:
            g_age = 'Between 31 and 35'
        elif 36 <= age <= 40:
            g_age = 'Between 36 and 40'
        elif 41 <= age <= 45:
            g_age = 'Between 41 and 45'
        elif 46 <= age <= 50:
            g_age = 'Between 46 and 50'
        elif 51 <= age <= 55:
            g_age = 'Between 51 and 55'
        elif 55 <= age <= 60:
            g_age = 'Between 55 and 60'
        if g_age not in city_dict.keys() and g_age:
            city_dict[g_age] = 0
        if g_age:
            city_dict[g_age] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        age = data.get('age')
        g_age = ''
        if 11 <= age <= 15:
            g_age = 'Between 11 and 15'
        elif 16 <= age <= 20:
            g_age = 'Between 16 and 20'
        elif 21 <= age <= 25:
            g_age = 'Between 21 and 25'
        elif 26 <= age <= 30:
            g_age = 'Between 26 and 30'
        elif 31 <= age <= 35:
            g_age = 'Between 31 and 35'
        elif 36 <= age <= 40:
            g_age = 'Between 36 and 40'
        elif 41 <= age <= 45:
            g_age = 'Between 41 and 45'
        elif 46 <= age <= 50:
            g_age = 'Between 46 and 50'
        elif 51 <= age <= 55:
            g_age = 'Between 51 and 55'
        elif 55 <= age <= 60:
            g_age = 'Between 55 and 60'

        city = data.get('town__name')
        count = data.get('count')

        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        if g_age:
            table_data[city][g_age] = "{0}".format(count)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data
