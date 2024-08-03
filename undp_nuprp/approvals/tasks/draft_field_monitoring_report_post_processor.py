from __future__ import absolute_import

from blackwidow.scheduler.celery import app as celery_app


@celery_app.task
def perform_draft_field_monitoring_report_post_processing(instance, request_user):
    instance.perform_mail_sending()
