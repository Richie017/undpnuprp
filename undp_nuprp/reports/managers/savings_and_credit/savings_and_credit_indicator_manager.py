from collections import OrderedDict

from django.db.models.aggregates import Count, Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup

__author__ = "Shama"


def get_scgnumber_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport
    question_responses = SavingsAndCreditReport.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        question_responses = question_responses.filter(scg__address__geography_id__in=wards)
    queryset = question_responses.values('scg', 'scg__address__geography__parent__name').order_by(
        'scg', 'scg__address__geography__parent__name').annotate(count=Count('pk', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('scg__address__geography__parent__name')
        if city not in city_dict.keys():
            city_dict[city] = 0
        city_dict[city] += data.get('count')

    response_data = list()
    response_data.append(([k for k in city_dict.keys()]))
    response_data.append(([v for v in city_dict.values()]))
    return response_data


def get_scgsavings_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport
    question_responses = SavingsAndCreditReport.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        question_responses = question_responses.filter(scg__address__geography_id__in=wards)
    queryset = question_responses.values('deposited_savings', 'scg__address__geography__parent__name').order_by(
        'deposited_savings', 'scg__address__geography__parent__name').annotate(
        count=Sum('deposited_savings', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('scg__address__geography__parent__name')
        if city not in city_dict.keys():
            city_dict[city] = 0
        city_dict[city] += data.get('count')

    response_data = list()
    response_data.append(([k for k in city_dict.keys()]))
    response_data.append(([v for v in city_dict.values()]))
    return response_data


def get_scgloans_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport
    question_responses = SavingsAndCreditReport.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        question_responses = question_responses.filter(scg__address__geography_id__in=wards)
    queryset = question_responses.values('loan_disbursed', 'scg__address__geography__parent__name').order_by(
        'loan_disbursed', 'scg__address__geography__parent__name').annotate(count=Sum('loan_disbursed', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('scg__address__geography__parent__name')
        if city not in city_dict.keys():
            city_dict[city] = 0
        city_dict[city] += data.get('count')

    response_data = list()
    response_data.append(([k for k in city_dict.keys()]))
    response_data.append(([v for v in city_dict.values()]))
    return response_data


def get_scgoutstandingloans_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport
    question_responses = SavingsAndCreditReport.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        question_responses = question_responses.filter(scg__address__geography_id__in=wards)
    queryset = question_responses.values('outstanding_loans', 'scg__address__geography__parent__name').order_by(
        'outstanding_loans', 'scg__address__geography__parent__name').annotate(
        count=Sum('outstanding_loans', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('scg__address__geography__parent__name')
        if city not in city_dict.keys():
            city_dict[city] = 0
        city_dict[city] += data.get('count')

    response_data = list()
    response_data.append(([k for k in city_dict.keys()]))
    response_data.append(([v for v in city_dict.values()]))
    return response_data


def get_scgmembers_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
    question_responses = SavingsAndCreditGroup.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        question_responses = question_responses.filter(scg__address__geography_id__in=wards)
    queryset = question_responses.values('address__geography__parent__name').order_by(
        'address__geography__parent__name').annotate(count=Count('members__pk', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('address__geography__parent__name')
        if city not in city_dict.keys():
            city_dict[city] = 0
        city_dict[city] += data.get('count')

    response_data = list()
    response_data.append(([k for k in city_dict.keys()]))
    response_data.append(([v for v in city_dict.values()]))
    return response_data


def get_scggender_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup

    question_responses = SavingsAndCreditGroup.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        question_responses = question_responses.filter(address__geography_id__in=wards)
    queryset = question_responses.values('address__geography__parent__name', 'members__client_meta__gender').order_by(
        'address__geography__parent__name').annotate(count=Count('members__pk', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        answer = data.get('members__client_meta__gender')
        if answer == 'M':
            answer = 'Male'
        elif answer == 'F':
            answer = 'Female'
        elif answer == 'H':
            answer = 'Hijra'
        else:
            continue
        if answer not in city_dict.keys():
            city_dict[answer] = 0
        city_dict[answer] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('address__geography__parent__name')
        answer = data.get('members__client_meta__gender')
        count = data.get('count')
        if answer == 'M':
            answer = 'Male'
        elif answer == 'F':
            answer = 'Female'
        elif answer == 'H':
            answer = 'Hijra'
        else:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        table_data[city][answer] = "{0}".format(count)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def get_scgdisability_status_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup

    question_responses = SavingsAndCreditGroup.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        question_responses = question_responses.filter(address__geography_id__in=wards)
    queryset = question_responses.values('address__geography__parent__name',
                                         'members__client_meta__is_disabled').order_by(
        'address__geography__parent__name').annotate(count=Count('members__pk', distinct=True))

    city_dict = OrderedDict()
    for data in queryset:
        answer = data.get('members__client_meta__is_disabled')
        if answer == False:
            answer = 'Is disabled'
        else:
            continue
        if answer not in city_dict.keys():
            city_dict[answer] = 0
        city_dict[answer] += data.get('count')

    table_data = OrderedDict()
    for data in queryset:
        city = data.get('address__geography__parent__name')
        answer = data.get('members__client_meta__is_disabled')
        count = data.get('count')
        if answer == False:
            answer = 'Is disabled'
        else:
            continue
        if city not in table_data.keys():
            table_data[city] = OrderedDict()
            for c in city_dict.keys():
                table_data[city][c] = 0

        table_data[city][answer] = "{0}".format(count)

    response_data = list()
    response_data.append((['City Corporation', ] + [g for g in city_dict.keys()]))
    for key, value in table_data.items():
        li = [str(key)]
        for k, v in value.items():
            li.append(v)
        response_data.append(li)
    return response_data


def get_pgmember_percentage_indicator_table_data(wards=list(), from_time=None, to_time=None):
    from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup

    savings_and_credit_queryset = SavingsAndCreditGroup.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    if wards:
        savings_and_credit_queryset = savings_and_credit_queryset.filter(address__geography_id__in=wards)
    queryset = savings_and_credit_queryset.values('address__geography__parent__name').order_by(
        'address__geography__parent__name').annotate(count=Count('members__pk', distinct=True))

    total_queryset = PrimaryGroupMember.objects.filter(is_deleted=False,
                                                       assigned_to__parent__address__geography_id__in=wards).using(
        BWDatabaseRouter.get_read_database_name())
    total_queryset = total_queryset.values('assigned_to__parent__address__geography__parent__name').order_by(
        'assigned_to__parent__address__geography__parent__name'
    ).annotate(total=Count('pk', distinct=True))

    total_dict = OrderedDict()
    for data in total_queryset:
        city = data.get('assigned_to__parent__address__geography__parent__name')
        if city not in total_dict.keys():
            total_dict[city] = 0
        total_dict[city] += data.get('total')

    city_dict = OrderedDict()
    for data in queryset:
        city = data.get('address__geography__parent__name')
        if city not in city_dict.keys():
            city_dict[city] = 0
        if city in total_dict.keys() and total_dict[city] > 0:
            city_dict[city] += (data.get('count') / float(total_dict[city]))
        else:
            city_dict[city] = 'N/A'

    response_data = list()
    response_data.append(([k for k in city_dict.keys()]))
    response_data.append(([(v if v == 'N/A' else '%.2f%%' % v * 100.0) for v in city_dict.values()]))
    return response_data


def get_report_indicator_table_data(wards=list(), from_time=None, to_time=None):
    def get_empty_data_row():
        empty_row = {
            'number_of_scg': 0,
            'saving': 0,
            'loans': 0,
            'involved_count': 0,
            'total_member': 0,
            'male': 0,
            'female': 0,
            'disabled': 0,
        }
        return empty_row

    question_responses = SavingsAndCreditGroup.objects.filter(is_deleted=False).using(
        BWDatabaseRouter.get_read_database_name())
    member_queryset = SavingsAndCreditGroup.objects.values(
        'address__geography__parent__name', 'members__client_meta__gender',
        'members__client_meta__is_disabled').annotate(count=Count('members__pk', distinct=True)).using(
        BWDatabaseRouter.get_read_database_name())

    pgmember_queryset = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).values(
        'assigned_to__parent__address__geography__parent__name').annotate(count=Count('pk', distinct=True))
    if wards:
        question_responses = question_responses.filter(scg__address__geography_id__in=wards)
    queryset = question_responses.values('address__geography__parent__name').order_by(
        'address__geography__parent__name').annotate(
        scg_count=Count('pk', distinct=True), saving=Sum('savingsandcreditreport__deposited_savings'),
        loans=Sum('savingsandcreditreport__loan_disbursed'))

    city_dict = OrderedDict()
    total_row = get_empty_data_row()
    for q in queryset:
        city = q['address__geography__parent__name']
        if city not in city_dict.keys():
            city_dict[city] = get_empty_data_row()
        city_dict[city]['number_of_scg'] += q['scg_count']
        total_row['number_of_scg'] += q['scg_count']

        city_dict[city]['saving'] += (q['saving'] if q['saving'] else 0)
        total_row['saving'] += (q['saving'] if q['saving'] else 0)

        city_dict[city]['loans'] += (q['loans'] if q['loans'] else 0)
        total_row['loans'] += (q['loans'] if q['loans'] else 0)

    for q in pgmember_queryset:
        city = q['assigned_to__parent__address__geography__parent__name']
        if city not in city_dict.keys():
            city_dict[city] = get_empty_data_row()
        city_dict[city]['total_member'] += q['count']
        total_row['total_member'] += q['count']

    for q in member_queryset:
        city = q['address__geography__parent__name']
        if city not in city_dict.keys():
            city_dict[city] = get_empty_data_row()

        city_dict[city]['involved_count'] += q['count']
        total_row['involved_count'] += q['count']
        gender = q['members__client_meta__gender']
        if gender == 'M':
            city_dict[city]['male'] += q['count']
            total_row['male'] += q['count']
        elif gender == 'F':
            city_dict[city]['female'] += q['count']
            total_row['female'] += q['count']
        if q['members__client_meta__is_disabled']:
            city_dict[city]['disabled'] += q['count']
            total_row['disabled'] += q['count']

    response_data = list()
    headers = ['City Corporation', 'Number of SCG groups formed', 'Cumulative value of savings generated',
               'Cumulative value of loans disbursed', '% of PG members involved in Savings & credit project',
               'Total number of SCG members', 'No of male members', 'No of female members',
               'No of members with a disability']
    response_data.append(headers)
    for city, value in city_dict.items():
        li = [str(city), value['number_of_scg'], value['saving'], value['loans'],
              '%.2f%%' % (value['involved_count'] * 100.0 / value['total_member'],), value['involved_count'],
              value['male'], value['female'], value['disabled']]
        response_data.append(li)
    return response_data
