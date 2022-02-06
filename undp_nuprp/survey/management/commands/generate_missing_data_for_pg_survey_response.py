import csv
import json
import os
import uuid

from django.core.management import BaseCommand

from blackwidow.core.models import ApiCallLog
from blackwidow.engine.extensions import Clock
from settings import STATIC_ROOT
from undp_nuprp.survey.models import SurveyResponse, QuestionResponse, Question, SectionResponse

__author__ = "Ziaul Haque"


class Command(BaseCommand):
    def load_data_from_csv(self, csv_path):
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            data = []
            for row in csv_reader:
                data.append(row)
            return data

    def handle(self, *args, **options):

        question_codes = [
            "1.1", "1.3", "2.6", "2.11", "4.2.2", "4.2.3", "4.2.4", "4.2.5",
            "4.2.6", "4.2.7", "4.2.8", "4.2.9", "4.3.1", "4.3.2", "4.3.3",
            "4.3.4", "4.3.5", "4.3.6",
            "5.1", "5.2",
            "6.1", "6.8", "6.10"
        ]

        # question_codes = ["1.1", "1.3"]
        survey_id = 3
        organization_id = 1
        queryset = SurveyResponse.objects.filter(survey_id=survey_id)

        filename = os.path.join(STATIC_ROOT, 'data/pg_survey_responses.csv')
        processable_survey_responses = self.load_data_from_csv(filename)[1:]

        filename = os.path.join(STATIC_ROOT, 'data/pg_survey_api_log.csv')
        processable_api_logs = self.load_data_from_csv(filename)[1:]

        api_log_dict = {}
        for api_log in processable_api_logs:
            api_log_dict[api_log[1]] = api_log[0]

        question_code_dict = {}
        for q in Question.objects.filter(section__survey_id=survey_id):
            question_code_dict[q.id] = {'code': q.question_code, 'section_id': q.section_id}

        total_processed = 0
        offset = 0
        limit = 1000
        processed_responses = []
        while total_processed < len(processable_survey_responses):
            queryset_slot = processable_survey_responses[offset:limit]
            response_dict = {}
            for item in queryset_slot:
                response_dict[item[0]] = item

            recoverable_response_queryset = queryset.filter(
                pk__in=response_dict.keys()
            ).values('pk', 'tsync_id', 'date_created', 'last_updated', 'created_by', 'last_updated_by').order_by(
                'date_created')
            creatable_entries = []
            for response in recoverable_response_queryset:
                tsync_id = response['tsync_id']
                response_data = response_dict[str(response['pk'])][2:]
                api_log_id = api_log_dict.get(tsync_id, None)
                total_processed += 1

                if not api_log_id:
                    continue

                api_log = ApiCallLog.objects.get(pk=api_log_id)
                body = json.loads(api_log.request_body)
                questions = body['questions']
                question_dict = {}
                for q in questions:
                    q_id = q['question']
                    q_code = question_code_dict[q_id]['code']
                    question_dict[q_code] = q

                section_response_dict = {}
                for section_response in SectionResponse.all_objects.filter(survey_response_id=response['pk']):
                    section_response_dict[section_response.section_id] = section_response.pk

                for index, question_code in enumerate(question_codes):
                    status = response_data[index]
                    if status == 'missing':
                        # print(question_code)
                        if question_code in question_dict.keys():
                            # print(question_code)
                            q_data = question_dict[question_code]

                            question_id = q_data['question']
                            answer_id = q_data['answer']
                            question_text = q_data['question_text']
                            answer_text = q_data['answer_text']
                            index = q_data['index']

                            section_id = question_code_dict[question_id]['section_id']
                            section_response_id = section_response_dict[section_id]

                            qr_instance = QuestionResponse()
                            qr_instance.type = QuestionResponse.__name__
                            qr_instance.organization_id = organization_id
                            qr_instance.tsync_id = uuid.uuid4()
                            qr_instance.date_created = response['date_created']
                            qr_instance.last_updated = response['last_updated']
                            qr_instance.created_by_id = response['created_by']
                            qr_instance.last_updated_by_id = response['last_updated_by']

                            qr_instance.section_response_id = section_response_id
                            qr_instance.question_id = question_id
                            qr_instance.answer_id = answer_id
                            qr_instance.question_text = question_text
                            qr_instance.answer_text = answer_text
                            qr_instance.index = index

                            creatable_entries.append(qr_instance)
                            processed_responses.append(response['pk'])

                if total_processed % 500 == 0:
                    print("Total Processed {0}, Last Processed ID {1}".format(total_processed, response['pk']))

            if len(creatable_entries) > 0:
                QuestionResponse.objects.bulk_create(creatable_entries, batch_size=1000)
                print("{0} entries created...".format(len(creatable_entries)))
            offset += 1000
            limit += 1000

        print("total {0} response updated".format(len(set(processed_responses))))

        current_timestamp = Clock.timestamp()
        updatable_entries = []
        for r in SurveyResponse.objects.filter(pk__in=set(processed_responses)):
            r.last_updated = current_timestamp
            updatable_entries.append(r)
            current_timestamp += 1

            if len(updatable_entries) % 1000 == 0:
                SurveyResponse.objects.bulk_update(updatable_entries, batch_size=1000)
                print("{0} entries updated...".format(len(updatable_entries)))
                updatable_entries = []

        SurveyResponse.objects.bulk_update(updatable_entries, batch_size=1000)
        print("{0} entries updated...".format(len(updatable_entries)))
