from django.core.management import BaseCommand
from django.db import transaction

from blackwidow.core.models import ErrorLog
from dynamic_survey.models.response.dynamic_question_response import DynamicQuestionResponse
from dynamic_survey.enums.dynamic_survey_question_type_enum import DynamicSurveyQuestionTypeEnum


class Command(BaseCommand):
    en_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    def process_bangla_number(self, bn_day_year):
        bn_digs = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯']
        en_digs = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        result = "".join(x if x not in bn_digs else en_digs[bn_digs.index(x)] for i, x in enumerate(bn_day_year))
        return result

    def process_bangla_month(self, bn_month):
        bn_months = ['জা', 'ফে', 'মা', 'এপ্রি', 'মে', 'জুন', 'জুল', 'আগ', 'সে', 'অক্টো', 'ন', 'ডি']
        for i, x in enumerate(bn_months):
            if x in bn_month:
                return self.en_months[i]
        return bn_month

    def process_bangla_date(self, bn_date):
        date = bn_date
        if '/' in date:
            date = '_/' + date
            date = date.replace('/', ' ')
        splits = date.split()
        if len(splits) > 1:
            date = self.process_bangla_number(splits[1])
            month = self.process_bangla_month(splits[2])
            if month not in self.en_months:
                month = self.process_bangla_number(month)
            else:
                month = str(self.en_months.index(month) + 1)
            year = self.process_bangla_number(splits[3])
            return date + "/" + month + "/" + year
        return bn_date

    def handle(self, *args, **options):
        print('---Starting Execution of Command---')
        try:
            qrs = DynamicQuestionResponse.objects.filter(
                question__question_type=DynamicSurveyQuestionTypeEnum.DateInput.value)
            with transaction.atomic():
                for qr in qrs:
                    qr.answer_text = self.process_bangla_date(qr.answer_text)
                    qr.save()
        except Exception as e:
            ErrorLog.log(exp=e)
        print('---Ending Execution of Command---')
