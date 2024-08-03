import os

from django.core.management import BaseCommand
from django.db.models import Max

__author__ = 'Ziaul Haque'

from settings import STATIC_ROOT
from undp_nuprp.survey.models import SurveyResponse, QuestionResponse


class Command(BaseCommand):

    def handle(self, *args, **options):

        file_path = os.path.join(STATIC_ROOT, 'data/')
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        filename = file_path + 'pg_survey_responses.csv'
        csv = open(filename, "w", encoding='utf-8')
        header = "Survey Response ID, Survey Time,"

        offset = 0
        limit = 2000

        queryset = SurveyResponse.objects.filter(survey_id=3).order_by('date_created')
        # queryset = queryset.filter(
        #     respondent_client__assigned_to__parent__address__geography__parent__name__in=[
        #         "Noakhali", "Gazipur"
        #     ]
        # ).order_by('date_created')
        qr_queryset = QuestionResponse.all_objects.filter(
            section_response__survey_response__survey_id=3
        ).order_by('section_response__survey_response', 'question__question_code')
        max_id = queryset.aggregate(Max('pk'))['pk__max']
        max_processed_id = 0
        question_codes = [
            "1.1", "1.3", "2.6", "2.11", "4.2.2", "4.2.3", "4.2.4", "4.2.5",
            "4.2.6", "4.2.7", "4.2.8", "4.2.9", "4.3.1", "4.3.2", "4.3.3",
            "4.3.4", "4.3.5", "4.3.6",
            "5.1", "5.2",
            "6.1", "6.8", "6.10"
        ]
        # question_codes = ["1.1", "1.3"]
        header += ",".join(question_codes)
        header += "\n"
        csv.write(header)
        total_found = 0
        while max_processed_id < max_id:
            survey_responses = queryset[offset:limit]
            question_responses = qr_queryset.filter(
                section_response__survey_response__in=survey_responses
            ).values('section_response__survey_response', 'question__question_code')

            question_response_dict = {}
            for qr in question_responses:
                key = qr['section_response__survey_response']
                if key not in question_response_dict.keys():
                    question_response_dict[key] = list()
                question_response_dict[key].append(qr['question__question_code'])

            _h = 0
            for survey_response in survey_responses:
                _response_id = survey_response.pk
                max_processed_id = _response_id
                if _h % 500 == 0:
                    print('{}'.format(_h, ))
                _h += 1
                available_questions = set(question_response_dict[_response_id])

                missing_codes = set(question_codes) - available_questions
                if len(missing_codes) == 0:
                    continue

                row = "{0},{1},".format(_response_id, survey_response.render_timestamp(survey_response.survey_time))
                for question_code in question_codes:
                    if question_code in available_questions:
                        row += "{0},".format('available')
                    else:
                        row += "{0},".format('missing')
                row += "\n"
                total_found += 1
                # print(missing_codes)
                # print(row)
                csv.write(row)
            offset += 2000
            limit += 2000
            print(limit)
        print("Total responses found: {0}".format(total_found))
        csv.close()
