"""
Created by Shuvro on 22/07/18
"""
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models.aggregates import Count

from undp_nuprp.approvals.models.savings_and_credits.cdc_reports.approved_cdc_monthly_report import \
    ApprovedCDCMonthlyReport
from undp_nuprp.approvals.models.savings_and_credits.scg_reports.approved_scg_monthly_report import \
    ApprovedSCGMonthlyReport

__author__ = 'Shuvro'


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            print('Start Updating baseline status of SCF Reports')
            approved_scg_report_ids = list(ApprovedSCGMonthlyReport.objects.distinct('parent_id').values_list(
                'pk', flat=True).order_by('parent_id', '-on_spot_creation_time'))
            print('Total Number of Approved SCG Reports : {0}'.format(len(approved_scg_report_ids)))

            duplicate_scg_ids = list(ApprovedSCGMonthlyReport.objects.values_list('scg_id', flat=True).annotate(
                total_scg=Count('scg_id')).filter(total_scg__gt=1, pk__in=approved_scg_report_ids))

            baseline_scg_ids = list(
                ApprovedSCGMonthlyReport.objects.filter(pk__in=list(approved_scg_report_ids)).exclude(
                    scg_id__in=duplicate_scg_ids).values_list('pk', flat=True))

            baseline_scg_ids.extend(list(ApprovedSCGMonthlyReport.objects.filter(
                pk__in=approved_scg_report_ids,
                scg_id__in=duplicate_scg_ids).order_by(
                'scg_id',
                'on_spot_creation_time').distinct(
                'scg_id').values_list('pk', flat=True)))

            total_updated = ApprovedSCGMonthlyReport.objects.filter(pk__in=baseline_scg_ids).update(is_baseline=True)

            print('Total {0} SCG reports baseline status has updated!'.format(total_updated))

            print('Start Updating baseline status of CDC Reports')
            approved_cdc_reports_ids = list(ApprovedCDCMonthlyReport.objects.distinct('parent_id').values_list(
                'pk', flat=True).order_by('parent_id', '-on_spot_creation_time'))

            print('Total Number of approved CDC Reports: {0}'.format(len(approved_cdc_reports_ids)))

            duplicate_cdc_ids = list(ApprovedCDCMonthlyReport.objects.values_list('cdc_id', flat=True).annotate(
                total_cdc=Count('cdc_id')).filter(total_cdc__gt=1, pk__in=list(approved_cdc_reports_ids)))

            baseline_cdc_ids = list(
                ApprovedCDCMonthlyReport.objects.filter(pk__in=list(approved_cdc_reports_ids)).exclude(
                    cdc_id__in=duplicate_cdc_ids).values_list('pk', flat=True))

            baseline_cdc_ids.extend(list(ApprovedCDCMonthlyReport.objects.filter(
                pk__in=approved_cdc_reports_ids,
                cdc_id__in=duplicate_cdc_ids).order_by(
                'cdc_id',
                'on_spot_creation_time').distinct(
                'cdc_id').values_list('pk', flat=True)))

            total_updated = ApprovedCDCMonthlyReport.objects.filter(pk__in=baseline_cdc_ids).update(is_baseline=True)

            print('Total {0} CDC reports baseline has updated!'.format(total_updated))
