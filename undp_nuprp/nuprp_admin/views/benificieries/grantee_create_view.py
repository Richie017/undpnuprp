"""
Created by tareq on 10/2/17
"""
from django.http.response import JsonResponse

from blackwidow.core.generics.views.create_view import GenericCreateView
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.benificieries.grantee import Grantee
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


@override_view(model=Grantee, view=ViewActionEnum.Create)
class GranteeCreateView(GenericCreateView):
    def get(self, request, *args, **kwargs):
        selected_pg_member_id = request.GET.get('pg_member', 0)
        if selected_pg_member_id > 0:
            gender = ''
            age = ''
            religion = ''
            ethnicity = ''
            education = ''
            survey_response = SurveyResponse.objects.filter(respondent_client_id=selected_pg_member_id).first()
            if survey_response:
                gender_response = QuestionResponse.objects.filter(question__question_code='1.5',
                                                                  section_response__survey_response_id=survey_response.pk).first()
                if gender_response:
                    gender = gender_response.answer_text

                age_response = QuestionResponse.objects.filter(question__question_code='4.2.4',
                                                               section_response__survey_response_id=survey_response.pk).first()
                if age_response:
                    age = age_response.answer_text

                religion_response = QuestionResponse.objects.filter(question__question_code='2.5',
                                                                    section_response__survey_response_id=survey_response.pk).first()
                if religion_response:
                    religion = gender_response.answer_text

                ethnicity_response = QuestionResponse.objects.filter(question__question_code='2.6',
                                                                     section_response__survey_response_id=survey_response.pk).first()
                if ethnicity_response:
                    ethnicity = ethnicity_response.answer_text

                education_response = QuestionResponse.objects.filter(question__question_code='2.7',
                                                                     section_response__survey_response_id=survey_response.pk).first()
                if education_response:
                    education = education_response.answer_text
            return JsonResponse(
                {
                    'gender': gender, 'age': age, 'religion': religion, 'ethnicity': ethnicity, 'education': education
                }
            )
        return super(GranteeCreateView, self).get(request, *args, **kwargs)
