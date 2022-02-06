from django.core.management import BaseCommand
from django.db import transaction
from django.db.models.query_utils import Q

from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_apprenticeship_grantee import \
    EligibleApprenticeshipGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_business_grantee import EligibleBusinessGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_drop_out_grantee import \
    EligibleEducationDropOutGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_early_marriage_grantee import \
    EligibleEducationEarlyMarriageGrantee

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():

            grantees_cls = [EligibleBusinessGrantee, EligibleApprenticeshipGrantee, EligibleEducationDropOutGrantee,
                           EligibleEducationEarlyMarriageGrantee]

            for cls in grantees_cls:
                queryset = cls.objects.filter(Q(grantee_name__endswith=' ') | Q(grantee_name__startswith=' '))
                print('Total {0} {1}\'s have name contains leading and trailing spaces'.format(queryset.count(),
                                                                                            cls.__name__))

                _updated_grantee_list = []

                for _grantee in queryset.all():
                    _grantee.grantee_name = _grantee.grantee_name.strip()
                    _updated_grantee_list.append(_grantee)

                if len(_updated_grantee_list) > 0:
                    cls.objects.bulk_update(_updated_grantee_list, batch_size=500)
                    print('Successfully removed spaces')
                else:
                    print('Nothing to update')
