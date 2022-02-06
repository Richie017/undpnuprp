from __future__ import absolute_import

import datetime
from datetime import timedelta

from celery.schedules import crontab
from celery.task.base import periodic_task
from django.db import transaction
from djcelery.models import PeriodicTask

from blackwidow.core.managers.log_cache_manager import LogCacheManager
from blackwidow.core.models import ConsoleUser
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.log.scheduler_log import SchedulerLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.core.models.system.device import UserDevice
from blackwidow.dbmediabackup.models.backup_task_queue import DBMediaBackupTaskQueue
from blackwidow.engine.enums.scheduled_task_enum import ScheduledTaskStatusEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.scheduler.celery import app as celery_app
from dynamic_survey.models import DynamicSurveyResponseGeneratedFile
from undp_nuprp.approvals.managers.cdc_report_manager import CDCReportManager
from undp_nuprp.approvals.managers.cumulative_report_manager import CumulativeReportManager
from undp_nuprp.approvals.managers.eligible_grantee_manager import EligibleGranteeManager
from undp_nuprp.approvals.managers.pending_report_approval_manager import PendingReportApprovalManager
from undp_nuprp.approvals.managers.pg_member_indicator_manager import PGMemberIndicatorManager
from undp_nuprp.approvals.managers.primary_group_member_alert_manager import PrimaryGroupMemberAlertManager
from undp_nuprp.approvals.managers.short_listed_eligible_grantee_manager import ShortListedEligibleGranteeManager
from undp_nuprp.approvals.models import CDCMonthlyReport, PMFUploadedFileQueue
from undp_nuprp.nuprp_admin.enums.delete_survey_status_enum import DeleteSurveyStatusEnum
from undp_nuprp.nuprp_admin.models import SavingsAndCreditGroup, DeleteTestSurvey
from undp_nuprp.reports.managers.third_party.third_party_api_manager import ThirdPartyAPIManager
from undp_nuprp.reports.models import SurveyStatistics
from undp_nuprp.reports.models.cache.sef_grantees_info_cache import SEFGranteesInfoCache
from undp_nuprp.survey.managers.enumerator_survey_stats_manager import EnumeratorSurveyStatisticsManager
from undp_nuprp.survey.managers.pg_survey_deletion_manager import PGSurveyDeletionManager
from undp_nuprp.survey.models import PGMPIIndicator
from undp_nuprp.survey.models.entity.survey import Survey
from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile
from undp_nuprp.survey.models.indicators.poverty_index_short_listed_grantee import PGPovertyIndexShortListedGrantee
from undp_nuprp.survey.models.schedulers.survey_export_task_queue import SurveyExportTaskQueue

'''
List of Tasks:
    Every 05 minutes:   trigger_dbmediabackup                                  Check if there is DB backup pending task. If yes, then backup DB
    Everyday at 11:00 PM GMT:  trigger_dbmediabackup_to_be_run_once_everyday   Daily DB backup task
    Everyday at 10:00 PM GMT:  trigger_dbmediarestore                          Daily DB restore task
    Everyday at 01:45 AM GMT:  trigger_generate_poverty_index_short_listed_grantee
    Every 02 minutes:   trigger_survey_export_lookup                           Check if there is SurveyResponse Export pending task. If yes, then export SurveyResponse
'''



@periodic_task(run_every=crontab(minute='*/2'))  # Every 02 minutes
def trigger_survey_export_lookup(*args, **kwargs):
    print("calling - trigger_survey_export_lookup method")
    start_time = int(datetime.datetime.now().timestamp() * 1000)
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_survey_export_lookup')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        # Cleanup deleted surveys
        print("calling - cleanup_deleted_pg_member_survey method")
        EnumeratorSurveyStatisticsManager.cleanup_deleted_pg_member_survey()
        # Update survey stats
        print("calling - update_enumerator_survey_statistics_cache method")
        EnumeratorSurveyStatisticsManager.update_enumerator_survey_statistics_cache()
        # generate survey response export file
        print("calling - generate_survey_export method")
        export_completed = SurveyExportTaskQueue.generate_survey_export()
        if export_completed:
            print("creating scheduler log with SUCCESS status")
            scheduler_log = SchedulerLog.objects.create(
                reference_task='trigger_survey_export_lookup',
                organization=Organization.objects.filter(is_master=True)[0],
                status=ScheduledTaskStatusEnum.SUCCESS.value,
                start_time=start_time,
                end_time=int(datetime.datetime.now().timestamp() * 1000)
            )
            print("created")

    except Exception as exp:
        print("creating scheduler log with Error status")
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
        scheduler_log = SchedulerLog.objects.create(
            reference_task='trigger_survey_export_lookup',
            organization=Organization.objects.filter(is_master=True)[0],
            status=ScheduledTaskStatusEnum.ERROR.value,
            start_time=start_time,
            end_time=int(datetime.datetime.now().timestamp() * 1000)
        )
        print("created.")


@periodic_task(run_every=crontab(minute='*/5'))
def trigger_delete_survey(*args, **kwargs):
    start_time = int(datetime.datetime.now().timestamp() * 1000)
    to_run = None
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_delete_survey')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        if not DeleteTestSurvey.objects.filter(status=DeleteSurveyStatusEnum.RUNNING.value).exists():
            to_run = DeleteTestSurvey.objects.filter(
                status=DeleteSurveyStatusEnum.SCHEDULED.value
            ).order_by('date_created').first()
            if to_run:
                to_run.status = DeleteSurveyStatusEnum.RUNNING.value
                to_run.save()
                total_deleted = PGSurveyDeletionManager.delete_pg_survey_and_its_reference(
                    city=to_run.city,
                    from_time=int(to_run.from_date.timestamp() * 1000),
                    to_time=int(to_run.to_date.replace(hour=23, minute=59, second=59).timestamp() * 1000)
                )
                to_run.status = DeleteSurveyStatusEnum.COMPLETED.value
                to_run.date_of_deletion = int(datetime.datetime.now().timestamp() * 1000)
                to_run.number_of_deleted_surveys = total_deleted
                to_run.save()

                scheduler_log = SchedulerLog.objects.create(
                    reference_task='trigger_delete_survey',
                    organization=Organization.objects.filter(is_master=True)[0],
                    status=ScheduledTaskStatusEnum.SUCCESS.value,
                    start_time=start_time,
                    end_time=int(datetime.datetime.now().timestamp() * 1000)
                )
    except Exception as exp:
        if to_run:
            to_run.status = DeleteSurveyStatusEnum.FAILED.value
            to_run.save()

        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
        scheduler_log = SchedulerLog.objects.create(
            reference_task='trigger_delete_survey',
            organization=org,
            status=ScheduledTaskStatusEnum.ERROR.value,
            start_time=start_time,
            end_time=int(datetime.datetime.now().timestamp() * 1000)
        )


# @periodic_task(run_every=crontab(minute=0, hour=23))  # Run at 5:00 AM daily (Bangladesh Time)
def trigger_dbmediabackup_to_be_run_once_everyday(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_dbmediabackup_to_be_run_once_everyday',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    with transaction.atomic():
        try:
            periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_daily_dbmediabackup')
            if not created:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            # backup database and media files
            DBMediaBackupTaskQueue.generate_backup_daily()
            status = ScheduledTaskStatusEnum.SUCCESS.value
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


# @periodic_task(run_every=crontab(minute='*/30'))  # Run every 30 minutes
def trigger_api_log_write_to_db(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_api_log_write_to_db',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_api_log_write_to_db')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        LogCacheManager.write_logs_to_database()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=5, hour=18))  # Run at 12:05 AM
def trigger_daily_mpi_calculation(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_daily_mpi_calculation',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_daily_mpi_calculation')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        # MPIIndicator.generate()
        PGMPIIndicator.generate()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=45, hour=18))  # Run at 12:45 AM
def trigger_daily_alert_generation(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_daily_alert_generation',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_daily_alert_generation')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        PrimaryGroupMemberAlertManager.generate()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=15, hour=19))  # Run everyday at 1:15 AM
def trigger_generate_pg_indicator_cache(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_pg_indicator_cache',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(
            name='trigger_generate_pg_indicator_cache')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        PGMemberIndicatorManager.generate_pg_member_indicator_cache()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=30, hour=19))  # Run everyday at 1:30 AM
def trigger_generate_sef_grantees_cache(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_sef_grantees_cache',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(
            name='trigger_generate_sef_grantees_cache')
        if not created:
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        SEFGranteesInfoCache.generate_sef_grantees_info_cache()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=45, hour=19))  # Run at 01:45 AM
def trigger_generate_poverty_index_short_listed_grantee(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_poverty_index_short_listed_grantee',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(
            name='trigger_generate_poverty_index_short_listed_grantee')
        if not created:
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
            _yesterday = datetime.datetime.now() - timedelta(days=1)
            # _yesterday = int(_yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
            PGPovertyIndexShortListedGrantee.generate()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=15, hour=20))  # Run at 02:15 AM
def trigger_generate_third_party_api_data(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_third_party_api_data',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(
            name='trigger_generate_third_party_api_data')
        if not created:
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        ThirdPartyAPIManager.prepare_pg_member_count_data()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=30, hour=20))  # Run everyday at 2:30 AM
def trigger_generate_eligible_grantee_list(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_eligible_grantee_list',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(
            name='trigger_generate_eligible_grantee_list')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        EligibleGranteeManager.generate()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=15, hour=21))  # Run everyday at 3:15 AM
def trigger_generate_eligible_grantee_file_generation(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_eligible_grantee_file_generation',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(
            name='trigger_generate_eligible_grantee_file_generation')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
        handling_time = datetime.datetime.now()
        EligibleGranteeManager.generate_files(
            last_run_time=last_run_time, handle_upto_time=handling_time)
        status = ScheduledTaskStatusEnum.SUCCESS.value
        periodic_task_obj.last_run_at = handling_time
        periodic_task_obj.save()
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=50, hour=21))  # Run everyday at 3:50 AM
def trigger_create_scg_for_newly_created_pg(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_create_scg_for_newly_created_pg',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    try:
        periodic_task_obj, created = PeriodicTask.objects.get_or_create(
            name='trigger_create_scg_for_newly_created_pg')
        if not created:
            last_run_time = periodic_task_obj.last_run_at
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()
        else:
            last_run_time = datetime.datetime.fromtimestamp(0)
            periodic_task_obj.last_run_at = Clock.utcnow()
            periodic_task_obj.save()

        SavingsAndCreditGroup.create_scg_for_newly_created_pg()
        status = ScheduledTaskStatusEnum.SUCCESS.value
    except Exception as exp:
        org = Organization.objects.get(is_master=True)
        ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=00, hour=22))  # Run everyday at 4:00 AM
def trigger_generate_short_listed_grantee_file(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_short_listed_grantee_file',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )

    status = ScheduledTaskStatusEnum.ERROR.value

    with transaction.atomic():
        try:
            periodic_task_obj, created = PeriodicTask.objects.get_or_create(
                name='trigger_generate_short_listed_grantee_file')

            if not created:
                last_run_time = periodic_task_obj.last_run_at
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)

            handling_time = datetime.datetime.now()
            ShortListedEligibleGranteeManager.generate_files(last_run_time=last_run_time,
                                                             handle_upto_time=handling_time)

            status = ScheduledTaskStatusEnum.SUCCESS.value
            periodic_task_obj.last_run_at = handling_time
            periodic_task_obj.save()
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)

    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=10, hour=22))  # Run everyday at 4:10 AM
def trigger_survey_export_excel(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_survey_export_excel',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    with transaction.atomic():
        try:
            periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_survey_export_excel')
            if not created:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            # generate survey response excel file
            survey_id_list = Survey.objects.all().values_list('pk', flat=True)
            for survey_id in survey_id_list:
                SurveyResponseGeneratedFile.perform_routine_export_files_generation(survey_id=survey_id)
            status = ScheduledTaskStatusEnum.SUCCESS.value
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=0, hour=23))  # Run at 5:00 AM daily (Bangladesh Time)
def trigger_dynamic_survey_export_excel(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_dynamic_survey_export_excel',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    with transaction.atomic():
        try:
            periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_dynamic_survey_export_excel')
            if not created:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            DynamicSurveyResponseGeneratedFile.perform_routine_export_files_generation()
            status = ScheduledTaskStatusEnum.SUCCESS.value
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=30, hour=22))  # Run everyday at 4:30 AM
def trigger_update_cdc_report_calculative_field_info(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_update_cdc_report_calculative_field_info',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    with transaction.atomic():
        try:
            periodic_task_obj, status = PeriodicTask.objects.get_or_create(
                name='trigger_update_cdc_report_calculative_field_info')
            if not status:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            # updating cdc report objects calculative field's information
            CDCReportManager.generate()

            status = ScheduledTaskStatusEnum.SUCCESS.value
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=40, hour=22, day_of_month='20'))  # Run on 4th day at 4:40 AM of every month
def trigger_generate_alert_for_pending_reports(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_alert_for_pending_reports',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    with transaction.atomic():
        try:
            periodic_task_obj, created = PeriodicTask.objects.get_or_create(
                name='trigger_generate_alert_for_pending_reports')
            if not created:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            # generate alert for pending reports (both SCG & CDC)
            CDCMonthlyReport.generate_alert_for_pending_reports()

            status = ScheduledTaskStatusEnum.SUCCESS.value
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=40, hour=22, day_of_month='23'))  # Run on 7th day at 4:40 AM of every month
def trigger_auto_approval_for_pending_reports(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_auto_approval_for_pending_reports',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    with transaction.atomic():
        try:
            periodic_task_obj, status = PeriodicTask.objects.get_or_create(
                name='trigger_auto_approval_for_pending_reports')
            if not status:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            # auto approve pending reports (both SCG & CDC)
            # updating kwargs dict by background user
            kwargs.update({
                'user': ConsoleUser.objects.filter(user__username='BackgroundUser').first()
            })
            PendingReportApprovalManager.approve_scg_reports(*args, **kwargs)
            PendingReportApprovalManager.approve_cdc_reports(*args, **kwargs)

            status = ScheduledTaskStatusEnum.SUCCESS.value
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


# @periodic_task(run_every=crontab(minute='*/10'))  # Every 10 minutes
def trigger_generate_survey_statistics(*args, **kwargs):
    with transaction.atomic():
        start_time = int(datetime.datetime.now().timestamp() * 1000)
        try:
            periodic_task_obj, created = PeriodicTask.objects.get_or_create(name='trigger_generate_survey_statistics')
            if not created:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            # generate survey statistics
            export_completed = SurveyStatistics.generate_survey_statistics()
            if export_completed:
                scheduler_log = SchedulerLog.objects.create(
                    reference_task='trigger_generate_survey_statistics',
                    organization=Organization.objects.filter(is_master=True)[0],
                    status=ScheduledTaskStatusEnum.SUCCESS.value,
                    start_time=start_time,
                    end_time=int(datetime.datetime.now().timestamp() * 1000)
                )
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
            scheduler_log = SchedulerLog.objects.create(
                reference_task='trigger_generate_survey_statistics',
                organization=Organization.objects.filter(is_master=True)[0],
                status=ScheduledTaskStatusEnum.ERROR.value,
                start_time=start_time,
                end_time=int(datetime.datetime.now().timestamp() * 1000)
            )


# @periodic_task(run_every=crontab(minute=40, hour=22, day_of_month='9'))  # Run on 9th day at 4:40 AM of every month
def trigger_generate_cumulative_report(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_generate_cumulative_report',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )
    status = ScheduledTaskStatusEnum.ERROR.value
    with transaction.atomic():
        try:
            periodic_task_obj, status = PeriodicTask.objects.get_or_create(
                name='trigger_generate_cumulative_report')
            if not status:
                last_run_time = periodic_task_obj.last_run_at
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)
                periodic_task_obj.last_run_at = Clock.utcnow()
                periodic_task_obj.save()

            # generate cdc wise cumulative report
            CumulativeReportManager.generate_reports()

            status = ScheduledTaskStatusEnum.SUCCESS.value
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)
    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@periodic_task(run_every=crontab(minute=50, hour=22))  # Run everyday at 4:50 AM
def trigger_process_scheduled_pmf_queues(*args, **kwargs):
    scheduler_log = SchedulerLog.objects.create(
        reference_task='trigger_process_scheduled_pmf_queues',
        organization=Organization.objects.filter(is_master=True)[0], status=ScheduledTaskStatusEnum.RUNNING.value,
        start_time=int(datetime.datetime.now().timestamp() * 1000)
    )

    status = ScheduledTaskStatusEnum.ERROR.value

    with transaction.atomic():
        try:
            periodic_task_obj, created = PeriodicTask.objects.get_or_create(
                name='trigger_process_scheduled_pmf_queues')

            if not created:
                last_run_time = periodic_task_obj.last_run_at
            else:
                last_run_time = datetime.datetime.fromtimestamp(0)

            handling_time = datetime.datetime.now()
            PMFUploadedFileQueue.process_scheduled_queues()

            status = ScheduledTaskStatusEnum.SUCCESS.value
            periodic_task_obj.last_run_at = handling_time
            periodic_task_obj.save()
        except Exception as exp:
            org = Organization.objects.get(is_master=True)
            ErrorLog.log(exp, organization=org)

    scheduler_log.status = status
    scheduler_log.end_time = int(datetime.datetime.now().timestamp() * 1000)
    scheduler_log.save()


@celery_app.task
def update_user_device_logs(user, request_meta):
    """
    create UserDevice if not exists by IMEI, update UserDevice if any info changes,
    create DeviceApkUpdateLog if not exists or apk_version changes
    :param request:
    :return: None
    """
    organization = user.organization
    try:
        imei_number = request_meta.get('HTTP_IMEI_NUMBER', '')
    except:
        imei_number = ''

    try:
        phone_number = request_meta.get('HTTP_PHONE_NUMBER', '')
    except:
        phone_number = ''

    try:
        model = request_meta.get('HTTP_DEVICE_MODEL', '')
    except:
        model = ''

    try:
        manufacturer = request_meta.get('HTTP_MANUFACTURER', '')
    except:
        manufacturer = ''

    try:
        os_version = request_meta.get('HTTP_DEVICE_OS', '')
    except:
        os_version = ''

    try:
        dpi = request_meta.get('HTTP_DEVICE_DPI', 0)
    except:
        dpi = ''

    try:
        apk_version = request_meta.get('HTTP_APK_VERSION', None)
    except:
        apk_version = None

    if organization and user and imei_number:
        device = UserDevice.objects.filter(user=user).first()
        if not device:
            device = UserDevice(user=user, imei_number=imei_number, phone_number=phone_number, model=model,
                                manufacturer=manufacturer, os_version=os_version, apk_version=apk_version,
                                dpi=dpi, organization=organization)
            device.save()

        elif device.phone_number != phone_number \
                or device.model != model or device.manufacturer != manufacturer or device.os_version != os_version \
                or device.apk_version != apk_version or device.dpi != dpi or device.imei_number != imei_number:
            device.imei_number = imei_number
            device.organization = user.organization
            device.phone_number = phone_number
            device.model = model
            device.manufacturer = manufacturer
            device.os_version = os_version
            device.apk_version = apk_version
            device.dpi = dpi
            device.save()
