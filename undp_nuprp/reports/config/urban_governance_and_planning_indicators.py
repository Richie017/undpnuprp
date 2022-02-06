from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum
from undp_nuprp.reports.utils.enums.urban_governance_and_planning_indicator import \
    UrbanGovernanceAndPlanningIndicatorEnum

urban_governance_and_planning_indicators = [
    {
        'name': 'Ward Committee',
        'full_name': 'Ward Committee',
        'indicator': UrbanGovernanceAndPlanningIndicatorEnum.WardCommittee.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Ward Committee (city-wise)</b>')
            }
        ]
    },
    {
        'name': 'Institutional Financial Capacity',
        'full_name': 'Institutional Financial Capacity',
        'indicator': UrbanGovernanceAndPlanningIndicatorEnum.InstitutionalFinancialCapability.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Institutional Financial Capacity (city-wise)</b>')
            }
        ]
    },
    {
        'name': 'Standing Committee',
        'full_name': 'Standing Committee',
        'indicator': UrbanGovernanceAndPlanningIndicatorEnum.StandingCommittee.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Standing Committee (city-wise)</b>')
            }
        ]
    }
]
