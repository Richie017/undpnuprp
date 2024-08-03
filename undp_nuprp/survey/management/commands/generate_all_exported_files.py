"""
    Created by tareq on 3/13/17
"""

from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from undp_nuprp.survey.models.export.survey_response_generated_file import SurveyResponseGeneratedFile

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        SurveyResponseGeneratedFile.generate_complete_export_file()
