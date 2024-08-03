"""
Created by tareq on 10/8/17
"""
from django.core.management.base import BaseCommand

from blackwidow.core.models.clients.client_meta import ClientMeta
from blackwidow.core.models.organizations.organization import Organization
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


class Command(BaseCommand):
    def handle(self, *args, **options):
        organization = Organization.objects.first()
        for pg_survey in SurveyResponse.objects.filter(survey__name__icontains=''):
            pg_member = pg_survey.respondent_client
            gender_question = QuestionResponse.objects.filter(section_response__survey_response_id=pg_survey.pk).first()
            client_meta = pg_member.client_meta
            if not client_meta:
                client_meta = ClientMeta.objects.create(organization=organization)
            if gender_question:
                if gender_question.answer_text.lower() == 'male':
                    client_meta.gender = 'M'
                elif gender_question.answer_text.lower() == 'female':
                    client_meta.gender = 'F'
                elif gender_question.answer_text.lower() == 'hijra':
                    client_meta.gender = 'H'
                client_meta.save()

            disabled_questions_count = QuestionResponse.objects.filter(
                section_response__survey_response_id=pg_survey.pk,
                question__question_code__in=['3.1', '3.2', '3.3', '3.4', '3.5', '3.6'],
                answer_text__in=['Cannot do at all', 'A lot of difficulty']
            ).count()
            if disabled_questions_count > 0:
                client_meta.is_disabled = True
                client_meta.save()

            pg_member.client_meta = client_meta
            pg_member.save()
            print("Updated client meta for {}".format(pg_member, ))
