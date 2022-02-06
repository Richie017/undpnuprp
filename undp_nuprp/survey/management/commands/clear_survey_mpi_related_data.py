from django.core.management.base import BaseCommand

from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationDropOutGrantee, EligibleEducationEarlyMarriageGrantee, GranteeGeneratedFile
from undp_nuprp.survey.models import *

__author__ = 'Ziaul Haque'


class Command(BaseCommand):

    def handle(self, *args, **options):
        pg_mpi_indicators = PGMPIIndicator.objects.all()
        pg_poverty_indexes = PGPovertyIndex.objects.all()
        business_grantees = EligibleBusinessGrantee.objects.all()
        apprenticeship_grantees = EligibleApprenticeshipGrantee.objects.all()
        education_dropout_grantees = EligibleEducationDropOutGrantee.objects.all()
        education_early_marriage_grantees = EligibleEducationEarlyMarriageGrantee.objects.all()

        print("Total %d PG MPI Indicators deleted." % pg_mpi_indicators.count())
        pg_mpi_indicators.delete()

        print("Total %d PG Poverty Indexes deleted." % pg_poverty_indexes.count())
        pg_poverty_indexes.delete()

        print("Total %d Business Grantees deleted." % business_grantees.count())
        business_grantees.delete()

        print("Total %d Apprenticeship Grantees deleted." % apprenticeship_grantees.count())
        apprenticeship_grantees.delete()

        print("Total %d EducationDropOut Grantees deleted." % education_dropout_grantees.count())
        education_dropout_grantees.delete()

        print("Total %d EducationEarlyMarriage Grantees deleted." % education_early_marriage_grantees.count())
        education_early_marriage_grantees.delete()

        grantee_generated_files = GranteeGeneratedFile.objects.all()

        print("Total %d Grantee Generated File deleted." % grantee_generated_files.count())
        grantee_generated_files.delete()
