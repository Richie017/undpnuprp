"""
    Created by tareq on 3/13/17
"""
from enum import Enum

__author__ = 'Tareq'


class HouseholdSurveyIndicatorEnum(Enum):
    GenderIndicator = 'gender'
    EmploymentIndicator = 'employment'
    EducationalIndicator = 'education'
    DependentMemberIndicator = 'dependent'
    HouseholdSizeIndicator = 'mean_size'
    HouseholdMPIIndicator = 'hh_mpi'
    DeprivedHouseholdIndicator = 'deprived'
    MPIvsCharacteristicIndicator = 'characteristic'

    DemoIndicator = 'demo'
