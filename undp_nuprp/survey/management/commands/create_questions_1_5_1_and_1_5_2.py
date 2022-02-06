from django.core.management import BaseCommand
from django.db import transaction

from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models import Question, Answer


class Command(BaseCommand):
    def handle(self, *args, **options):
        # THIS COMMAND IS DEPRECATED! DO NOT RUN IT
        with transaction.atomic():
            parent_ = Question.objects.filter(question_code='1.5').first()
            next_ = Question.objects.filter(question_code='1.6').first()

            questions = Question.objects.filter(order__gt=parent_.order).order_by('order')
            update_orders = []
            for q in questions:
                q.order += 2
                update_orders.append(q)
            Question.objects.bulk_update(update_orders, batch_size=200)

            q1 = Question(
                section_id=parent_.section_id,
                parent_id=parent_.id,
                text='Is s/he attending school now?',
                text_bd='সে কি এখনো স্কুলে পড়াশোনা করে?',
                order=parent_.order + 1,
                question_code='1.5.1',
                question_type=QuestionTypeEnum.SingleSelectInput.value
            )
            q1.save()

            q2 = Question(
                section_id=parent_.section_id,
                parent_id=parent_.id,
                text='In which class?',
                text_bd='কোন ক্লাসে?',
                order=parent_.order + 2,
                question_code='1.5.2',
                question_type=QuestionTypeEnum.SingleSelectInput.value
            )
            q2.save()

            update_new_questions = []
            for pa in parent_.answers.all():
                pa.next_question_id = q1.id
                update_new_questions.append(pa)
            Question.objects.bulk_update(update_new_questions, batch_size=200)

            a = parent_.answers.last()
            answers = Answer.objects.filter(order__gt=a.order).order_by('order')
            update_orders = []
            for ans in answers:
                ans.order += 3
                update_orders.append(ans)
            Answer.objects.bulk_update(update_orders, batch_size=200)

            a1_1 = Answer(
                question_id=q1.id,
                next_question_id=q2.id,
                text='Yes',
                text_bd='হ্যাঁ',
                order=a.order + 1,
                answer_type=AnswerTypeEnum.SingleSelectInput.value,
                answer_code='1.5.1.1'
            )
            a1_1.save()

            a1_2 = Answer(
                question_id=q1.id,
                next_question_id=next_.id,
                text='No',
                text_bd='না',
                order=a.order + 2,
                answer_type=AnswerTypeEnum.SingleSelectInput.value,
                answer_code='1.5.1.2'
            )
            a1_2.save()

            a2 = Answer(
                question_id=q2.id,
                next_question_id=next_.id,
                order=a.order + 3,
                answer_type=AnswerTypeEnum.TextInput.value,
                answer_code='1.5.2.1'
            )
            a2.save()
