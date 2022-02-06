
__author__ = 'Sohel'

import django.dispatch

from blackwidow.core.signals.handlers.import_completed_handler import import_completed_handler

import_completed = django.dispatch.Signal(providing_args=["items", "user", "organization"])

import_completed.connect(import_completed_handler)


sig_generate_kpi = django.dispatch.Signal(providing_args=["ref_user"])

