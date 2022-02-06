"""
    Created by tareq on 7/23/19
"""
from django.core.management import BaseCommand

from undp_nuprp.survey.models import QuestionResponse, SectionResponse

__author__ = "Tareq"


class Command(BaseCommand):
    def handle(self, *args, **options):
        wrong_placed_responses = QuestionResponse.objects.filter(section_response__section_id=16).filter(
            question__question_code__startswith="5.")

        checked = 0
        handled = 0
        for r in wrong_placed_responses:
            checked += 1
            target_section = SectionResponse.objects.filter(section_id=22, survey_response_id=r.section_response.survey_response_id).first()
            if target_section:
                r.section_response = target_section
                r.save()
                handled += 1
            if checked % 100 == 0:
                print("Checked: {}, fixed: {}".format(checked,handled))
        print("Checked: {}, fixed: {}".format(checked, handled))