from threading import Thread

from crequest.middleware import CrequestMiddleware

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.managers.log_cache_manager import LogCacheManager
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.scheduler.tasks import trigger_generate_eligible_grantee_list, \
    trigger_generate_eligible_grantee_file_generation
from blackwidow.scheduler.tasks import trigger_survey_export_lookup
from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
from undp_nuprp.approvals.managers.cumulative_report_manager import CumulativeReportManager
from undp_nuprp.approvals.managers.pending_report_approval_manager import PendingReportApprovalManager
from undp_nuprp.approvals.managers.pg_member_indicator_manager import PGMemberIndicatorManager
from undp_nuprp.approvals.managers.short_listed_eligible_grantee_manager import ShortListedEligibleGranteeManager
from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationGrantee, CDCMonthlyReport, PMFUploadedFileQueue
from undp_nuprp.approvals.models.savings_and_credits.cumulative_reports.cumulative_report import CumulativeReport
from undp_nuprp.nuprp_admin.models import SavingsAndCreditGroup
from undp_nuprp.nuprp_admin.models.developer.api_worker import APIWorker
from undp_nuprp.reports.managers.third_party.third_party_api_manager import ThirdPartyAPIManager
from undp_nuprp.reports.models import PGMemberInfoCache, KeyValueCount
from undp_nuprp.survey.models import PGMPIIndicator, PGPovertyIndex
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile
from undp_nuprp.survey.models.indicators.poverty_index_short_listed_grantee import PGPovertyIndexShortListedGrantee

__author__ = 'shamil'


@decorate(override_view(model=APIWorker, view=ViewActionEnum.Manage))
class APIWorkerView(GenericListView):
    def get_template_names(self):
        return ['developer/api_worker.html']

    def get(self, request, *args, **kwargs):
        return super(APIWorkerView, self).get(request, *args, **kwargs)

    @classmethod
    def generate_survey_response_excel(cls):
        SurveyResponseGeneratedFile.generate_complete_export_file()

    @classmethod
    def generate_eligible_grantees_list(cls):
        trigger_generate_eligible_grantee_list()
        trigger_generate_eligible_grantee_file_generation()

    @classmethod
    def generate_survey_export_email(cls):
        trigger_survey_export_lookup()

    @classmethod
    def generate_survey_statistics(cls):
        from undp_nuprp.reports.models import SurveyStatistics
        SurveyStatistics.generate_survey_statistics()

    @classmethod
    def clear_survey_statistics(cls):
        from undp_nuprp.reports.models import SurveyStatistics
        SurveyStatistics.objects.all().delete()

    def post(self, request, *args, **kwargs):
        service = request.POST.get('service', None)
        if service == 'survey_response_excel':
            process = Thread(target=self.generate_survey_response_excel)
            process.start()
        if service == 'survey_export_email':
            process = Thread(target=self.generate_survey_export_email)
            process.start()
        if service == 'mpi':
            PGMPIIndicator.generate()
        if service == 'generate_eligible_grantees':
            process = Thread(target=self.generate_eligible_grantees_list)
            process.start()
        if service == 'clear_eligible_grantees':
            EligibleBusinessGrantee.objects.all().delete()
            EligibleApprenticeshipGrantee.objects.all().delete()
            EligibleEducationGrantee.objects.all().delete()
        if service == 'clear_mpi':
            PGMPIIndicator.objects.all().delete()
            PGPovertyIndex.objects.all().delete()
        if service == 'clear_pg_member_info_cache':
            KeyValueCount.objects.all().delete()
            PGMemberInfoCache.objects.all().delete()
        if service == 'generate_pg_member_indicator':
            PGMemberIndicatorManager.generate_pg_member_indicator_cache()
        if service == 'generate_savings_and_credit_alert':
            CDCMonthlyReport.generate_alert_for_pending_reports()
        if service == 'auto_approve_pending_cdc_scg_report':
            kwargs.update({
                'user': CrequestMiddleware.get_request().c_user
            })
            # approving pending cdc reports
            PendingReportApprovalManager.approve_cdc_reports(*args, **kwargs)
            # approving pending scg reports
            PendingReportApprovalManager.approve_scg_reports(*args, **kwargs)
        if service == 'generate_survey_statistics':
            process = Thread(target=self.generate_survey_statistics)
            process.start()
        if service == 'clear_survey_statistics':
            self.clear_survey_statistics()
        if service == 'delete_disabled_survey_and_its_responses':
            DynamicSurvey.delete_disabled_survey_and_its_responses()
        if service == 'generate_cumulative_report':
            CumulativeReportManager.generate_reports()
        if service == 'clear_cumulative_report':
            CumulativeReport.objects.all().delete()
        if service == 'write_api_log':
            LogCacheManager.write_logs_to_database()
        if service == 'generate_poverty_index_short_listed_grantee':
            # _from_time = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
            PGPovertyIndexShortListedGrantee.generate()
        if service == 'generate_third_party_api_data':
            ThirdPartyAPIManager.prepare_third_party_api_data()
        if service == 'generate_poverty_index_short_listed_grantee':
            PGPovertyIndexShortListedGrantee.generate()
        if service == 'generate_exported_files':
            ShortListedEligibleGranteeManager.generate_files()
        if service == 'generate_todays_exported_files':
            ShortListedEligibleGranteeManager.generate_todays_files()
        if service == 'create_scg_for_newly_created_pg':
            SavingsAndCreditGroup.create_scg_for_newly_created_pg()
        if service == 'process_scheduled_pmf_queues':
            PMFUploadedFileQueue.process_scheduled_queues()
        return super(APIWorkerView, self).get(request, *args, **kwargs)
