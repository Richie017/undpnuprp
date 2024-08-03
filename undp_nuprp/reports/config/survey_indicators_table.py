from undp_nuprp.reports.utils.enums.household_survey_indicator import HouseholdSurveyIndicatorEnum

__author__ = 'Ashraful'


TABLE_HEADERS = dict()
TABLE_HEADERS[HouseholdSurveyIndicatorEnum.GenderIndicator.value] = ('City Name', 'Female', 'Hijra', "Male")


def get_table_headers(val=None):
    global TABLE_HEADERS
    return TABLE_HEADERS[val]
