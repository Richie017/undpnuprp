from django.core.management import BaseCommand
from django.db.models import Q

from undp_nuprp.approvals.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        classes = [
            (SEFBusinessGrantDisbursement, SEFBusinessGrantee),
            (SEFApprenticeshipGrantDisbursement, SEFApprenticeshipGrantee),
            (SEFEducationDropoutGrantDisbursement, SEFEducationDropoutGrantee),
            (SEFEducationChildMarriageGrantDisbursement, SEFEducationChildMarriageGrantee),
            (SEFNutritionGrantDisbursement, SEFNutritionGrantee),
        ]
        results = []

        for class_pair in classes:
            _total, _processed, _error = self.handle_grant_disbursement(class_pair[0], class_pair[1])
            results.append((_total, _processed, _error))

        print("\n\nTask completed.")
        for i in range(len(classes)):
            print("{}: total: {}, processed: {}, error: {}".format(
                classes[i][0].__name__, results[i][0], results[i][1], results[i][2]))

    def handle_grant_disbursement(self, DisbursementClass, GranteeClass):
        filter_options = Q(**{
            '{}__isnull'.format(GranteeClass.__name__.lower()): True
        })
        disbursements_with_missing_grantee = DisbursementClass.objects.filter(filter_options)

        to_be_processed = disbursements_with_missing_grantee.count()
        processed = 0
        error = 0

        for disbursement in disbursements_with_missing_grantee:
            candidate_grantee = GranteeClass.objects.filter(
                pg_member_name=disbursement.pg_member_name,
                pg_member_assigned_code=disbursement.pg_member_assigned_code
            ).last()

            if not candidate_grantee:
                print("No matching grantee found for {} ({})".format(
                    disbursement.pg_member_name, disbursement.pg_member_assigned_code))
                error += 1
            else:
                candidate_grantee.sef_grant_disbursement = disbursement
                candidate_grantee.save()
                processed += 1
            print("Processed: {}/{} (error: {})".format(processed, to_be_processed, error))
        return to_be_processed, processed, error

