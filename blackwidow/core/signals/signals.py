
__author__ = 'Sohel'

import django.dispatch

from blackwidow.core.signals.handlers.import_completed_handler import import_completed_handler

import_completed = django.dispatch.Signal()

import_completed.connect(import_completed_handler)


sig_generate_kpi = django.dispatch.Signal()

