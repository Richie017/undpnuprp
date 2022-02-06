from enum import Enum


class CRMIFIndicatorEnum(Enum):
    CommunityContractIndicator = 'community_contract'
    InterventionTypeIndicator = 'intervention_type'
    ExpenditureIndicator = 'expenditure'
    GenderByIntervention = 'gender_by_intervention'
    BeneficiaryByIntervention = 'beneficiary_by_intervention'
    OnTimeCompletedIntervention = 'on_time_completed_intervention'
    OnBudgetCompletedIntervention = 'on_budget_completed_intervention'
    EmployedPeopleByIntervention = 'employed_people_by_intervention'
    TotalPeopleByIntervention = 'total_people_by_intervention'
    InterventionsLessThanHalf = 'interventions_less_than_half'
    InterventionsMoreThanHalf = 'interventions_more_than_half'
