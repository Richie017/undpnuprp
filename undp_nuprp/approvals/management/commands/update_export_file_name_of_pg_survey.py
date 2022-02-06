from django.core.management import BaseCommand

from blackwidow.core.models import ExportFileObject

excludable_file_patterns = [
    "AllGeography",
    "ApprovedCDCMonthlyReport", "ApprovedSCGMonthlyReport",
    "CDC", "CommunityMobilizationReporting", "CommunityOrganizer",
    "CRMIF", "DynamicSurveyResponse", "eligibleapprenticeshipgrantee",
    "eligiblebusinessgrantee", "eligibleeducationdropoutgrantee",
    "eligibleeducationearlymarriagegrantee", "Enumerator",
    "MonthlyProgress", "MonthlyTarget", "PG_MemberSurveyResponses",
    "PMFReport", "PrimaryGroup", "Role", "SavingsAndCreditGroup",
    "SEFApprenticeshipGrantee", "SEFBusinessGrantee", "SEFEducationChildMarriageGrantee",
    "SEFEducationDropoutGrantee", "SIF", "SR", "Survey_Stats", "TownManager", "Training",
    "Workshop"
]

__author__ = "Ziaul Haque"


class Command(BaseCommand):
    def handle(self, *args, **options):
        excludable_ids = []
        for file_pattern in excludable_file_patterns:
            excludable_ids += list(ExportFileObject.objects.filter(
                name__startswith=file_pattern).values_list('pk', flat=True))

        queryset = ExportFileObject.objects.exclude(pk__in=excludable_ids)

        updatable_entries = list()
        for q in queryset:
            q.name = 'deleted_' + str(q.name)
            updatable_entries.append(q)

        if len(updatable_entries) > 0:
            print("updating {0} entries".format(len(updatable_entries)))
            ExportFileObject.objects.bulk_update(updatable_entries)
            print("updated...")
