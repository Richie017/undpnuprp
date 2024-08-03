from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from django.db import models

from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate
from dynamic_survey.models.response.dynamic_question_response import DynamicQuestionResponse

__author__ = 'Razon'


@decorate(expose_api('dynamic-section-response'), )
class DynamicSectionResponse(OrganizationDomainEntity):
    survey_response = models.ForeignKey('dynamic_survey.DynamicSurveyResponse')
    section = models.ForeignKey('dynamic_survey.DynamicSection')

    @classmethod
    def get_serializer(cls):
        ODESerializer = OrganizationDomainEntity.get_serializer()

        class SectionResponseSerializer(ODESerializer):
            def __init__(self, *args, fields=None, context=None, **kwargs):
                _data = kwargs.get('data', None)
                if _data and 'questions' in _data:
                    self.questions = _data['questions']
                super().__init__(fields=fields, context=context, *args, **kwargs)

            def create(self, attrs):
                instance = super().create(attrs=attrs)
                if hasattr(self, 'questions'):
                    for question in self.questions:
                        question.update({'section_response': instance.pk})
                        question_serializer = DynamicQuestionResponse.get_serializer()(data=question)
                        question_serializer.is_valid(raise_exception=True)
                        question_serializer.save()
                return instance

            class Meta:
                model = cls
                fields = 'id', 'tsync_id', 'survey_response', 'section', 'date_created', 'last_updated'

        return SectionResponseSerializer

    class Meta:
        app_label = 'dynamic_survey'
