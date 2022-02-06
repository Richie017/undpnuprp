from django.utils.safestring import mark_safe

from undp_nuprp.reports.utils.enums.economic_development_and_planning_indicator import \
    EconomicDevelopmentAndLivelihoodEnum
from undp_nuprp.reports.utils.enums.graph_types import DataTableConfigEnum

economic_development_and_livelihood_indicators = [
    {
        'name': 'City-wise established SCC',
        'full_name': 'City-wise established SCC',
        'indicator': EconomicDevelopmentAndLivelihoodEnum.EstablishedSCC.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Established SCC (city-wise)</b>')
            }
        ]
    },
    {
        'name': 'Bi-annual meeting report city wise',
        'full_name': 'Bi-annual meeting report city wise',
        'indicator': EconomicDevelopmentAndLivelihoodEnum.BiAnnualMeeting.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Bi-annual meeting report (city-wise)</b>')
            }
        ]
    },
    {
        'name': 'Report on Initiatives have been taken by the SCC',
        'full_name': 'Report on Initiatives have been taken by the SCC',
        'indicator': EconomicDevelopmentAndLivelihoodEnum.InitiativesBySCC.value,
        'graph_types': [
            {
                'type': DataTableConfigEnum.DataTable.value,
                'title': mark_safe('<b>Report on Initiatives have been taken by the SCC (city-wise)</b>')
            }
        ]
    }
]
