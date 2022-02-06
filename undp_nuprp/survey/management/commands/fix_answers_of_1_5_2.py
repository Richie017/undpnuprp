from django.core.management import BaseCommand
from django.db import transaction

from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum
from undp_nuprp.survey.models import Answer


class Command(BaseCommand):
    def handle(self, *args, **options):
        with transaction.atomic():
            # THIS COMMAND IS DEPRECATED! DO NOT RUN IT
            ans = Answer.objects.filter(answer_code='1.5.2.1').first()
            ans.answer_type = AnswerTypeEnum.SingleSelectInput.value
            ans.text = 'Pre-primary/ Moktab'
            ans.text_bd = 'প্রি -প্রাইমারি/মক্তব'
            ans.save()

            order = ans.order
            new_ans = [('Primary/ Ibtadayee/ JDC', 'প্রাইমারি/ ইবতেদায়ী / জেডিসি'),
                       ('SSC / Dakhil', 'এস এস সি/দাখিল'),
                       ('HSC/ Alim', 'এইচ এস সি/আলিম'),
                       ('University/ Fazil / Kamil', 'বিশ্ববিদ্যালয়/ফাযিল/কামিল'),
                       ('Never attended school', 'কখনো স্কুলে যায়নি'),
                       ('Do not know', 'জানিনা')]

            change_orders = Answer.objects.filter(order__gt=order)
            sz = len(new_ans)
            update_orders = []
            for o in change_orders:
                o.order += sz
                update_orders.append(o)
            Answer.objects.bulk_update(update_orders, batch_size=200)

            count = 0
            for text in new_ans:
                count += 1
                a = Answer(
                    question_id=ans.question_id,
                    next_question_id=ans.next_question_id,
                    text=text[0],
                    text_bd=text[1],
                    order=order + count,
                    answer_type=AnswerTypeEnum.SingleSelectInput.value,
                    answer_code='1.5.2.' + str(count + 1)
                )
                a.save()
