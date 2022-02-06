from django.core.management import BaseCommand
from django.db import transaction

from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models import Question, Answer


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            a = Answer.objects.filter(question__question_code='6.11')
            a_order = a.first().order + 2
            q = Question.objects.filter(question_code='6.11')
            q_section, q_parent, q_order, q_group = q.first().section_id, q.first().parent_id, q.first().order, \
                q.first().group
            # create question 6.12 and its answers from 3.1
            q_tups = [('6.12', '3.1'), ('6.13', '3.2'), ('6.14', '3.3'), ('6.15', '3.4'), ('6.16', '3.5'),
                      ('6.17', '3.6')]
            count = 1
            for t in q_tups:
                q3 = Question.objects.filter(question_code=t[1]).first()
                q6 = Question(
                    section_id=q_section,
                    parent_id=q_parent,
                    text=q3.text,
                    text_bd=q3.text_bd,
                    order=q_order + count,
                    group=q_group,
                    question_type=QuestionTypeEnum.SingleSelectInput.value,
                    question_code=t[0]
                )
                q6.save()
                count += 1

                a3 = Answer.objects.filter(question__question_code='3.1')
                a_count = 1
                for ans in a3:
                    a6 = Answer(
                        question_id=q6.id,
                        text=ans.text,
                        text_bd=ans.text_bd,
                        order=a_order,
                        answer_type=AnswerTypeEnum.SingleSelectInput.value,
                        answer_code=t[0] + '.' + str(a_count)
                    )
                    a6.save()
                    a_count += 1
                    a_order += 1
