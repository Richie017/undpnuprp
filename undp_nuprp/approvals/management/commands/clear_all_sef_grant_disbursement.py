from django.core.management import BaseCommand

from undp_nuprp.approvals.models.sef_grant_disbursement.sef_apprenticeship_grant_disbursement import \
    SEFApprenticeshipGrantDisbursement
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_business_grant_disbursement import \
    SEFBusinessGrantDisbursement
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_education_child_marriage_grantee import \
    SEFEducationChildMarriageGrantDisbursement
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_education_dropout_grant_disbursement import \
    SEFEducationDropoutGrantDisbursement
from undp_nuprp.approvals.models.sef_grant_disbursement.sef_nutrition_grant_disbursement import \
    SEFNutritionGrantDisbursement

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        sef_grant_disbursement = [SEFBusinessGrantDisbursement, SEFApprenticeshipGrantDisbursement,
                                  SEFEducationChildMarriageGrantDisbursement,
                                  SEFEducationDropoutGrantDisbursement, SEFNutritionGrantDisbursement]

        print('Grant disbursement name: Operation ID')

        for index, sef_grant_dis in enumerate(sef_grant_disbursement):
            grant_dis_name = sef_grant_dis.get_model_meta('route', 'display_name')
            print('{0}: {1}'.format(grant_dis_name, index + 1))

        print('All grant disbursements: 6')

        op_id = int(input('Enter operation ID:'))

        if op_id == 6:
            for sef_grant_dis in sef_grant_disbursement:
                grantee_name = sef_grant_dis.get_model_meta('route', 'display_name')
                print("Total {} {} has deleted.".format(sef_grant_dis.objects.count(), grantee_name))
                sef_grant_dis.objects.all().delete()
        else:
            sef_grant_dis = sef_grant_disbursement[op_id - 1]
            grantee_name = sef_grant_dis.get_model_meta('route', 'display_name')
            print("Total {} {} has deleted.".format(sef_grant_dis.objects.count(), grantee_name))
            sef_grant_dis.objects.all().delete()
