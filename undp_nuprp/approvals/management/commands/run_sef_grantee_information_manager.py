from django.core.management import BaseCommand

from undp_nuprp.approvals.managers.sef_grantee_information_manager import SEFGranteeInformationManager


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('---Starting Execution---')
        SEFGranteeInformationManager.sync_sef_business_grantee_info_from_eligible_business_grantee()
        SEFGranteeInformationManager.sync_sef_apprenticeship_grantee_info_from_eligible_apprenticeship_grantee()
        SEFGranteeInformationManager.sync_sef_dropout_grantee_info_from_eligible_dropout_grantee()
        SEFGranteeInformationManager.sync_sef_dropout_grantee_info_from_eligible_dropout_grantee()
        print('---Ending Execution---')
