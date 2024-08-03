from datetime import datetime, timedelta

from undp_nuprp.approvals.models import GranteeGeneratedFile
from undp_nuprp.approvals.models.grantees.short_listed_eligible_grantees.short_listed_eligible_apprenticeship_grantee import \
    ShortListedEligibleApprenticeshipGrantee
from undp_nuprp.approvals.models.grantees.short_listed_eligible_grantees.short_listed_eligible_business_grantee import \
    ShortListedEligibleBusinessGrantee
from undp_nuprp.approvals.models.grantees.short_listed_eligible_grantees.shortlisted_eligible_education_drop_out_grantee import \
    ShortListedEligibleEducationDropOutGrantee
from undp_nuprp.approvals.models.grantees.short_listed_eligible_grantees.shortlisted_eligible_education_early_marriage_grantee import \
    ShortListedEligibleEducationEarlyMarriageGrantee

__author__ = 'Shuvro'


class ShortListedEligibleGranteeManager(object):
    @classmethod
    def generate_files(cls, last_run_time=None, handle_upto_time=None):
        if not last_run_time:
            last_run_time = datetime(datetime.now().year - 1, 1, 1)
        if not handle_upto_time:
            handle_upto_time = datetime.now()

        print("Generating business grants file")
        # generating csv export file for ShortListedEligibleBusinessGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=ShortListedEligibleBusinessGrantee.get_export_file_name(),
            model=ShortListedEligibleBusinessGrantee, last_run_time=last_run_time, handle_upto_time=handle_upto_time
        )

        print("Generating apprenticeship grants file")
        # generating csv export file for ShortListedEligibleApprenticeshipGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=ShortListedEligibleApprenticeshipGrantee.get_export_file_name(),
            model=ShortListedEligibleApprenticeshipGrantee, last_run_time=last_run_time, handle_upto_time=handle_upto_time
        )

        print("Generating education drop out grants file")
        # generating csv export file for ShortListedEligibleEducationDropOutGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=ShortListedEligibleEducationDropOutGrantee.get_export_file_name(),
            model=ShortListedEligibleEducationDropOutGrantee, last_run_time=last_run_time,
            handle_upto_time=handle_upto_time
        )

        print("Generating education early marriage grants file")
        # generating csv export file for ShortListedEligibleEducationEarlyMarriageGrantee list
        GranteeGeneratedFile.generate_complete_export_file(
            name=ShortListedEligibleEducationEarlyMarriageGrantee.get_export_file_name(),
            model=ShortListedEligibleEducationEarlyMarriageGrantee, last_run_time=last_run_time,
            handle_upto_time=handle_upto_time
        )

    @classmethod
    def generate_todays_files(cls):
        _cur_datetime = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        _cur_year = _cur_datetime.year
        start_time = _cur_datetime.timestamp() * 1000
        end_time = (_cur_datetime + timedelta(days=1)).timestamp() * 1000 - 1000
        cls.generate_files(last_run_time=start_time, handle_upto_time=end_time)
