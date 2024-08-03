from django.core.management import BaseCommand

from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_apprenticeship_grantee import \
    SEFApprenticeshipGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_business_grantee import SEFBusinessGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_dropout_grantee import \
    SEFEducationDropoutGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_education_early_marriage_grantee import \
    SEFEducationChildMarriageGrantee
from undp_nuprp.approvals.models.socio_economic_funds.sef_grantees.sef_nutrition_grantee import SEFNutritionGrantee

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        sef_grantees = [SEFBusinessGrantee, SEFApprenticeshipGrantee, SEFEducationChildMarriageGrantee,
                        SEFEducationDropoutGrantee, SEFNutritionGrantee]

        print('Grantee Name: Operation ID')

        for index, sef_grant in enumerate(sef_grantees):
            grantee_name = sef_grant.get_model_meta('route', 'display_name')
            print('{0}: {1}'.format(grantee_name, index + 1))

        print('All grantees: 6')

        op_id = int(input('Enter operation ID:'))

        if op_id == 6:
            for sef_grant in sef_grantees:
                grantee_name = sef_grant.get_model_meta('route', 'display_name')
                print("Total {} {} has deleted.".format(sef_grant.objects.count(), grantee_name))
                sef_grant.objects.all().delete()
        else:
            sef_grant = sef_grantees[op_id-1]
            grantee_name = sef_grant.get_model_meta('route', 'display_name')
            print("Total {} {} has deleted.".format(sef_grant.objects.count(), grantee_name))
            sef_grant.objects.all().delete()