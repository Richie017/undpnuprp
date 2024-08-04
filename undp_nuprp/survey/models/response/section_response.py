from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from undp_nuprp.survey.models.response.question_response import QuestionResponse

__author__ = 'Tareq'


class SectionResponse(OrganizationDomainEntity):
    survey_response = models.ForeignKey('survey.SurveyResponse', null=True, on_delete=models.SET_NULL)
    section = models.ForeignKey('survey.Section', on_delete=models.CASCADE)

    @classmethod
    def version_enabled_related_fields(cls):
        return ['questionresponse']

    @classmethod
    def get_serializer(cls):
        ODESerializer = OrganizationDomainEntity.get_serializer()

        class SectionResponseSerializer(ODESerializer):
            def __init__(self, *args, fields=None, context=None, **kwargs):
                _data = kwargs['data']
                if 'questions' in _data:
                    self.questions = _data['questions']
                super().__init__(fields=fields, context=context, *args, **kwargs)

            def create(self, attrs):
                instance = super().create(attrs=attrs)
                if hasattr(self, 'questions'):
                    for question in self.questions:
                        question.update({'section_response': instance.pk})
                        question_serializer = QuestionResponse.get_serializer()(data=question)
                        question_serializer.is_valid(raise_exception=True)
                        question_serializer.save()
                return instance

            class Meta:
                model = cls
                fields = 'survey_response', 'section'

        return SectionResponseSerializer

    class Meta:
        app_label = 'survey'
