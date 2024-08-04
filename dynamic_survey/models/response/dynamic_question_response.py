from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from django.db import models
from rest_framework import serializers
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate

__author__ = 'Razon'


@decorate(expose_api('dynamic-question-response'), )
class DynamicQuestionResponse(OrganizationDomainEntity):
    section_response = models.ForeignKey('dynamic_survey.DynamicSectionResponse', on_delete=models.CASCADE)
    question = models.ForeignKey('dynamic_survey.DynamicQuestion', on_delete=models.CASCADE)
    answer = models.ForeignKey('dynamic_survey.DynamicAnswer', on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1024, blank=True, null=True, default="")
    answer_text = models.CharField(max_length=2048, blank=True, null=True, default="")
    photo = models.ForeignKey('core.ImageFileObject', null=True, on_delete=models.SET_NULL)
    index = models.IntegerField(default=-1)

    @classmethod
    def get_serializer(cls):
        ode_serializer = OrganizationDomainEntity.get_serializer()

        class QuestionResponseSerializer(ode_serializer):
            from blackwidow.core.models.file.imagefileobject import ImageFileObject
            photo = ImageFileObject.get_serializer()(required=False)
            parent_tsync_id = serializers.SerializerMethodField(required=False)

            def get_parent_tsync_id(self, obj):
                if hasattr(self, "parent_tsync_id"):
                    return self.parent_tsync_id
                else:
                    return ""

            class Meta:
                model = cls
                fields = (
                'id', 'tsync_id', 'parent_tsync_id', 'section_response', 'question', 'answer', 'question_text',
                'answer_text', 'photo', 'index', 'date_created', 'last_updated')

        return QuestionResponseSerializer

    # @MongoDBManager.execute_mongo_transaction
    # def prepare_document_object(self, *args, **kwargs):
    #     obj = QuestionResponseDocument()
    #     obj.db_id = self.pk
    #     obj.question = self.question.prepare_document_object(*args, **kwargs)
    #     obj.answer = self.answer.prepare_document_object(*args, **kwargs)
    #     obj.question_text = self.question_text
    #     obj.question_code = self.question.question_code
    #     obj.answer_text = self.answer_text
    #     obj.index = self.index
    #     return obj

    class Meta:
        app_label = 'dynamic_survey'
