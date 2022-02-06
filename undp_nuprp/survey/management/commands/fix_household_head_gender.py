"""
    Written by tareq on 9/30/18
"""
from django.core.management import BaseCommand

from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationGrantee
from undp_nuprp.reports.config.constants.pg_survey_constants import HH_GENDER_QUESTION_CODE, GENDER_QUESTION_CODE
from undp_nuprp.survey.models import PGMPIIndicator, QuestionResponse

__author__ = 'Tareq'


class Command(BaseCommand):
    def update_mpi_indicators(self):
        female_count = 0
        male_count = 0
        total = PGMPIIndicator.objects.all().count()
        handled = 0

        updatable_queue = []

        for mpi in PGMPIIndicator.objects.all():
            if handled % 500 == 0:
                print("Handling {}-{}/{}\n>> Male headed: {}\n>> Female headed: {}".format(
                    handled, min(handled + 500, total), total, male_count, female_count))
            handled += 1

            update = False
            female_headed = False
            male_headed = False
            hh_head_response = QuestionResponse.objects.filter(
                section_response__survey_response_id=mpi.survey_response_id,
                question__question_code=HH_GENDER_QUESTION_CODE
            ).values('answer_text').first()

            if hh_head_response:
                if hh_head_response['answer_text'].lower() == 'female':
                    female_headed = True
                elif hh_head_response['answer_text'].lower() == 'male':
                    male_headed = True
            else:
                member_response = QuestionResponse.objects.filter(
                    section_response__survey_response_id=mpi.survey_response_id,
                    question__question_code=GENDER_QUESTION_CODE
                ).values('answer_text').first()

                if member_response:
                    if member_response['answer_text'].lower() == 'female':
                        female_headed = True
                    elif member_response['answer_text'].lower() == 'male':
                        male_headed = True

            if female_headed:
                female_count += 1
                if not mpi.is_female_headed:
                    mpi.is_female_headed = True
                    update = True
            else:
                if mpi.is_female_headed:
                    mpi.is_female_headed = False
                    update = True

            if male_headed:
                male_count += 1
                if not mpi.is_male_headed:
                    mpi.is_male_headed = True
                    update = True
            else:
                if mpi.is_male_headed:
                    mpi.is_male_headed = False
                    update = True

            if update:
                updatable_queue.append(mpi)
                EligibleBusinessGrantee.objects.filter(survey_response_id=mpi.survey_response_id).exclude(
                    is_female_headed=mpi.is_female_headed).update(is_female_headed=mpi.is_female_headed)
                EligibleApprenticeshipGrantee.objects.filter(survey_response_id=mpi.survey_response_id).exclude(
                    is_female_headed=mpi.is_female_headed).update(is_female_headed=mpi.is_female_headed)
                EligibleEducationGrantee.objects.filter(survey_response_id=mpi.survey_response_id).exclude(
                    is_female_headed=mpi.is_female_headed).update(is_female_headed=mpi.is_female_headed)

        if updatable_queue:
            print("Updating {} entries.".format(len(updatable_queue), ))
            PGMPIIndicator.objects.bulk_update(updatable_queue, batch_size=250)

    def handle(self, *args, **options):
        print("Update MPI indicators")
        self.update_mpi_indicators()
