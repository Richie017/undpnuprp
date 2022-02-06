from django.db.models import Sum, Case, When, IntegerField, Q

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import UrbanGovernanceAndPlanning


def get_ugp_ward_committee_indicator_table_data(from_time=None, to_time=None):
    ugp_queryset = UrbanGovernanceAndPlanning.objects.exclude(
        ward_committee_ward_no=""
    ).using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        ugp_queryset = ugp_queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = ugp_queryset.order_by('city__name').values('city__name').annotate(
        total_wards=Sum(Case(When(Q(ward_committee_ward_no__isnull=True) | Q(ward_committee_ward_no=""), then=0),
                             default=1),
                        output_field=IntegerField()),
        established_wards=Sum(Case(When(ward_committee_established='Yes', then=1),
                                   default=0),
                              output_field=IntegerField()),
        functional_wards=Sum(Case(When(ward_committee_functional='Yes', then=1),
                                  default=0),
                             output_field=IntegerField())
    )

    header = ['City']
    header += ['Total Ward Committee']
    header += [
        {
            'column_name': 'No of Established Ward Committee',
            'extra_column_name': 'No of Established Ward Committee(%)',
            'split': 'true'
        }
    ]
    header += [
        {
            'column_name': 'No of Functional Ward Committee',
            'extra_column_name': 'No of Functional Ward Committee(%)',
            'split': 'true'
        }
    ]

    response_data = [header, ]

    for data in queryset:
        total = data.get('total_wards')
        established = data.get('established_wards')
        functional = data.get('functional_wards')
        response_data.append([
            data.get('city__name'), str(total),
            '{0:.0f}%'.format(established * 100 / total if total else 0.0) + ' (' + str(established) + ')',
            '{0:.0f}%'.format(functional * 100 / total if total else 0.0) + ' (' + str(functional) + ')'
        ])

    return response_data


def get_ugp_institutional_financial_capability_indicator_table_data(from_time=None, to_time=None):
    ugp_queryset = UrbanGovernanceAndPlanning.objects.exclude(
        ward_committee_ward_no=""
    ).using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        ugp_queryset = ugp_queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = ugp_queryset.order_by('city__name').values('city__name').annotate(
        total_wards=Sum(Case(When(Q(ward_committee_ward_no__isnull=True) | Q(ward_committee_ward_no=""), then=0),
                             default=1),
                        output_field=IntegerField()),
        drafted=Sum(Case(When(drafted='Yes', then=1),
                         default=0),
                    output_field=IntegerField()),
        finalized=Sum(Case(When(finalized='Yes', then=1),
                           default=0),
                      output_field=IntegerField()),
        approved=Sum(Case(When(approved='Yes', then=1),
                          default=0),
                     output_field=IntegerField())
    )

    header = ['City']
    header += [{'column_name': 'Drafted', 'extra_column_name': 'Drafted(%)', 'split': 'true'}]
    header += [{'column_name': 'Finalized', 'extra_column_name': 'Finalized(%)', 'split': 'true'}]
    header += [{'column_name': 'Approved', 'extra_column_name': 'Approved(%)', 'split': 'true'}]

    response_data = [header, ]

    for data in queryset:
        total = data.get('total_wards')
        drafted = data.get('drafted')
        finalized = data.get('finalized')
        approved = data.get('approved')
        response_data.append([
            data.get('city__name'),
            '{0:.0f}%'.format(drafted * 100 / total if total else 0.0) + ' (' + str(drafted) + ')',
            '{0:.0f}%'.format(finalized * 100 / total if total else 0.0) + ' (' + str(finalized) + ')',
            '{0:.0f}%'.format(approved * 100 / total if total else 0.0) + ' (' + str(approved) + ')'
        ])

    return response_data


def get_ugp_standing_committee_indicator_table_data(from_time=None, to_time=None):
    ugp_queryset = UrbanGovernanceAndPlanning.objects.exclude(
        standing_committee_ward_no=""
    ).using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        ugp_queryset = ugp_queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = ugp_queryset.order_by('city__name').values('city__name').annotate(
        total_wards=Sum(
            Case(When(Q(standing_committee_ward_no__isnull=True) | Q(standing_committee_ward_no=""), then=0),
                 default=1),
            output_field=IntegerField()),
        established_wards=Sum(Case(When(standing_committee_established='Yes', then=1),
                                   default=0),
                              output_field=IntegerField()),
        functional_wards=Sum(Case(When(standing_committee_functional='Yes', then=1),
                                  default=0),
                             output_field=IntegerField())
    )

    header = ['City']
    header += ['Total Standing Committee']
    header += [
        {
            'column_name': 'No of Established Standing Committee',
            'extra_column_name': 'No of Established Standing Committee(%)',
            'split': 'true'
        }
    ]
    header += [
        {
            'column_name': 'No of Functional Standing Committee',
            'extra_column_name': 'No of Functional Standing Committee(%)',
            'split': 'true'
        }
    ]

    response_data = [header, ]

    for data in queryset:
        total = data.get('total_wards')
        established = data.get('established_wards')
        functional = data.get('functional_wards')
        response_data.append([
            data.get('city__name'), str(total),
            '{0:.0f}%'.format(established * 100 / total if total else 0.0) + ' (' + str(established) + ')',
            '{0:.0f}%'.format(functional * 100 / total if total else 0.0) + ' (' + str(functional) + ')'
        ])

    return response_data
