import calendar
from datetime import date

from django.db.models import Sum

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import NutritionRegistration, NutritionConditionalFoodTransfer


def get_nutrition_registration_indicator_table_data_1(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionRegistration.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_pregnant_women_by_age_lt_20=Sum('no_of_pregnant_women_by_age_lt_20'),
        sum_no_of_pregnant_women_by_age_20_25=Sum('no_of_pregnant_women_by_age_20_25'),
        sum_no_of_pregnant_women_by_age_26_30=Sum('no_of_pregnant_women_by_age_26_30'),
        sum_no_of_pregnant_women_by_age_31_35=Sum('no_of_pregnant_women_by_age_31_35'),
        sum_no_of_pregnant_women_by_age_36_40=Sum('no_of_pregnant_women_by_age_36_40'),
        sum_no_of_pregnant_women_by_age_41_45=Sum('no_of_pregnant_women_by_age_41_45'),
        sum_no_of_pregnant_women_by_age_46_50=Sum('no_of_pregnant_women_by_age_46_50'),
        sum_no_of_pregnant_women_by_age_gt_50=Sum('no_of_pregnant_women_by_age_gt_50')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_lt_20'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_20_25'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_26_30'))['total']
    tot_4 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_31_35'))['total']
    tot_5 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_36_40'))['total']
    tot_6 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_41_45'))['total']
    tot_7 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_46_50'))['total']
    tot_8 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_gt_50'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of pregnant women by age below 20',
                       'extra_column_name': 'No of pregnant women by age below 20(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 20-25',
                       'extra_column_name': 'No of pregnant women by age 20-25(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 26-30',
                       'extra_column_name': 'No of pregnant women by age 26-30(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 31-35',
                       'extra_column_name': 'No of pregnant women by age 31-35(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 36-40',
                       'extra_column_name': 'No of pregnant women by age 36-40(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 41-45',
                       'extra_column_name': 'No of pregnant women by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 41-45',
                       'extra_column_name': 'No of pregnant women by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age above 50',
                       'extra_column_name': 'No of pregnant women by age above 50(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_pregnant_women_by_age_lt_20')
        c2 = data.get('sum_no_of_pregnant_women_by_age_20_25')
        c3 = data.get('sum_no_of_pregnant_women_by_age_26_30')
        c4 = data.get('sum_no_of_pregnant_women_by_age_31_35')
        c5 = data.get('sum_no_of_pregnant_women_by_age_36_40')
        c6 = data.get('sum_no_of_pregnant_women_by_age_41_45')
        c7 = data.get('sum_no_of_pregnant_women_by_age_46_50')
        c8 = data.get('sum_no_of_pregnant_women_by_age_gt_50')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')',
                              '{0:.0f}%'.format(c4 * 100 / tot_4 if tot_4 else 0.0) + ' (' + str(c4) + ')',
                              '{0:.0f}%'.format(c5 * 100 / tot_5 if tot_5 else 0.0) + ' (' + str(c5) + ')',
                              '{0:.0f}%'.format(c6 * 100 / tot_6 if tot_6 else 0.0) + ' (' + str(c6) + ')',
                              '{0:.0f}%'.format(c7 * 100 / tot_7 if tot_7 else 0.0) + ' (' + str(c7) + ')',
                              '{0:.0f}%'.format(c8 * 100 / tot_8 if tot_8 else 0.0) + ' (' + str(c8) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')',
                          '100% (' + str(tot_4) + ')',
                          '100% (' + str(tot_5) + ')',
                          '100% (' + str(tot_6) + ')',
                          '100% (' + str(tot_7) + ')',
                          '100% (' + str(tot_8) + ')'
                          ])

    return response_data


def get_nutrition_registration_indicator_table_data_2(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionRegistration.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_lactating_mothers_by_age_lt_20=Sum('no_of_lactating_mothers_by_age_lt_20'),
        sum_no_of_lactating_mothers_by_age_20_25=Sum('no_of_lactating_mothers_by_age_20_25'),
        sum_no_of_lactating_mothers_by_age_26_30=Sum('no_of_lactating_mothers_by_age_26_30'),
        sum_no_of_lactating_mothers_by_age_31_35=Sum('no_of_lactating_mothers_by_age_31_35'),
        sum_no_of_lactating_mothers_by_age_36_40=Sum('no_of_lactating_mothers_by_age_36_40'),
        sum_no_of_lactating_mothers_by_age_41_45=Sum('no_of_lactating_mothers_by_age_41_45'),
        sum_no_of_lactating_mothers_by_age_46_50=Sum('no_of_lactating_mothers_by_age_46_50'),
        sum_no_of_lactating_mothers_by_age_gt_50=Sum('no_of_lactating_mothers_by_age_gt_50')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_lt_20'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_20_25'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_26_30'))['total']
    tot_4 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_31_35'))['total']
    tot_5 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_36_40'))['total']
    tot_6 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_41_45'))['total']
    tot_7 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_46_50'))['total']
    tot_8 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_gt_50'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of lactating mothers by age below 20',
                       'extra_column_name': 'No of lactating mothers by age below 20(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 20-25',
                       'extra_column_name': 'No of lactating mothers by age 20-25(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 26-30',
                       'extra_column_name': 'No of lactating mothers by age 26-30(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 31-35',
                       'extra_column_name': 'No of lactating mothers by age 31-35(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 36-40',
                       'extra_column_name': 'No of lactating mothers by age 36-40(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 41-45',
                       'extra_column_name': 'No of lactating mothers by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 41-45',
                       'extra_column_name': 'No of lactating mothers by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age above 50',
                       'extra_column_name': 'No of lactating mothers by age above 50(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_lactating_mothers_by_age_lt_20')
        c2 = data.get('sum_no_of_lactating_mothers_by_age_20_25')
        c3 = data.get('sum_no_of_lactating_mothers_by_age_26_30')
        c4 = data.get('sum_no_of_lactating_mothers_by_age_31_35')
        c5 = data.get('sum_no_of_lactating_mothers_by_age_36_40')
        c6 = data.get('sum_no_of_lactating_mothers_by_age_41_45')
        c7 = data.get('sum_no_of_lactating_mothers_by_age_46_50')
        c8 = data.get('sum_no_of_lactating_mothers_by_age_gt_50')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')',
                              '{0:.0f}%'.format(c4 * 100 / tot_4 if tot_4 else 0.0) + ' (' + str(c4) + ')',
                              '{0:.0f}%'.format(c5 * 100 / tot_5 if tot_5 else 0.0) + ' (' + str(c5) + ')',
                              '{0:.0f}%'.format(c6 * 100 / tot_6 if tot_6 else 0.0) + ' (' + str(c6) + ')',
                              '{0:.0f}%'.format(c7 * 100 / tot_7 if tot_7 else 0.0) + ' (' + str(c7) + ')',
                              '{0:.0f}%'.format(c8 * 100 / tot_8 if tot_8 else 0.0) + ' (' + str(c8) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')',
                          '100% (' + str(tot_4) + ')',
                          '100% (' + str(tot_5) + ')',
                          '100% (' + str(tot_6) + ')',
                          '100% (' + str(tot_7) + ')',
                          '100% (' + str(tot_8) + ')'
                          ])

    return response_data


def get_nutrition_registration_indicator_table_data_3(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionRegistration.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_child_0_6_months_by_male=Sum('no_of_child_0_6_months_by_male'),
        sum_no_of_child_0_6_months_by_female=Sum('no_of_child_0_6_months_by_female'),
        sum_no_of_child_0_6_months_by_transgender=Sum('no_of_child_0_6_months_by_transgender')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_child_0_6_months_by_male'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_child_0_6_months_by_female'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_child_0_6_months_by_transgender'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of child 0-6 months by Male',
                       'extra_column_name': 'No of child 0-6 months by Male(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 0-6 months by Female',
                       'extra_column_name': 'No of child 0-6 months by Female(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 0-6 months by Transgender',
                       'extra_column_name': 'No of child 0-6 months by Transgender(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_child_0_6_months_by_male')
        c2 = data.get('sum_no_of_child_0_6_months_by_female')
        c3 = data.get('sum_no_of_child_0_6_months_by_transgender')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')'
                          ])

    return response_data


def get_nutrition_registration_indicator_table_data_4(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionRegistration.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_child_7_24_months_by_male=Sum('no_of_child_7_24_months_by_male'),
        sum_no_of_child_7_24_months_by_female=Sum('no_of_child_7_24_months_by_female'),
        sum_no_of_child_7_24_months_by_transgender=Sum('no_of_child_7_24_months_by_transgender')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_child_7_24_months_by_male'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_child_7_24_months_by_female'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_child_7_24_months_by_transgender'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of child 7-24 months by Male',
                       'extra_column_name': 'No of child 7-24 months by Male(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 7-24 months by Female',
                       'extra_column_name': 'No of child 7-24 months by Female(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 7-24 months by Transgender',
                       'extra_column_name': 'No of child 7-24 months by Transgender(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_child_7_24_months_by_male')
        c2 = data.get('sum_no_of_child_7_24_months_by_female')
        c3 = data.get('sum_no_of_child_7_24_months_by_transgender')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')'
                          ])

    return response_data


def get_nutrition_conditional_food_transfer_indicator_table_data_1(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionConditionalFoodTransfer.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_pregnant_women_by_age_lt_20=Sum('no_of_pregnant_women_by_age_lt_20'),
        sum_no_of_pregnant_women_by_age_20_25=Sum('no_of_pregnant_women_by_age_20_25'),
        sum_no_of_pregnant_women_by_age_26_30=Sum('no_of_pregnant_women_by_age_26_30'),
        sum_no_of_pregnant_women_by_age_31_35=Sum('no_of_pregnant_women_by_age_31_35'),
        sum_no_of_pregnant_women_by_age_36_40=Sum('no_of_pregnant_women_by_age_36_40'),
        sum_no_of_pregnant_women_by_age_41_45=Sum('no_of_pregnant_women_by_age_41_45'),
        sum_no_of_pregnant_women_by_age_46_50=Sum('no_of_pregnant_women_by_age_46_50'),
        sum_no_of_pregnant_women_by_age_gt_50=Sum('no_of_pregnant_women_by_age_gt_50')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_lt_20'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_20_25'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_26_30'))['total']
    tot_4 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_31_35'))['total']
    tot_5 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_36_40'))['total']
    tot_6 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_41_45'))['total']
    tot_7 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_46_50'))['total']
    tot_8 = queryset.aggregate(total=Sum('sum_no_of_pregnant_women_by_age_gt_50'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of pregnant women by age below 20',
                       'extra_column_name': 'No of pregnant women by age below 20(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 20-25',
                       'extra_column_name': 'No of pregnant women by age 20-25(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 26-30',
                       'extra_column_name': 'No of pregnant women by age 26-30(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 31-35',
                       'extra_column_name': 'No of pregnant women by age 31-35(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 36-40',
                       'extra_column_name': 'No of pregnant women by age 36-40(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 41-45',
                       'extra_column_name': 'No of pregnant women by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age 41-45',
                       'extra_column_name': 'No of pregnant women by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of pregnant women by age above 50',
                       'extra_column_name': 'No of pregnant women by age above 50(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_pregnant_women_by_age_lt_20')
        c2 = data.get('sum_no_of_pregnant_women_by_age_20_25')
        c3 = data.get('sum_no_of_pregnant_women_by_age_26_30')
        c4 = data.get('sum_no_of_pregnant_women_by_age_31_35')
        c5 = data.get('sum_no_of_pregnant_women_by_age_36_40')
        c6 = data.get('sum_no_of_pregnant_women_by_age_41_45')
        c7 = data.get('sum_no_of_pregnant_women_by_age_46_50')
        c8 = data.get('sum_no_of_pregnant_women_by_age_gt_50')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')',
                              '{0:.0f}%'.format(c4 * 100 / tot_4 if tot_4 else 0.0) + ' (' + str(c4) + ')',
                              '{0:.0f}%'.format(c5 * 100 / tot_5 if tot_5 else 0.0) + ' (' + str(c5) + ')',
                              '{0:.0f}%'.format(c6 * 100 / tot_6 if tot_6 else 0.0) + ' (' + str(c6) + ')',
                              '{0:.0f}%'.format(c7 * 100 / tot_7 if tot_7 else 0.0) + ' (' + str(c7) + ')',
                              '{0:.0f}%'.format(c8 * 100 / tot_8 if tot_8 else 0.0) + ' (' + str(c8) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')',
                          '100% (' + str(tot_4) + ')',
                          '100% (' + str(tot_5) + ')',
                          '100% (' + str(tot_6) + ')',
                          '100% (' + str(tot_7) + ')',
                          '100% (' + str(tot_8) + ')'
                          ])

    return response_data


def get_nutrition_conditional_food_transfer_indicator_table_data_2(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionConditionalFoodTransfer.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_lactating_mothers_by_age_lt_20=Sum('no_of_lactating_mothers_by_age_lt_20'),
        sum_no_of_lactating_mothers_by_age_20_25=Sum('no_of_lactating_mothers_by_age_20_25'),
        sum_no_of_lactating_mothers_by_age_26_30=Sum('no_of_lactating_mothers_by_age_26_30'),
        sum_no_of_lactating_mothers_by_age_31_35=Sum('no_of_lactating_mothers_by_age_31_35'),
        sum_no_of_lactating_mothers_by_age_36_40=Sum('no_of_lactating_mothers_by_age_36_40'),
        sum_no_of_lactating_mothers_by_age_41_45=Sum('no_of_lactating_mothers_by_age_41_45'),
        sum_no_of_lactating_mothers_by_age_46_50=Sum('no_of_lactating_mothers_by_age_46_50'),
        sum_no_of_lactating_mothers_by_age_gt_50=Sum('no_of_lactating_mothers_by_age_gt_50')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_lt_20'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_20_25'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_26_30'))['total']
    tot_4 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_31_35'))['total']
    tot_5 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_36_40'))['total']
    tot_6 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_41_45'))['total']
    tot_7 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_46_50'))['total']
    tot_8 = queryset.aggregate(total=Sum('sum_no_of_lactating_mothers_by_age_gt_50'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of lactating mothers by age below 20',
                       'extra_column_name': 'No of lactating mothers by age below 20(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 20-25',
                       'extra_column_name': 'No of lactating mothers by age 20-25(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 26-30',
                       'extra_column_name': 'No of lactating mothers by age 26-30(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 31-35',
                       'extra_column_name': 'No of lactating mothers by age 31-35(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 36-40',
                       'extra_column_name': 'No of lactating mothers by age 36-40(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 41-45',
                       'extra_column_name': 'No of lactating mothers by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age 41-45',
                       'extra_column_name': 'No of lactating mothers by age 41-45(%)',
                       'split': 'true'},
                      {'column_name': 'No of lactating mothers by age above 50',
                       'extra_column_name': 'No of lactating mothers by age above 50(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_lactating_mothers_by_age_lt_20')
        c2 = data.get('sum_no_of_lactating_mothers_by_age_20_25')
        c3 = data.get('sum_no_of_lactating_mothers_by_age_26_30')
        c4 = data.get('sum_no_of_lactating_mothers_by_age_31_35')
        c5 = data.get('sum_no_of_lactating_mothers_by_age_36_40')
        c6 = data.get('sum_no_of_lactating_mothers_by_age_41_45')
        c7 = data.get('sum_no_of_lactating_mothers_by_age_46_50')
        c8 = data.get('sum_no_of_lactating_mothers_by_age_gt_50')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')',
                              '{0:.0f}%'.format(c4 * 100 / tot_4 if tot_4 else 0.0) + ' (' + str(c4) + ')',
                              '{0:.0f}%'.format(c5 * 100 / tot_5 if tot_5 else 0.0) + ' (' + str(c5) + ')',
                              '{0:.0f}%'.format(c6 * 100 / tot_6 if tot_6 else 0.0) + ' (' + str(c6) + ')',
                              '{0:.0f}%'.format(c7 * 100 / tot_7 if tot_7 else 0.0) + ' (' + str(c7) + ')',
                              '{0:.0f}%'.format(c8 * 100 / tot_8 if tot_8 else 0.0) + ' (' + str(c8) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')',
                          '100% (' + str(tot_4) + ')',
                          '100% (' + str(tot_5) + ')',
                          '100% (' + str(tot_6) + ')',
                          '100% (' + str(tot_7) + ')',
                          '100% (' + str(tot_8) + ')'
                          ])

    return response_data


def get_nutrition_conditional_food_transfer_indicator_table_data_3(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionConditionalFoodTransfer.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_child_0_6_months_by_male=Sum('no_of_child_0_6_months_by_male'),
        sum_no_of_child_0_6_months_by_female=Sum('no_of_child_0_6_months_by_female'),
        sum_no_of_child_0_6_months_by_transgender=Sum('no_of_child_0_6_months_by_transgender')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_child_0_6_months_by_male'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_child_0_6_months_by_female'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_child_0_6_months_by_transgender'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of child 0-6 months by Male',
                       'extra_column_name': 'No of child 0-6 months by Male(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 0-6 months by Female',
                       'extra_column_name': 'No of child 0-6 months by Female(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 0-6 months by Transgender',
                       'extra_column_name': 'No of child 0-6 months by Transgender(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_child_0_6_months_by_male')
        c2 = data.get('sum_no_of_child_0_6_months_by_female')
        c3 = data.get('sum_no_of_child_0_6_months_by_transgender')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')'
                          ])

    return response_data


def get_nutrition_conditional_food_transfer_indicator_table_data_4(from_time=None, to_time=None, year=None, month=None):
    queryset = NutritionConditionalFoodTransfer.objects.all().using(BWDatabaseRouter.get_read_database_name())
    if from_time and to_time:
        queryset = queryset.filter(date_created__gte=from_time - 1000, date_created__lte=to_time + 1000)
    queryset = queryset.filter(year=int(year), month=int(month)).order_by('city__name').values('city__name').annotate(
        sum_no_of_child_7_24_months_by_male=Sum('no_of_child_7_24_months_by_male'),
        sum_no_of_child_7_24_months_by_female=Sum('no_of_child_7_24_months_by_female'),
        sum_no_of_child_7_24_months_by_transgender=Sum('no_of_child_7_24_months_by_transgender')
    )

    tot_1 = queryset.aggregate(total=Sum('sum_no_of_child_7_24_months_by_male'))['total']
    tot_2 = queryset.aggregate(total=Sum('sum_no_of_child_7_24_months_by_female'))['total']
    tot_3 = queryset.aggregate(total=Sum('sum_no_of_child_7_24_months_by_transgender'))['total']

    response_data = [['City', 'Month',
                      {'column_name': 'No of child 7-24 months by Male',
                       'extra_column_name': 'No of child 7-24 months by Male(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 7-24 months by Female',
                       'extra_column_name': 'No of child 7-24 months by Female(%)',
                       'split': 'true'},
                      {'column_name': 'No of child 7-24 months by Transgender',
                       'extra_column_name': 'No of child 7-24 months by Transgender(%)',
                       'split': 'true'}
                      ]]

    for data in queryset:
        c1 = data.get('sum_no_of_child_7_24_months_by_male')
        c2 = data.get('sum_no_of_child_7_24_months_by_female')
        c3 = data.get('sum_no_of_child_7_24_months_by_transgender')
        response_data.append([data.get('city__name') or 'Unassigned', calendar.month_name[int(month)],
                              '{0:.0f}%'.format(c1 * 100 / tot_1 if tot_1 else 0.0) + ' (' + str(c1) + ')',
                              '{0:.0f}%'.format(c2 * 100 / tot_2 if tot_2 else 0.0) + ' (' + str(c2) + ')',
                              '{0:.0f}%'.format(c3 * 100 / tot_3 if tot_3 else 0.0) + ' (' + str(c3) + ')'])
    response_data.append(['Total', '',
                          '100% (' + str(tot_1) + ')',
                          '100% (' + str(tot_2) + ')',
                          '100% (' + str(tot_3) + ')'
                          ])

    return response_data