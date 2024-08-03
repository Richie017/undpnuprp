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


def get_disability_status_of_grantee_stack_bar_chart_data():
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]
    disability_label_list = ['Difficulty in Seeing', 'Difficulty in Hearing', 'Difficulty in Walking',
                             'Difficulty in Remembering', 'Difficulty in Self Care', 'Difficulty in Communicating']
    disability_options = ['No difficulty', 'Some difficulty', 'A lot of difficulty', 'Cannot do at all']
    difficulty_matrix = OrderedDict()
    total_no_grantee = 0

    for option in disability_options:
        difficulty_matrix[option] = OrderedDict()
        for disability_label in disability_label_list:
            difficulty_matrix[option][disability_label] = 0

    for grantee in grantees:
        disability_queryset = grantee.objects

        total_no_grantee += disability_queryset.count()

        for disability_label in disability_label_list:
            disability_model_field = disability_label.lower().replace(' ', '_')
            disability_info = disability_queryset.aggregate(
                **{option: Count(
                    Case(When(Q(**{disability_model_field: option}), then=1), output_field=IntegerField())) for option
                   in disability_options}
            )
            for option in disability_options:
                difficulty_matrix[option][disability_label] += disability_info[option]

    series = list()
    for option in disability_options:
        data = list()
        for label in disability_label_list:
            _value = difficulty_matrix[option][label] / total_no_grantee * 100 if total_no_grantee else 0
            data.append(_value)
        series.append({
            'name': option,
            'data': data
        })

    return series, disability_label_list


def get_disability_status_of_grantee_data_table_data(towns=list):
    grantees = [SEFApprenticeshipGrantee, SEFBusinessGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]
    disability_label_list = ['Difficulty in Seeing', 'Difficulty in Hearing', 'Difficulty in Walking',
                             'Difficulty in Remembering', 'Difficulty in Self Care', 'Difficulty in Communicating']
    response_data = []
    grantee_wise_disability = OrderedDict()
    no_of_grantee_dict = dict()

    header_row = ['Type of Grant', 'Total Respondent']
    for disability_label in disability_label_list:
        header_row += [
            {'column_name': disability_label, 'extra_column_name': '{}(%)'.format(disability_label), 'split': 'true'}]

    for grantee in grantees:
        disability_queryset = grantee.objects

        if towns:
            disability_queryset = disability_queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__pk__in=towns)

        total_no_grantee = disability_queryset.count()
        no_of_grantee_dict[grantee.get_model_meta('route', 'display_name')] = total_no_grantee
        disability_info = disability_queryset.aggregate(
            **{
                disability_label: Count(
                    Case(
                        When(Q(**{disability_label.lower().replace(' ', '_'): 'A lot of difficulty'}), then=1),
                        When(Q(**{disability_label.lower().replace(' ', '_'): 'Cannot do at all'}), then=1),
                        output_field=IntegerField()
                    )) for disability_label in disability_label_list
                }
        )
        grantee_wise_disability[grantee.get_model_meta('route', 'display_name')] = disability_info

    response_data.append(header_row)

    footer_row = [0] * (len(header_row) - 1)

    for grantee_name, dis_infos in grantee_wise_disability.items():
        total_no_grantee = no_of_grantee_dict[grantee_name]
        row = [grantee_name.replace('Grantees', 'Grantees'), str(total_no_grantee)]
        col = 0
        footer_row[col] += total_no_grantee
        for label in disability_label_list:
            dis_no = dis_infos[label]
            disable_in_percent = dis_no / total_no_grantee * 100 if total_no_grantee else 0
            row.append(("{0:.0f}%".format(disable_in_percent) + ' (' + str(dis_no) + ')'))
            col += 1
            footer_row[col] += dis_no
        response_data.append(row)

    last_row = ['Total (all cities)', str(footer_row[0])]
    for i in range(len(footer_row) - 1):
        dis_no = footer_row[i + 1]
        disable_in_percent = dis_no / footer_row[0] * 100 if footer_row[0] else 0
        last_row.append(("{0:.0f}%".format(disable_in_percent) + ' (' + str(dis_no) + ')'))
    response_data.append(last_row)

    return response_data


def get_disability_status_of_grantee_pie_chart_data():
    grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                SEFEducationChildMarriageGrantee, SEFNutritionGrantee]
    disability_label_list = ['Difficulty in Seeing', 'Difficulty in Hearing', 'Difficulty in Walking',
                             'Difficulty in Remembering', 'Difficulty in Self Care', 'Difficulty in Communicating']
    disability_options = ['No difficulty', 'Some difficulty', 'A lot of difficulty', 'Cannot do at all']
    difficulty_matrix = OrderedDict()
    grantee_having_no_difficulty = 0
    grantee_having_difficulty = 0  # who have a lot of difficulty or cannot do at all

    for option in disability_options:
        difficulty_matrix[option] = OrderedDict()
        for disability_label in disability_label_list:
            difficulty_matrix[option][disability_label] = 0

    for grantee in grantees:
        disability_queryset = grantee.objects

        for disability_label in disability_label_list:
            disability_model_field = disability_label.lower().replace(' ', '_')
            disability_info = disability_queryset.aggregate(
                **{option: Count(
                    Case(When(Q(**{disability_model_field: option}), then=1), output_field=IntegerField())) for option
                   in disability_options}
            )
            if disability_info['No difficulty'] > 0:
                grantee_having_no_difficulty += disability_info['No difficulty']
            if disability_info['A lot of difficulty'] > 0:
                grantee_having_difficulty += disability_info['A lot of difficulty']
            if disability_info['Cannot do at all'] > 0:
                grantee_having_difficulty += disability_info['Cannot do at all']

    report_data = [
        {
            'name': "No difficulty",
            'y': grantee_having_no_difficulty
        },
        {
            'name': "This includes respondents who have a lot of difficulties <br>"
                    "or cannot do the following functions at all: seeing, <br>"
                    "hearing, walking, remembering, self-care, communicating",
            'y': grantee_having_difficulty
        }
    ]
    report = {
        'name': 'Count',
        'data': report_data
    }
    return [report]
