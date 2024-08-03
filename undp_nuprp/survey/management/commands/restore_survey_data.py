"""
    Created by tareq on 7/22/19
"""
import random

from django.core.management import BaseCommand

from undp_nuprp.survey.models import SurveyResponse, QuestionResponse, Question, Answer, SectionResponse

__author__ = "Tareq"


class Command(BaseCommand):
    def handle(self, *args, **options):
        pg_member_survey_responses = SurveyResponse.objects.filter(survey_id=3)

        total_checked = 0
        missed_5_3 = 0
        missed_5_8 = 0
        missed_5_9 = 0
        missed_2_4 = 0
        missed_2_7 = 0
        missed_5_4_1 = 0
        missed_5_4 = 0
        missed_5_1 = 0
        missed_5_2 = 0
        missed_5_5 = 0
        missed_5_6 = 0
        missed_5_6_1 = 0
        missed_5_7 = 0
        missed_2_8 = 0
        missed_2_9 = 0
        missed_2_6 = 0
        missed_2_10 = 0

        handled_5_3 = 0
        handled_5_8 = 0
        handled_5_9 = 0
        handled_2_4 = 0
        handled_2_7 = 0
        handled_5_4_1 = 0
        handled_5_4 = 0
        handled_5_1 = 0
        handled_5_2 = 0
        handled_5_5 = 0
        handled_5_6 = 0
        handled_5_6_1 = 0
        handled_5_7 = 0
        handled_2_8 = 0
        handled_2_9 = 0
        handled_2_6 = 0
        handled_2_10 = 0

        question_5_3 = Question.objects.filter(section__survey_id=3, question_code='5.3').first()
        question_5_8 = Question.objects.filter(section__survey_id=3, question_code='5.8').first()
        question_5_9 = Question.objects.filter(section__survey_id=3, question_code='5.9').first()
        question_5_4_1 = Question.objects.filter(section__survey_id=3, question_code='5.4.1').first()
        question_5_4 = Question.objects.filter(section__survey_id=3, question_code='5.4').first()
        question_5_1 = Question.objects.filter(section__survey_id=3, question_code='5.1').first()
        question_5_2 = Question.objects.filter(section__survey_id=3, question_code='5.2').first()
        question_5_5 = Question.objects.filter(section__survey_id=3, question_code='5.5').first()
        question_5_6 = Question.objects.filter(section__survey_id=3, question_code='5.6').first()
        question_5_6_1 = Question.objects.filter(section__survey_id=3, question_code='5.6.1').first()
        question_5_7 = Question.objects.filter(section__survey_id=3, question_code='5.7').first()

        question_2_4 = Question.objects.filter(section__survey_id=3, question_code='2.4').first()
        question_2_7 = Question.objects.filter(section__survey_id=3, question_code='2.7').first()
        question_2_8 = Question.objects.filter(section__survey_id=3, question_code='2.8').first()
        question_2_9 = Question.objects.filter(section__survey_id=3, question_code='2.9').first()
        question_2_6 = Question.objects.filter(section__survey_id=3, question_code='2.6').first()
        question_2_10 = Question.objects.filter(section__survey_id=3, question_code='2.10').first()

        section_5 = question_5_8.section
        section_2 = question_2_4.section

        probable_answer_2_4 = Answer.objects.filter(question_id=question_2_4.pk, text__in=[
            "Never attended school", "Do not know"])
        probable_answer_2_8 = Answer.objects.filter(question_id=question_2_8.pk, text__in=[
            "No"])
        probable_answer_2_9 = Answer.objects.filter(question_id=question_2_9.pk, text__in=[
            "No"])
        probable_answer_2_10 = Answer.objects.filter(question_id=question_2_10.pk, text__in=[
            "No"])
        probable_answer_2_6 = Answer.objects.filter(question_id=question_2_6.pk, text__in=[
            "Hotel/Tea Shop/furniture /grocery worker", "Construction worker", "Beggar", "Hawker/Vendor",
            "Transport worker", "Small Businessman",
            "Skilled Worker (plumber, electrician, garments & sweater factory, mills, mechanics and so on)",
            "Service (govt, semi govt and autonomous)", "Service (NGO/Private)", "Unemployed", "Handloom/handicrafts"])
        no_answer_2_7 = Answer.objects.filter(question_id=question_2_7.pk, text='No').first()
        probable_answer_5_3 = Answer.objects.filter(question_id=question_5_3.pk, text__in=[
            "Rented, on government land"])
        probable_answer_5_4 = Answer.objects.filter(question_id=question_5_4.pk, text__in=[
            "Pit latrine with slab"])
        probable_answer_5_5 = Answer.objects.filter(question_id=question_5_5.pk, text__in=[
            "Liquid Petroleum Gas (LPG)", "Natural gas", "Kerosene"])
        probable_answer_5_1 = Answer.objects.filter(question_id=question_5_1.pk, text__in=[
            "Yes"])
        probable_answer_5_2 = Answer.objects.filter(question_id=question_5_2.pk, text__in=[
            "Cement"])
        probable_answer_5_6 = Answer.objects.filter(question_id=question_5_6.pk, text__in=[
            "Piped into dwelling", "Tubewell/borehole"])
        probable_answer_5_7 = Answer.objects.filter(question_id=question_5_7.pk, text__in=[
            "Piped into dwelling"])
        probable_answer_5_6_1 = Answer.objects.filter(question_id=question_5_6_1.pk, text__in=[
            "On Premise"])
        probable_answer_5_8 = Answer.objects.filter(question_id=question_5_8.pk, text__in=[
            "Radio", "Functional refrigerator", "Smart/ Led TV", "Smart mobile phone", "Bicycle", "Motorbike/Scooter"])
        no_answer_5_9 = Answer.objects.filter(question_id=question_5_9.pk, text='No').first()
        no_answer_5_4_1 = Answer.objects.filter(question_id=question_5_4_1.pk, text='No').first()

        options_2_4 = [x for x in probable_answer_2_4]
        options_2_8 = [x for x in probable_answer_2_8]
        options_2_9 = [x for x in probable_answer_2_9]
        options_2_10 = [x for x in probable_answer_2_10]
        options_2_6 = [x for x in probable_answer_2_6]
        options_2_7 = [no_answer_2_7]
        options_5_3 = [x for x in probable_answer_5_3]
        options_5_9 = [no_answer_5_9]
        options_5_4_1 = [no_answer_5_4_1]
        options_5_1 = [x for x in probable_answer_5_1]
        options_5_8 = [x for x in probable_answer_5_8]
        options_5_4 = [x for x in probable_answer_5_4]
        options_5_2 = [x for x in probable_answer_5_2]
        options_5_5 = [x for x in probable_answer_5_5]
        options_5_6 = [x for x in probable_answer_5_6]
        options_5_6_1 = [x for x in probable_answer_5_6_1]
        options_5_7 = [x for x in probable_answer_5_7]

        for response in pg_member_survey_responses:
            has_2_4 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='2.4').first()
            has_2_8 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='2.8').first()
            has_2_9 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='2.9').first()
            has_2_10 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                       question__question_code='2.10').first()
            has_2_7 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='2.7').first()
            has_2_6 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='2.6').first()
            has_5_3 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.3').first()
            has_5_8 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.8').first()
            has_5_9 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.9').first()
            has_5_4_1 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                        question__question_code='5.4.1').first()
            has_5_4 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.4').first()
            has_5_1 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.1').first()
            has_5_2 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.2').first()
            has_5_5 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.5').first()
            has_5_6 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.6').first()
            has_5_6_1 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                        question__question_code='5.6.1').first()
            has_5_7 = QuestionResponse.objects.filter(section_response__survey_response_id=response.pk,
                                                      question__question_code='5.7').first()

            total_checked += 1
            if not has_2_4:
                missed_2_4 += 1
                choosen_answer = random.choice(options_2_4)
                section_response = SectionResponse.objects.filter(
                    section_id=section_2.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_2_4, answer=choosen_answer,
                    question_text=question_2_4.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_2_4 += 1

            if not has_2_8:
                missed_2_8 += 1
                choosen_answer = random.choice(options_2_8)
                section_response = SectionResponse.objects.filter(
                    section_id=section_2.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_2_8, answer=choosen_answer,
                    question_text=question_2_8.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_2_8 += 1

            if not has_2_9:
                missed_2_9 += 1
                choosen_answer = random.choice(options_2_9)
                section_response = SectionResponse.objects.filter(
                    section_id=section_2.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_2_9, answer=choosen_answer,
                    question_text=question_2_9.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_2_9 += 1

            if not has_2_6:
                missed_2_6 += 1
                choosen_answer = random.choice(options_2_6)
                section_response = SectionResponse.objects.filter(
                    section_id=section_2.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_2_6, answer=choosen_answer,
                    question_text=question_2_6.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_2_6 += 1

            if not has_2_10:
                missed_2_10 += 1
                choosen_answer = random.choice(options_2_10)
                section_response = SectionResponse.objects.filter(
                    section_id=section_2.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_2_10, answer=choosen_answer,
                    question_text=question_2_10.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_2_10 += 1

            if not has_2_7:
                missed_2_7 += 1
                choosen_answer = random.choice(options_2_7)
                section_response = SectionResponse.objects.filter(
                    section_id=section_2.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_2_7, answer=choosen_answer,
                    question_text=question_2_7.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_2_7 += 1

            if not has_5_8:
                missed_5_8 += 1
                choosen_answer = random.choice(options_5_8)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    section_response = SectionResponse(
                        survey_response=response, section=section_5
                    )
                    section_response.save()
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_8, answer=choosen_answer,
                    question_text=question_5_8.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_8 += 1

            if not has_5_9:
                missed_5_9 += 1
                choosen_answer = random.choice(options_5_9)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_9, answer=choosen_answer,
                    question_text=question_5_9.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_9 += 1

            if not has_5_3:
                missed_5_3 += 1
                choosen_answer = random.choice(options_5_3)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_3, answer=choosen_answer,
                    question_text=question_5_3.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_3 += 1

            if not has_5_4_1:
                missed_5_4_1 += 1
                choosen_answer = random.choice(options_5_4_1)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_4_1, answer=choosen_answer,
                    question_text=question_5_4_1.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_4_1 += 1

            if not has_5_4:
                missed_5_4 += 1
                choosen_answer = random.choice(options_5_4)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_4, answer=choosen_answer,
                    question_text=question_5_4.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_4 += 1

            if not has_5_1:
                missed_5_1 += 1
                choosen_answer = random.choice(options_5_1)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_1, answer=choosen_answer,
                    question_text=question_5_1.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_1 += 1

            if not has_5_2:
                missed_5_2 += 1
                choosen_answer = random.choice(options_5_2)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_2, answer=choosen_answer,
                    question_text=question_5_2.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_2 += 1

            if not has_5_5:
                missed_5_5 += 1
                choosen_answer = random.choice(options_5_5)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_5, answer=choosen_answer,
                    question_text=question_5_5.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_5 += 1

            if not has_5_6:
                missed_5_6 += 1
                choosen_answer = random.choice(options_5_6)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_6, answer=choosen_answer,
                    question_text=question_5_6.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_6 += 1

            if not has_5_6_1:
                missed_5_6_1 += 1
                choosen_answer = random.choice(options_5_6_1)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_6_1, answer=choosen_answer,
                    question_text=question_5_6_1.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_6_1 += 1

            if not has_5_7:
                missed_5_7 += 1
                choosen_answer = random.choice(options_5_7)
                section_response = SectionResponse.objects.filter(
                    section_id=section_5.pk, survey_response_id=response.pk).first()
                if section_response is None:
                    print("Cannot find section response")
                    continue
                qr = QuestionResponse(
                    section_response=section_response, question=question_5_7, answer=choosen_answer,
                    question_text=question_5_7.text, answer_text=choosen_answer.text
                )
                qr.save()
                print("Choosen: {}".format(qr.answer_text))
                handled_5_7 += 1

            print(
                "Total checked: {}, 2.4: {}/{}, 2.7: {}/{}, 2.6: {}/{},  2.8: {}/{}, 2.9: {}/{}, 2.10: {}/{}, 5.1: {}/{}, 5.2: {}/{}, "
                "5.3: {}/{}, 5.4: {}/{}, 5.4.1: {}/{}, 5.5: {}/{}, 5.6: {}/{}, 5.6.1: {}/{}, 5.7: {}/{}, 5.8: {}/{}, 5.9: {}/{}".format(
                    total_checked,
                    handled_2_4, missed_2_4,
                    handled_2_7, missed_2_7,
                    handled_2_6, missed_2_6,
                    handled_2_8, missed_2_8,
                    handled_2_9, missed_2_9,
                    handled_2_10, missed_2_10,
                    handled_5_1, missed_5_1,
                    handled_5_2, missed_5_2,
                    handled_5_3, missed_5_3,
                    handled_5_4, missed_5_4,
                    handled_5_4_1, missed_5_4_1,
                    handled_5_5, missed_5_5,
                    handled_5_6, missed_5_6,
                    handled_5_6_1, missed_5_6_1,
                    handled_5_7, missed_5_7,
                    handled_5_8, missed_5_8,
                    handled_5_9, missed_5_9))
