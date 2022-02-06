"""
Created by tareq on 2/19/18
"""

__author__ = 'Tareq'


def get_education_attainment_indicators():
    from undp_nuprp.survey.models.entity.answer import Answer
    return list(
        Answer.objects.filter(question__question_code=HH_EDUCATION_ATTAINMENT_QUESTION_CODE, question__is_active=True,
                              question__is_deleted=False).order_by(
            'order').values_list('text', flat=True))


def get_hh_resource_list():
    from undp_nuprp.survey.models.entity.answer import Answer
    return list(
        Answer.objects.filter(question__question_code=HH_RESOURCE_QUESTION_CODE, question__is_active=True,
                              question__is_deleted=False).order_by('order').values_list('text', flat=True))


PG_MEMBER_SURVEY_NAME = 'PG Member Survey Questionnaire'
NID_AVAILABILITY_QUESTION_TEXT = 'Do you have NID/ Smart Card/ Birth registration number?'
NID_QUESTION_TEXT = 'What is your NID/ Smart Card/Birth registration number?'
NAME_QUESTION_CODE = '1.1'
NID_AVAILABILITY_QUESTION = '1.2'
NID_ANSWER_CODE = '1.2.1'
NID_QUESTION = '1.2.1'
PHONE_QUESTION = '1.3'
GENDER_QUESTION_CODE = '1.4'
AGE_QUESTION_CODE = '1.5'
PG_MEMBER_AGE_LOWER_LIMIT = 20
PG_MEMBER_AGE_UPPER_LIMIT = 59
PG_MEMBER_AGE_GROUP_STEP = 10

RELIGION_QUESTION_CODE = '2.2'

ETHNICITY_QUESTION_CODE = '2.3'
ETHNIC_MAJORITY_ANSWER = 'Bengali'

MARITAL_STATUS_QUESTION_CODE = '2.11'
EDUCATION_QUESTION_CODE = '2.4'
HH_EDUCATION_ATTAINMENT_QUESTION_CODE = '2.5'
EMPLOYMENT_QUESTION_CODE = '2.6'
FORMAL_STUDENT_QUESTION_CODE = '2.9'
TRAINING_QUESTION_CODE = '2.8'
HH_QUESTION_CODE = '4.1'
DISABLITY_QUESTION_CODE = ['3.1', '3.2', '3.3', '3.4', '3.5', '3.6']
DISABLED_ANSWER_TEXT = ['Cannot do at all', 'A lot of difficulty']
PG_DISABILITY_LABEL_DICT = {
    '3.1': 'Difficulty in Seeing', '3.2': 'Difficulty in Hearing', '3.3': 'Difficulty in Walking',
    '3.4': 'Difficulty in Remebering', '3.5': 'Difficulty in Self Care', '3.6': 'Difficulty in Communicating'
}

PG_DISABILITY_LABEL_LIST = ['Difficulty in Seeing', 'Difficulty in Hearing', 'Difficulty in Walking',
                            'Difficulty in Remebering', 'Difficulty in Self Care', 'Difficulty in Communicating']

PG_MEMBER_AGE_RANGE_LIST = ['Below 20', '20-29', '30-39', '40-49', '50-59', '60 and above']
PG_MEMBER_RELIGION_LIST = ['Muslim', 'Hindu', 'Buddhist', 'Christian', 'Other']
PG_MEMBER_ETHNICITY_LIST = ['Bengali', 'Indigenous CHT', 'Bihari', 'Rohyngia', 'Dalit', 'Horizon', 'Other']
PG_MEMBER_MARITAL_STATUS_LIST = ['Unmarried', 'Married', 'Divorced', 'Widow/ Widower', 'Seperated', 'Abandoned']
PG_MEMBER_GENDER_LIST = ['Female', 'Male', 'Hijra']
PG_MEMBER_EDUCATION_ATTAINMENT_LIST = ['Pre-primary/ Moktab', 'Primary/ Ibtadayee/ JDC', 'SSC / Dakhil', 'HSC/ Alim',
                                       'University/ Fazil / Kamil', 'Never attended school', 'Do not know']
EMPLOYMENT_STATUS_LIST = ['Day labour', 'Housewife', 'Small Businessman', 'Domestic worker', 'Construction worker',
                          'Hotel/Tea Shop/furniture /grocery worker', 'Hawker/Vendor', 'Transport worker',
                          'Rickshaw/van/push cart/other puller',
                          'Skilled Worker (plumber, electrician, garments & sweater factory, mills, mechanics and so on)',
                          'Service (govt, semi govt and autonomous)', 'Service (NGO/Private)', 'Beggar', 'Unemployed',
                          'Handloom/handicrafts', 'Not Applicable', 'Other']

HH_NAME_QUESTION_CODE = '4.2.1'
HH_GENDER_QUESTION_CODE = '4.2.4'
HH_EMPLOYMENT_QUESTION_CODE = '4.2.8'
HH_EDUCATION_QUESTION_CODE = '4.2.7'
HH_DISABLITY_QUESTION_CODE = ['4.3.1', '4.3.2', '4.3.3', '4.3.4', '4.3.5', '4.3.6']
HH_DISABLED_ANSWER_TEXT = ['Cannot do at all', 'A lot of difficulty']
HH_DISABILITY_LABEL_DICT = {
    '4.3.1': 'Difficulty in Seeing', '4.3.2': 'Difficulty in Hearing', '4.3.3': 'Difficulty in Walking',
    '4.3.4': 'Difficulty in Remebering', '4.3.5': 'Difficulty in Self Care', '4.3.6': 'Difficulty in Communicating'
}

HM_COUNT_QUESTION_CODE = '4.4.1'
HM_COUNT_MALE_QUESTION_CODE = '4.4.2'
HM_COUNT_FEMALE_QUESTION_CODE = '4.4.3'
HM_PREGNANCY_COUNT_QUESTION_CODE = '4.4.5.1'
HM_LACTATING_MOTHER_QUESTION_CODE = '4.4.6'
HM_LACTATING_MOTHER_COUNT_QUESTION_CODE = '4.4.6.1'
HM_CHILDREN_QUESTION_CODE = '4.4.7'
HM_CHILDREN_COUNT_QUESTION_CODE = '4.4.7.1'
HM_ADOLESCENT_GIRL_QUESTION_CODE = '4.4.8'
HM_GIRLS_10_to_18_COUNT_QUESTION_CODE = '4.4.8.1'
DISABILITY_COUNT_QUESTION_CODE = '4.4.9.1'

EDUCATION_ATAINMENT_QUESTION_CODE = '5.1'
ANY_MEMBER_SCHOOL_ATTENDANCE_QUESTION_CODE = '5.1.1'
SCHOOL_ATTENDENCE_QUESTION_CODE = '5.1.1.1'
CHILD_BIRTH_QUESTION_CODE = '5.9'
ANY_DISABLED_MEMBER_QUESTION_CODE = '4.4.9'
HH_RESOURCE_QUESTION_CODE = '5.8'
HIGH_VALUE_RESOURCES = [
    'Radio', 'Functional refrigerator', 'Smart/ Led TV', 'Land phone',
    'Smart mobile phone', 'Bicycle', 'Motorbike/Scooter'
]
CAR_TRUCK_RESOURCE = ['Car', 'Truck']
SANITATION_QUALITY_QUESTION_CODE = '5.4'
SANITATION_SHARED_QUESTION_CODE = '5.4.1'
POOR_SANITATION_ANSWERS = [
    'Pit latrine without slab / open pit', 'Bucket', 'Hanging toilet/hanging latrine', 'No facilities or bush or field',
    'Other'
]

WATER_SOURCE_QUESTION_CODE = '5.6'
WATER_COLLECTION_TIME_QUESTION_CODE = '5.6.1'

FLOOR_TYPE_QUESTION_CODE = '5.2'
FUEL_TYPE_QUESTION_CODE = '5.5'
POOR_FUEL_ANSWERS = ['Wood', 'Charcoal', 'Animal dung', 'Other']

GRANT_FROM_ANY_ORGANIZATION_QUESTION_CODE = '2.7'
GRANT_FROM_NUPRP_QUESTION_CODE = '2.10'
GRANT_RECEIVED_FROM_ANY_ORGANIZATION_QUESTION_CODE = '2.7.1'
GRANT_RECEIVED_FROM_NUPRP_QUESTION_CODE = '2.10.1'

FAMILY_MEMBER_NAME_QUESTION_CODE = '6.1'
FAMILY_MEMBER_AGE_QUESTION_CODE = '6.2'
FAMILY_MEMBER_GENDER_QUESTION_CODE = '6.3'
FAMILY_MEMBER_RELATION_QUESTION_CODE = '6.4'
FAMILY_MEMBER_FORMAL_STUDENT_QUESTION_CODE = '6.5'
FAMILY_MEMBER_UPPR_GRANT_QUESTION_CODE = '6.6'
FAMILY_MEMBER_UPPR_GRANT_TYPE_QUESTION_CODE = '6.7'
FAMILY_MEMBER_NUPRP_GRANT_QUESTION_CODE = '6.8'
FAMILY_MEMBER_NUPRP_GRANT_TYPE_QUESTION_CODE = '6.9'
FAMILY_MEMBER_TRAINING_QUESTION_CODE = '6.10'
FAMILY_MEMBER_DISABILITY_QUESTION_CODE = '6.11'

FAMILY_MEMBER_APPRENTICESHIP_ALLOWED_RELATIONS = ['Husband', 'Wife', 'Son', 'Daughter']
FAMILY_MEMBER_EDUCATION_ALLOWED_RELATIONS = ['Son', 'Daughter']
FAMILY_MEMBER_EDUCATION_ALLOWED_TO_REDUCE_EARLY_MARRIAGE_RELATIONS = ['Daughter']
HH_DEPRIVATION_INDICATORS = ['Education (Years of Schooling)', 'Education (Child School Attendance)',
                             'Health (Mortality)', 'Standard of Living (Electricity)',
                             'Standard of Living (Sanitation)', 'Standard of Living (Water)',
                             'Standard of Living (Floor)', 'Standard of Living (Cooking Fuel)',
                             'Standard of Living (Assets)', 'Disability']
HH_DEPRIVATION_INDICATORS_DESCRIPTIONS = ['No primary_group_member member has completed five years of schooling',
                                          'Any school-aged child is not attending school in years 5 to 18',
                                          'Any child has died in the family', 'The household has no electricity',
                                          'The household\'s sanitation facility is not improved (according to MDG guidelines), or it is improved but shared with other households. If the HH has the following sanitation facility then it is not improved: pit latrine without slab/ open pit, bucket, hanging toilet, no facilities or bush/ field',
                                          'The household does not have access to clean drinking water (according to MDG guidelines), or clean water is more than 30 minutes walking from home If they access water from: rainwater, tanker truck, cart with small tank/ drum, surface water, unprotected well, unprotected spring, then they do not have access to clean water',
                                          'The household has dirt, sand or dung floor',
                                          'The household cooks with dung, wood or charcoal',
                                          'The household does not own more than one of: radio, TV, telephone, bike, motorbike or refrigerator, and does not',
                                          'Household head is disabled']

HH_EDUCATION_ATTAINMENT_INDICATORS = get_education_attainment_indicators

PG_MPI_CATEGORIES = ['0-9.9', '10-19.9', '20-29.9', '30-39.9', '40-49.9', '50-59.9', '60-69.9', '70-79.9', '80-89.9',
                     '90-99.9']

MPI_HH_RESOURCE_LIST = get_hh_resource_list

MPI_SCORE_RELATED_QUESTION_CODES = [
    ANY_DISABLED_MEMBER_QUESTION_CODE, EDUCATION_ATAINMENT_QUESTION_CODE,
    ANY_MEMBER_SCHOOL_ATTENDANCE_QUESTION_CODE, SCHOOL_ATTENDENCE_QUESTION_CODE,
    FLOOR_TYPE_QUESTION_CODE, SANITATION_QUALITY_QUESTION_CODE,
    SANITATION_SHARED_QUESTION_CODE,
    FUEL_TYPE_QUESTION_CODE, WATER_SOURCE_QUESTION_CODE,
    WATER_COLLECTION_TIME_QUESTION_CODE, HH_RESOURCE_QUESTION_CODE,
    CHILD_BIRTH_QUESTION_CODE
]

MPI_SCORE_FOR_POOR = 20
MPI_SCORE_FOR_MP = 60
MPI_SCORE_FOR_EP = 90
WATER_FETCHING_TIME = 'More than 30 minutes'
FAMILY_MEMBER_LIMIT = 11

DIFFICULTY_IN_SEEING_QUESTION_CODE = '3.1'
DIFFICULTY_IN_HEARING_QUESTION_CODE = '3.2'
DIFFICULTY_IN_WALKING_QUESTION_CODE = '3.3'
DIFFICULTY_IN_REMEMBERING_QUESTION_CODE = '3.4'
DIFFICULTY_IN_SELF_CARE_QUESTION_CODE = '3.5'
DIFFICULTY_IN_COMMUNICATING_QUESTION_CODE = '3.6'

HH_DIFFICULTY_IN_SEEING_QUESTION_CODE = '4.3.1'
HH_DIFFICULTY_IN_HEARING_QUESTION_CODE = '4.3.2'
HH_DIFFICULTY_IN_WALKING_QUESTION_CODE = '4.3.3'
HH_DIFFICULTY_IN_REMEMBERING_QUESTION_CODE = '4.3.4'
HH_DIFFICULTY_IN_SELF_CARE_QUESTION_CODE = '4.3.5'
HH_DIFFICULTY_IN_COMMUNICATING_QUESTION_CODE = '4.3.6'
