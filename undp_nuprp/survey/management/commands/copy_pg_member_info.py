from django.core.management.base import BaseCommand
from datetime import datetime

from blackwidow.engine.extensions.date_age_converter import calculate_age
from undp_nuprp.reports.config.constants.pg_survey_constants import PG_MEMBER_SURVEY_NAME, HH_QUESTION_CODE
from undp_nuprp.survey.models import SurveyResponse, QuestionResponse, Question


class Command(BaseCommand):
    def handle(self, *args, **options):

        HH_QUESTIONS = {
            '1.1': '4.2.1', '1.3': '4.2.2', '1.4': '4.2.4', '1.5': '4.2.3', '2.2': '4.2.5', '2.3': '4.2.6',
            '2.4': '4.2.7',
            '2.6': '4.2.8', '2.11': '4.2.9', '3.1': '4.3.1', '3.2': '4.3.2', '3.3': '4.3.3', '3.4': '4.3.4',
            '3.5': '4.3.5', '3.6': '4.3.6'
        }
        survey_responses = SurveyResponse.objects.filter(survey__name=PG_MEMBER_SURVEY_NAME).all()
        response = 0
        for survey_response in survey_responses:
            hh_question = QuestionResponse.objects.filter(question__question_code=HH_QUESTION_CODE,
                                                          answer_text='Yes',
                                                          section_response__survey_response_id=survey_response.pk).first()
            if hh_question:
                hh_question_responses = QuestionResponse.objects.filter(
                    question__question_code__in=list(HH_QUESTIONS.keys()),
                    section_response__survey_response_id=survey_response.pk)
                for hh_question_response in hh_question_responses:
                    hh_question_code = HH_QUESTIONS[hh_question_response.question.question_code]
                    hh_original_question = Question.objects.filter(section__survey__name=PG_MEMBER_SURVEY_NAME,
                                                                   question_code=hh_question_code).first()
                    hh_question_id = hh_original_question.pk
                    if hh_question_code == '4.2.3':
                        try:
                            birth_date = datetime.strptime(hh_question_response.answer_text, "%d-%b-%Y")
                        except:
                            birth_date = datetime(year=int(hh_question_response.answer_text.split('-')[-1]), month=1,
                                                  day=1)
                        hh_age = calculate_age(birth_date)
                        copied_hh_response = QuestionResponse(
                            organization_id=hh_question.organization_id,
                            question_id=hh_question_id,
                            question_text=hh_original_question.text,
                            answer_id=hh_question_response.answer_id,
                            answer_text=hh_age,
                            section_response_id=hh_question.section_response_id)
                    else:
                        copied_hh_response = QuestionResponse(
                            organization_id=hh_question.organization_id,
                            question_id=hh_question_id,
                            question_text=hh_original_question.text,
                            answer_id=hh_question_response.answer_id,
                            answer_text=hh_question_response.answer_text,
                            section_response_id=hh_question.section_response_id)
                    copied_hh_response.save()
            response += 1
        print(str(response) + " Survey Response Updated")
