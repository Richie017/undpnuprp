from __future__ import absolute_import
BROKER_URL = 'pyamqp://guest:guest@nuprp.info:5672//'
CELERY_IMPORTS=('blackwidow.scheduler.tasks',)
CELERYBEAT_SCHEDULE = {}
CELERY_TIMEZONE = 'UTC'

# The following configs are for crontab monitor for celery tasks
#
# If TASK_MONITOR_ERROR_EMAIL is True, then an email will be sent to the TASK_MONITOR_EMAIL_RECIPIENTS email addresses
# with a list of tasks that did not run in time.
#
# If TASK_MONITOR_SUCCESS_EMAIL is True, then an email will be sent to the TASK_MONITOR_EMAIL_RECIPIENTS email addresses
# mentioning that all tasks ran in time.
#
# TASK_MONITOR_EMAIL_RECIPIENTS is a list of email addresses who will receive email notifications if sending email
# is turn on either by TASK_MONITOR_SUCCESS_EMAIL or TASK_MONITOR_ERROR_EMAIL.
#
# If TASK_MONITOR_RERUN_TASK is True, for each task that were missed by the schedule, task's method will be called to
# manually run the operation.

TASK_MONITOR_ERROR_EMAIL = True
TASK_MONITOR_SUCCESS_EMAIL = True
TASK_MONITOR_EMAIL_RECIPIENTS = []
TASK_MONITOR_RERUN_TASK = False
TASK_MONITOR_IGNORED_TASK_LIST = ['trigger_survey_export_lookup']