from collections import OrderedDict

from django.db.models.aggregates import Count
from django.db.models.expressions import When, Case
from django.db.models.fields import IntegerField

from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_apprenticeship_grantee import \
    SEFApprenticeshipGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_business_grantee import SEFBusinessGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_dropout_grantee import \
    SEFEducationDropoutGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_early_marriage_grantee import \
    SEFEducationChildMarriageGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_nutrition_grantee import SEFNutritionGrantee
from undp_nuprp.reports.utils.thousand_separator import thousand_separator


def get_gender_of_grantee_table_data(towns=None):
    if towns is None:
        towns = list()
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    grantee_wise_gender_dict = OrderedDict()
    total_male = 0
    total_female = 0
    total_hijra = 0

    header = ['Type of Grant']
    header += [{'column_name': 'Male', 'extra_column_name': 'Male(%)', 'split': 'true'}]
    header += [{'column_name': 'Female', 'extra_column_name': 'Female(%)', 'split': 'true'}]
    header += [{'column_name': 'Hijra', 'extra_column_name': 'Hijra(%)', 'split': 'true'}]
    response_data = [header]

    for grantee in grantees:
        grantee_queryset = grantee.objects.all()
        if towns:
            grantee_queryset = grantee_queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)

        grantee_gender_info = grantee_queryset.aggregate(
            male=Count(Case(When(gender='Male', then=1), output_field=IntegerField())),
            female=Count(Case(When(gender='Female', then=1), output_field=IntegerField())),
            hijra=Count(Case(When(gender='Hijra', then=1), output_field=IntegerField())),
            total=Count(Case(When(gender__isnull=False, then=1), output_field=IntegerField()))
        )
        grantee_wise_gender_dict[grantee.__name__] = grantee_gender_info
        total_male += grantee_gender_info['male']
        total_female += grantee_gender_info['female']
        total_hijra += grantee_gender_info['hijra']

    grand_total_grantee = 0

    for grantee in grantees:
        grantee_gender_info = grantee_wise_gender_dict[grantee.__name__]
        number_of_grantee = grantee_gender_info['total']
        grand_total_grantee += number_of_grantee
        response_data.append([
            grantee.get_model_meta('route', 'display_name').replace('Grantees', ''),
            '{0:.0f}%'.format(
                grantee_gender_info['male'] / number_of_grantee * 100 if number_of_grantee else 0) + ' (' + thousand_separator(int(
                grantee_gender_info['male'])) + ')',
            '{0:.0f}%'.format(
                grantee_gender_info['female'] / number_of_grantee * 100 if number_of_grantee else 0) + ' (' + thousand_separator(int(
                grantee_gender_info['female'])) + ')',
            '{0:.0f}%'.format(
                grantee_gender_info['hijra'] / number_of_grantee * 100 if number_of_grantee else 0) + ' (' + thousand_separator(int(
                grantee_gender_info['hijra'])) + ')'
        ])

    response_data.append(['Total',
                          '{0:.0f}% ({1})'.format(total_male / grand_total_grantee * 100 if grand_total_grantee else 0,
                                                  thousand_separator(int(total_male))),
                          '{0:.0f}% ({1})'.format(
                              total_female / grand_total_grantee * 100 if grand_total_grantee else 0,
                              thousand_separator(int(total_female))),
                          '{0:.0f}% ({1})'.format(total_hijra / grand_total_grantee * 100 if grand_total_grantee else 0,
                                                  thousand_separator(int(total_hijra)))
                          ])
    return response_data


def get_gender_of_grantee_pie_chart_data():
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]

    total_male = 0
    total_female = 0
    total_hijra = 0

    for grantee in grantees:
        grantee_queryset = grantee.objects.all()

        grantee_gender_info = grantee_queryset.aggregate(
            male=Count(Case(When(gender='Male', then=1), output_field=IntegerField())),
            female=Count(Case(When(gender='Female', then=1), output_field=IntegerField())),
            hijra=Count(Case(When(gender='Hijra', then=1), output_field=IntegerField()))
        )
        total_male += grantee_gender_info['male']
        total_female += grantee_gender_info['female']
        total_hijra += grantee_gender_info['hijra']

    report = [
        {
            'name': 'Gender of grantees',
            'data': [
                {
                    'name': 'Male',
                    'y': total_male
                },
                {
                    'name': 'Female',
                    'y': total_female
                },
                {
                    'name': 'Hijra',
                    'y': total_hijra
                }
            ]
        }
    ]

    return report
