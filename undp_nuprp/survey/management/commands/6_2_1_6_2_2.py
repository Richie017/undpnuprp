from django.core.management import BaseCommand
from django.db import transaction

from blackwidow.engine.extensions import Clock
from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models import Question, Answer


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            q_6_3 = Question.objects.filter(question_code='6.3').first()
            q_6_3_order = q_6_3.order

            update_orders = []
            current_timestamp = Clock.timestamp()
            for q in Question.objects.filter(order__gte=q_6_3_order):
                q.order += 2
                q.last_updated = current_timestamp
                update_orders.append(q)
                current_timestamp += 1
            Question.objects.bulk_update(update_orders, batch_size=200)

            q1 = Question(
                section_id=q_6_3.section_id,
                parent=q_6_3.parent,
                text='Is s/he attending school now?',
                text_bd='সে কি এখনো স্কুলে পড়াশোনা করে?',
                group=q_6_3.group,
                order=q_6_3_order,
                question_code='6.2.1',
                question_type=QuestionTypeEnum.SingleSelectInput.value
            )
            q1.save()

            q2 = Question(
                section_id=q_6_3.section_id,
                parent=q_6_3.parent,
                text='In which class?',
                text_bd='কোন ক্লাসে?',
                group=q_6_3.group,
                order=q_6_3_order + 1,
                question_code='6.2.2',
                question_type=QuestionTypeEnum.SingleSelectInput.value
            )
            q2.save()

            q_6_2 = Question.objects.filter(question_code='6.2').first()
            for ans in q_6_2.answers.all():
                ans.next_question = q1
                ans.save()

            a = q_6_3.answers.order_by('order').first()
            a_order = a.order
            answers = Answer.objects.filter(order__gte=a_order).order_by('order')
            update_orders = []
            for ans in answers:
                ans.order += 12
                ans.last_updated = current_timestamp
                update_orders.append(ans)
                current_timestamp += 1
            Answer.objects.bulk_update(update_orders, batch_size=200)

            a1_1 = Answer(
                question_id=q1.id,
                next_question_id=q2.id,
                text='Yes',
                text_bd='হ্যাঁ',
                order=a_order,
                answer_type=AnswerTypeEnum.SingleSelectInput.value,
                answer_code='6.2.1.1'
            )
            a1_1.save()

            a1_2 = Answer(
                question_id=q1.id,
                next_question_id=q_6_3.id,
                text='No',
                text_bd='না',
                order=a_order + 1,
                answer_type=AnswerTypeEnum.SingleSelectInput.value,
                answer_code='6.2.1.2'
            )
            a1_2.save()

            answers = [('Class 10', '১০ম শ্রেনী'),
                       ('Class 9', '৯ম শ্রেনী'),
                       ('Class 8', '৮ম শ্রেনী'),
                       ('Class 7', '৭ম শ্রেনী'),
                       ('Class 6', '৬ষ্ঠ শ্রেনী'),
                       ('Class 5', '৫ম শ্রেনী'),
                       ('Class 4', '৪র্থ শ্রেনী'),
                       ('Class 3', '৩য় শ্রেনী'),
                       ('Class 2', '২য় শ্রেনী'),
                       ('Class 1', '১ম শ্রেনী')]

            code = 1
            count = 2
            for ans in answers:
                answer = Answer(
                    question_id=q2.id,
                    next_question_id=q_6_3.id,
                    text=ans[0],
                    text_bd=ans[1],
                    order=a_order + count,
                    answer_type=AnswerTypeEnum.SingleSelectInput.value,
                    answer_code='6.2.2.' + str(code)
                )
                code += 1
                count += 1
                answer.save()
