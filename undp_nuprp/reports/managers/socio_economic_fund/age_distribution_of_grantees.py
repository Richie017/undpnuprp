from collections import OrderedDict

from django.db.models.aggregates import Count
from django.db.models.expressions import Case, When
from django.db.models.fields import IntegerField
from django.db.models.query_utils import Q

from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_apprenticeship_grantee import \
    SEFApprenticeshipGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_business_grantee import SEFBusinessGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_dropout_grantee import \
    SEFEducationDropoutGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_early_marriage_grantee import \
    SEFEducationChildMarriageGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_nutrition_grantee import SEFNutritionGrantee

__author__ = 'Shuvro'


def get_age_distributor_of_grantees_table_data(towns=list):
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    grantee_wise_age_dict = OrderedDict()
    total_below_20 = total_range_20_29 = total_range_30_39 = total_range_40_49 = total_range_50_59 = total_above_59 = 0

    header = ['Type of Grant']
    header += [{'column_name': 'Below 20', 'extra_column_name': 'Below 20(%)', 'split': 'true'}]
    header += [{'column_name': '20-29', 'extra_column_name': '20-29(%)', 'split': 'true'}]
    header += [{'column_name': '30-39', 'extra_column_name': '30-39(%)', 'split': 'true'}]
    header += [{'column_name': '40-49', 'extra_column_name': '40-49(%)', 'split': 'true'}]
    header += [{'column_name': '50-59', 'extra_column_name': '50-59(%)', 'split': 'true'}]
    header += [{'column_name': '60 and above', 'extra_column_name': '60 and above(%)', 'split': 'true'}]
    response_data = [header]

    for grantee in grantees:
        grantee_queryset = grantee.objects
        if towns:
            grantee_queryset = grantee_queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)

        grantee_age_info = grantee_queryset.aggregate(
            below_20=Count(Case(When(age__lt=20, then=1), output_field=IntegerField())),
            range_20_29=Count(Case(When(Q(age__gt=19, age__lt=30), then=1), output_field=IntegerField())),
            range_30_39=Count(Case(When(Q(age__gt=29, age__lt=40), then=1), output_field=IntegerField())),
            range_40_49=Count(Case(When(Q(age__gt=39, age__lt=50), then=1), output_field=IntegerField())),
            range_50_59=Count(Case(When(Q(age__gt=49, age__lt=60), then=1), output_field=IntegerField())),
            above_59=Count(Case(When(age__gt=59, then=1), output_field=IntegerField())),
            total=Count(Case(When(age__isnull=False, then=1), output_field=IntegerField()))
        )
        grantee_wise_age_dict[grantee.__name__] = grantee_age_info
        total_below_20 += grantee_age_info['below_20']
        total_range_20_29 += grantee_age_info['range_20_29']
        total_range_30_39 += grantee_age_info['range_30_39']
        total_range_40_49 += grantee_age_info['range_40_49']
        total_range_50_59 += grantee_age_info['range_50_59']
        total_above_59 += grantee_age_info['above_59']

    for grantee in grantees:
        grantee_age_info = grantee_wise_age_dict[grantee.__name__]
        num_of_grantee = grantee_age_info['total']
        response_data.append([
            grantee.get_model_meta('route', 'display_name').replace('Grantees', ''),
            '{0:.0f}%'.format(
                grantee_age_info['below_20'] / num_of_grantee * 100 if num_of_grantee else 0) + ' (' + str(
                grantee_age_info['below_20']) + ')',
            '{0:.0f}%'.format(
                grantee_age_info['range_20_29'] / num_of_grantee * 100 if num_of_grantee else 0) + ' (' + str(
                grantee_age_info['range_20_29']) + ')',
            '{0:.0f}%'.format(
                grantee_age_info['range_30_39'] / num_of_grantee * 100 if num_of_grantee else 0) + ' (' + str(
                grantee_age_info['range_30_39']) + ')',
            '{0:.0f}%'.format(
                grantee_age_info['range_40_49'] / num_of_grantee * 100 if num_of_grantee else 0) + ' (' + str(
                grantee_age_info['range_40_49']) + ')',
            '{0:.0f}%'.format(
                grantee_age_info['range_50_59'] / num_of_grantee * 100 if num_of_grantee else 0) + ' (' + str(
                grantee_age_info['range_50_59']) + ')',
            '{0:.0f}%'.format(
                grantee_age_info['above_59'] / num_of_grantee * 100 if num_of_grantee else 0) + ' (' + str(
                grantee_age_info['above_59']) + ')'
        ])

    total_grantee = total_below_20 + total_range_20_29 + total_range_30_39 + total_range_40_49 + total_range_50_59 + \
        total_above_59

    response_data.append(
        ['Total', '{0:.0f}% ({1})'.format(total_below_20 / total_grantee * 100, total_below_20),
         '{0:.0f}% ({1})'.format(total_range_20_29 / total_grantee * 100, total_range_20_29),
         '{0:.0f}% ({1})'.format(total_range_30_39 / total_grantee * 100, total_range_30_39),
         '{0:.0f}% ({1})'.format(total_range_40_49 / total_grantee * 100, total_range_40_49),
         '{0:.0f}% ({1})'.format(total_range_50_59 / total_grantee * 100, total_range_50_59),
         '{0:.0f}% ({1})'.format(total_above_59 / total_grantee * 100, total_above_59)])

    return response_data


def get_age_distributor_of_grantees_pie_chart_data():
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]
    total_below_20 = total_range_20_29 = total_range_30_39 = total_range_40_49 = total_range_50_59 = total_above_59 = 0

    for grantee in grantees:
        grantee_queryset = grantee.objects.all()

        grantee_age_info = grantee_queryset.aggregate(
            below_20=Count(Case(When(age__lt=20, then=1), output_field=IntegerField())),
            range_20_29=Count(Case(When(Q(age__gt=19, age__lt=30), then=1), output_field=IntegerField())),
            range_30_39=Count(Case(When(Q(age__gt=29, age__lt=40), then=1), output_field=IntegerField())),
            range_40_49=Count(Case(When(Q(age__gt=39, age__lt=50), then=1), output_field=IntegerField())),
            range_50_59=Count(Case(When(Q(age__gt=49, age__lt=60), then=1), output_field=IntegerField())),
            above_59=Count(Case(When(age__gt=59, then=1), output_field=IntegerField()))
        )
        total_below_20 += grantee_age_info['below_20']
        total_range_20_29 += grantee_age_info['range_20_29']
        total_range_30_39 += grantee_age_info['range_30_39']
        total_range_40_49 += grantee_age_info['range_40_49']
        total_range_50_59 += grantee_age_info['range_50_59']
        total_above_59 += grantee_age_info['above_59']

    report = [
        {
            'name': 'Age distribution of grantees',
            'data': [
                {
                    'name': 'Below 20',
                    'y': total_below_20
                },
                {
                    'name': '20-29',
                    'y': total_range_20_29
                },
                {
                    'name': '30-39',
                    'y': total_range_30_39
                },
                {
                    'name': '40-49',
                    'y': total_range_40_49
                },
                {
                    'name': '50-59',
                    'y': total_range_50_59
                },
                {
                    'name': '60 and above',
                    'y': total_above_59
                }
            ]
        }
    ]

    return report
