"""
Created by tareq on 2/15/18
"""
from collections import OrderedDict

from blackwidow.core.models import FieldGroup, Organization
from blackwidow.engine.enums.field_type_enum import FieldTypesEnum
from blackwidow.engine.enums.reachout_level_enum import ReachoutLevelEnum
from undp_nuprp.approvals.models import CDCMonthlyReportField, SCGMonthlyReportField, CumulativeReportField

__author__ = 'Tareq, Ziaul Haque'

# Custom Field: ->
# assigned_code, EX:001001001 (first 3 digits for model index, next 3 for group index, last 3 for field index)

# Field Group: ->
# assigned_code, EX:001001001 (first 3 digits for app index, next 3 for model index, last 3 for group index)


def initialize_cdc_monthly_report_form(*args, **kwargs):
    organization = Organization.objects.first()
    cdc_report = OrderedDict()
    cdc_report[('001001005', 'Savings')] = OrderedDict()  # moved in 1st position to set group weight 1.
    cdc_report[('001001001', 'Loans')] = OrderedDict()
    cdc_report[('001001002', 'Service Charges & Fees')] = OrderedDict()
    cdc_report[('001001003', 'Fund Status')] = OrderedDict()
    cdc_report[('001001004', 'Records')] = OrderedDict()
    cdc_group_translation_dict = OrderedDict()

    cdc_group_translation_dict[('001001001', 'Loans')] = 'ঋণ'
    cdc_group_translation_dict[('001001002', 'Service Charges & Fees')] = 'সার্ভিস চার্জ ও ফিস'
    cdc_group_translation_dict[('001001003', 'Fund Status')] = 'তহবিলের অবস্থা'
    cdc_group_translation_dict[('001001004', 'Records')] = 'নথিপত্র'
    cdc_group_translation_dict[('001001005', 'Savings')] = 'সঞ্চয়'

    cdc_report[('001001001', 'Loans')] = [
        # ('001001001', 'Total targeted receiveable current loan for reporting month', 'চলতি মাসে মোট আদায়যোগ ঋনের পরিমান', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        # ('001001002', 'Total received (Collected) current loan for reporting month', 'চলতি মাসে মোট আদায়কৃত ঋনের পরিমান', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        # ('001001003', 'Total value of loans repaid/ collected in current month (Outstanding+overdue+Advance)', 'চলতি মাসে পরিশোধিত মোট ঋণের পরিমাণ (বকেয়া+ মেয়াদোত্তীর্ন+অগ্রিম)', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001001007', 'Value of total loans disbursed by the CDC', 'সিডিসি কর্তৃক বিতরণকৃত মোট ঋণের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001001006', 'Value of total loans received by SCG\'s', 'সঞ্চয় ও ঋণ দল কর্তৃক গৃহীত মোট ঋণের পরিমাণ', FieldTypesEnum.Calculated_Field.value, True, '', '', ReachoutLevelEnum.All.value, '002002002,002002003'),
        ('001001004', 'Value of outstanding loans', 'বকেয়া মোট ঋণের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001001005', 'Value of overdue loans', 'মেয়াদ উত্তীর্ণ (বকেয়া) ঋণের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001001008', 'Difference', '', FieldTypesEnum.Calculated_Field.value, True, '', '', ReachoutLevelEnum.MissionControl.value, '(@001001006@+@001001007@)'),
    ]

    cdc_report[('001001002', 'Service Charges & Fees')] = [
        ('001002001', 'Value of service charges(Interest collected from loans)', 'সার্ভিস চাজের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001002002', 'Value of admission fees (passbook and others)', 'সদস্য র্ভতি ফি (পাশ বই ও অন্যান্য)', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001002003', 'Value of interest collected from Bank(s)', 'ব্যাংক সুদের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001002004', 'Value of bank charges', 'ব্যাংক চার্জের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001002005', 'Value of other expenditure e.g. logistics, photocopy etc', 'অন্যান্য ক্ষেত্রে (উদাহরণস্বরূপ, উপকরণ, ফটোকপি ইত্যাদি) ব্যয়ের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001002006', 'Interest Paid on savings for the reporting period', 'প্রতিবেদন সময়কালীন সদস্যদের সঞ্চয়ের উপর সূদ প্রদান', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001002007', 'Interest payable on savings balance at end of the reporting period', 'রির্পোটিং মাস শেষে সদস্যদের সঞ্চয়ের উপর প্রদানযোগ্য সূদের স্থিতি', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
    ]

    cdc_report[('001001003', 'Fund Status')] = [
        ('001003001', 'Bank balance (at the end of the reporting month)', 'রির্পোটিং মাস পর্যন্ত ব্যাংক স্থিতি', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001003002', 'Cash in hand (at the end of the reporting month)', 'রির্পোটিং মাস পর্যন্ত হাতে নগদের মোট পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
    ]

    cdc_report[('001001004', 'Records')] = [
        ('001004001', 'Are the Savings & credit register books (All register) updated?', 'সঞ্চয় ও ঋণ রেজিস্টার (সমস্ত রেজিষস্টার) হাল নাগাদ করা হয়েছে?', FieldTypesEnum.Choice_Field.value, False, 'Yes\nNo\nNot applicable', 'হাঁ\nনা\nপ্রযোজ্য নয়', ReachoutLevelEnum.All.value, ''),
        ('001004002', 'Are there any inconsistency of CDCs registers and SCGs records?', 'সঞ্চয় ও ঋণ দল এবং সিডিসি’র রেকর্ডের মধ্যে কি কোন গড়-মিল রয়েছে?', FieldTypesEnum.Choice_Field.value, False, 'Yes\nNo\nNot available\nNot applicable', 'হাঁ\nনা\nনাই\nপ্রযোজ্য নয়', ReachoutLevelEnum.All.value, ''),
        ('001004003', 'In which areas are there inconsistencies?', 'কোন্ কোন্ ক্ষেত্রে গড়-মিল রয়েছে?', FieldTypesEnum.Choice_Field.value, False, 'Savings\nLoan\nSavings & loan\nNot applicable', 'সঞ্চয়\nঋণ\nসঞ্চয় ও ঋণ\nপ্রযোজ্য নয়', ReachoutLevelEnum.All.value, ''),
        ('001004004', 'If yes, mention value in BDT (Input)', 'যদি হ্যাঁ হয়, তাহলে পরিমান টাকায় উল্লেখ করুণ', FieldTypesEnum.Integer_Field.value, False, '', '', ReachoutLevelEnum.All.value, ''),
    ]

    cdc_report[('001001005', 'Savings')] = [
        ('001005001', 'Value of total Savings of all SCG\'s', 'সকল সঞ্চয় ও ঋণ দলের মোট সঞ্চয়ের পরিমান', FieldTypesEnum.Calculated_Field.value, True, '', '', ReachoutLevelEnum.All.value, '002001001'),
        ('001005002', 'Actual value of total Savings of CDC\'s', 'সিডিসি’র প্রকৃত মোট সঞ্চয়ের পরিমান', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001005003', 'Value of total Savings withdrawn by all SCG', 'সকল সঞ্চয় ও ঋণ দল কর্তৃক উত্তোলনকৃত মোট সঞ্চয়ের পরিমান', FieldTypesEnum.Calculated_Field.value, True, '', '', ReachoutLevelEnum.All.value, '002001002'),
        ('001005004', 'Actual value of total Savings withdrawn by CDC', 'সিডিসি কর্তৃক উত্তোলনকৃত প্রকৃত মোট সঞ্চয়ের পরিমান', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('001005005', 'Difference', '', FieldTypesEnum.Calculated_Field.value, True, '', '', ReachoutLevelEnum.MissionControl.value, '(@001005003@+@001005004@)'),
    ]

    group_weight = 1
    field_weight = 1
    for group, field_list in cdc_report.items():
        group_assigned_code, group_name = group
        field_group, created = FieldGroup.objects.get_or_create(
            organization=organization, assigned_code=group_assigned_code
        )
        field_group.weight = group_weight
        field_group.name = group_name
        field_group.name_bd = cdc_group_translation_dict.get(group, '')
        field_group.save()
        group_weight += 1
        print('> ' + group_name)

        for q_code, field_name, field_name_bd, field_type, is_required, options, options_bd, reachout, formula in field_list:
            custom_field = CDCMonthlyReportField.objects.filter(assigned_code=q_code).first()
            if custom_field is None:
                custom_field = CDCMonthlyReportField(assigned_code=q_code)
            custom_field.name = field_name
            custom_field.field_group = field_group
            custom_field.name_bd = field_name_bd
            custom_field.field_type = field_type
            custom_field.is_required = is_required
            custom_field.list_values = options
            custom_field.list_values_bd = options_bd
            custom_field.reachout_level = reachout
            custom_field.weight = field_weight
            custom_field.formula = formula
            custom_field.save()
            field_weight += 1

            print('>> ' + field_name)


def initialize_scg_monthly_report_form(*args, **kwargs):
    organization = Organization.objects.first()
    scg_report = OrderedDict()
    scg_report[('001002001', 'Savings')] = OrderedDict()
    scg_report[('001002002', 'Loans')] = OrderedDict()
    scg_report[('001002003', 'Records')] = OrderedDict()
    scg_group_translation_dict = OrderedDict()

    scg_group_translation_dict[('001002001', 'Savings')] = 'সঞ্চয়'
    scg_group_translation_dict[('001002002', 'Loans')] = 'ঋণ'
    scg_group_translation_dict[('001002003', 'Records')] = 'নথিপত্র'
    # Note: Don't change the code of 002002009 as this field will show first time of a report in mobile. So, this field will
    # be carry forwarded to other monthly report. This was rendered hard coded in details view and export files.
    # For adding a new field maintain the required order here
    scg_report[('001002001', 'Savings')] = [
        ('002001001', 'Value of savings deposited ', 'মোট সঞ্চয়ের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002001002', 'Value of savings withdrawn', 'মোট সঞ্চয় উত্তোলনের পরিমাণ', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
    ]

    scg_report[('001002002', 'Loans')] = [
        ('002002001', 'Number of loans received', 'মোট কতটি ঋণ গ্রহণ করা হয়েছে', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002002002', 'Value of total loan received (Principal)', 'মোট ঋণের পরিমাণ (আসল)', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002002003', 'Value of total loan received (Interest)', 'মোট ঋণের পরিমাণ (সূদ)', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002002009', 'Total value of loans collected since the beginning to reporting month-Cumulative amount (Pricipal+Interest)', 'শুরু থেকে রিপোর্টিং মাস পর্যন্ত পরিশোধিত মোট ঋণের পরিমাণ ( আসল+সুদ)',
         FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002002004', 'Total targeted receivable current loan (Principal + Interest) for the reporting month', 'চলতি মাসে মোট আদায়যোগ্য ঋণের পরিমান (আসল+সূদ)', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002002005', 'Total collected current loan (Principal + Interest) for the reporting month', 'চলতি মাসে মোট আদায়কৃত ঋণের পরিমান (আসল+সূদ)', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        # ('002002006', 'Value of total loan collected (Principal) of Outstanding + Overdue + Advances', 'আদায়কৃত   মোট ঋণের পরিমান (আসল) -বকেয়া+ মেয়াদোত্তীর্ন+ অগ্রিম', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002002007', 'Value of total loan collected (Principal+ Interest) of Overdue + Advances', 'পরিশোধিত মোট ঋণের পরিমান- আসল+ সূদ সহ (মেয়াদোত্তীর্ন+অগ্রিম)', FieldTypesEnum.Integer_Field.value, True, '', '', ReachoutLevelEnum.All.value, ''),
        ('002002010', 'Value of outstanding loans',
         'অবশিষ্ট মোট বকেয়া ঋণের পরিমাণ (আসল +সুদ) (Outstanding)', FieldTypesEnum.Integer_Field.value, True, '',
         '', ReachoutLevelEnum.MissionControl.value, '@002002002@+@002002003@+@002002007@-@002002009@'),
        ('002002008', 'Outstanding amount in the current Outstanding loan (Principal)',
         'চলতি ঋণের মধ্যে বকেয়া আছে এমন ঋণের Outstanding পরিমান (আসল)', FieldTypesEnum.Integer_Field.value, True, '',
         '', ReachoutLevelEnum.All.value, ''),
        ('002002011', '% of Risky loan amount (PAR)',
         'ঝুকিপূর্ন ঋণের পরিমাণ (শতকরা হার) PAR', FieldTypesEnum.Decimal_Field.value, True, '',
         '', ReachoutLevelEnum.MissionControl.value, '@002002008@/@002002010@*100'),
    ]

    scg_report[('001002003', 'Records')] = [
        ('002003001', 'Personal passbook updated?', 'ব্যক্তিগত পাস বহি কি হালনাগাদকৃত?', FieldTypesEnum.Choice_Field.value, False, 'Yes\nNo\nNot applicable', 'হাঁ\nনা\nপ্রযোজ্য নয়', ReachoutLevelEnum.All.value, ''),
        ('002003002', 'Are there any inconsistencies between passbook and SCG record?', 'পাস বহি ও দলের রেকর্ডের মধ্যে কি কোন গড়-মিল রয়েছে?', FieldTypesEnum.Choice_Field.value, False, 'Yes\nNo\nNot available\nNot applicable', 'হাঁ\nনা\nনাই\nপ্রযোজ্য নয়', ReachoutLevelEnum.All.value, ''),
        ('002003003', 'In which areas are there inconsistencies?', 'কোন্ কোন্ ক্ষেত্রে গড়-মিল রয়েছে?', FieldTypesEnum.Choice_Field.value, False, 'Savings\nLoan\nSavings & loan\nNot applicable', 'সঞ্চয়\nঋণ\nসঞ্চয় ও ঋণ\nপ্রযোজ্য নয়', ReachoutLevelEnum.All.value, ''),
        ('002003004', 'If yes, mention value in BDT (Input)', 'যদি হ্যাঁ হয়, তাহলে পরিমান টাকায় উল্লেখ করুণ', FieldTypesEnum.Integer_Field.value, False, '', '', ReachoutLevelEnum.All.value, ''),
    ]

    group_weight = 1
    field_weight = 1
    for group, field_list in scg_report.items():
        group_assigned_code, group_name = group
        field_group, created = FieldGroup.objects.get_or_create(
            organization=organization, assigned_code=group_assigned_code
        )
        field_group.name = group_name
        field_group.weight = group_weight
        field_group.name_bd = scg_group_translation_dict.get(group, '')
        field_group.save()
        group_weight += 1
        print('> ' + group_name)

        for q_code, field_name, field_name_bd, field_type, is_required, options, options_bd, reachout, formula in field_list:
            custom_field = SCGMonthlyReportField.objects.filter(assigned_code=q_code).first()
            if custom_field is None:
                custom_field = SCGMonthlyReportField(assigned_code=q_code)
            custom_field.name = field_name
            custom_field.field_group = field_group
            custom_field.name_bd = field_name_bd
            custom_field.field_type = field_type
            custom_field.is_required = is_required
            custom_field.list_values = options
            custom_field.list_values_bd = options_bd
            custom_field.reachout_level = reachout
            custom_field.weight = field_weight
            custom_field.formula = formula
            custom_field.save()
            field_weight += 1

            print('>> ' + field_name)


def initialize_cumulative_report_form(*args, **kwargs):
    organization = Organization.objects.first()
    cumulative_report = OrderedDict()
    cumulative_report[('001003001', 'Savings')] = OrderedDict()
    cumulative_report[('001003002', 'Loans')] = OrderedDict()
    cumulative_report[('001003003', 'Service Charges & Fees')] = OrderedDict()
    cumulative_report[('001003004', 'Fund Status')] = OrderedDict()
    cumulative_group_translation_dict = OrderedDict()

    cumulative_report[('001003001', 'Savings')] = [
        ('003001001', 'Total value of Savings deposited', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@002001001@'),
        ('003001002', 'Total value of Savings withdrawal', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@002001002@'),
        ('003001003', 'Savings balance at the end of the reporting month', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, '@003001001@-@003001002@'),
    ]

    cumulative_report[('001003002', 'Loans')] = [
        ('003002001', 'Total number of loan disbursed', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@002002001@'),
        ('003002002', 'Total value of loan disbursed (Principal)', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@002002002@'),
        ('003002003', 'Total value of loan disbursed (Interest)', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@002002003@'),
        ('003002004', 'Total targeted receiveable current loan for reporting month', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001001001@'),
        ('003002005', 'Total received (Collected) current loan for reporting month', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001001002@'),
        ('003002006', 'Total value of loans repaid/ collected (Cumulative) as of today', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001001003@'), # need further clarification
        ('003002007', 'Value of outstanding loans as of today', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'LATEST:@001001004@'),
        ('003002008', 'Value of overdue loans as of today', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'LATEST:@001001005@'),
    ]

    cumulative_report[('001003003', 'Service Charges & Fees')] = [
        ('003003001', 'Total value of service charges', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001002001@'),
        ('003003002', 'Total value of admission fees (passbook and others) collected as of date of assessment/ reporting (Cumulative)', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001002002@'),
        ('003003003', 'Total bank interest earn', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001002003@'),
        ('003003004', 'Total Bank charges for the reporting period', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001002004@'),
        ('003003005', 'Total other expenditure e.g. logistics, photocopy etc. for the reporting period', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'SUM:@001002005@'),
        ('003003006', 'Interest expense on member\'s savings for the reporting period', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'LATEST:@001002006@'),
        ('003003007', 'Interest payable on member\'s savings balance at the end of the reporting period', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'LATEST:@001002007@'),
    ]

    cumulative_report[('001003004', 'Fund Status')] = [
        ('003004001', 'Bank Balance at the end of reporting month', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'LATEST:@001003001@'),
        ('003004002', 'Cash in hand at the end of reporting month', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, 'LATEST:@001003002@'),
        ('003004003', 'Total fund', '', FieldTypesEnum.Calculated_Field.value, False, '', '', ReachoutLevelEnum.All.value, '(@003002007@+@003003001@+@003003002@+@003003003@+@003004001@+@003004002@)-(@003001003@+@003003004@+@003003005@+@003003006@+@003003007@)'),
    ]

    group_weight = 1
    field_weight = 1
    for group, field_list in cumulative_report.items():
        group_assigned_code, group_name = group
        field_group, created = FieldGroup.objects.get_or_create(
            organization=organization, assigned_code=group_assigned_code
        )
        field_group.weight = group_weight
        field_group.name = group_name
        field_group.name_bd = cumulative_group_translation_dict.get(group_name, '')
        field_group.save()
        group_weight += 1
        print('> ' + group_name)

        for q_code, field_name, field_name_bd, field_type, is_required, options, options_bd, reachout, formula in field_list:
            custom_field = CumulativeReportField.objects.filter(assigned_code=q_code).first()
            if custom_field is None:
                custom_field = CumulativeReportField(assigned_code=q_code)
            custom_field.name = field_name
            custom_field.field_group = field_group
            custom_field.name_bd = field_name_bd
            custom_field.field_type = field_type
            custom_field.is_required = is_required
            custom_field.list_values = options
            custom_field.list_values_bd = options_bd
            custom_field.reachout_level = reachout
            custom_field.weight = field_weight
            custom_field.formula = formula
            custom_field.save()
            field_weight += 1

            print('>> ' + field_name)


def initialize(*args, **kwargs):
    actions = [
        initialize_cdc_monthly_report_form,
        initialize_scg_monthly_report_form,
        initialize_cumulative_report_form
    ]

    i = 1
    for a in actions:
        a(*args, **kwargs)
        i += 1
    print('-------successfully completed-------')
