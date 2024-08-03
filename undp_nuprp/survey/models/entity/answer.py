from collections import OrderedDict

from django.db import models
from modeltranslation.translator import TranslationOptions
from rest_framework import serializers

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum

__author__ = 'Tareq'


@decorate(save_audit_log, is_object_context, expose_api('answer'),
          route(route='answer', group='Member Registration', module=ModuleEnum.Administration,
                display_name='Answer', group_order=2, item_order=4, hide=True))
class Answer(OrganizationDomainEntity):
    question = models.ForeignKey('survey.Question', related_name='answers')
    next_question = models.ForeignKey('survey.Question', null=True, related_name='+')
    text = models.CharField(max_length=2048, blank=True)
    order = models.IntegerField(default=0)
    answer_type = models.CharField(max_length=64, blank=True, null=True)
    answer_code = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        app_label = 'survey'

    @property
    def render_question(self):
        return self.question.question_code + '. ' + self.question.text

    @property
    def render_section(self):
        return self.question.section.name

    @property
    def render_survey(self):
        return self.question.section.survey

    @property
    def render_answer_type(self):
        return AnswerTypeEnum.get_answer_type_label(self.answer_type)

    @classmethod
    def table_columns(cls):
        return ('text', 'text_bd', 'render_answer_type', 'render_question', 'render_section', 'render_survey',
                'date_created', 'last_updated')

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.answer_code
        details['text'] = self.text
        details['text (Bangla)'] = self.text_bd
        details['question'] = self.question
        details['next_question'] = self.next_question if self.next_question else 'N/A'
        details['section'] = self.render_section
        details['survey'] = self.render_survey
        details['type'] = self.answer_type
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        return details

    def details_link_config(self, **kwargs):
        return []

    @classmethod
    def get_serializer(cls):
        _ODESerializer = OrganizationDomainEntity.get_serializer()

        class AnswerSerializer(_ODESerializer):
            next_question = serializers.SerializerMethodField()

            def get_next_question(self, obj):
                try:
                    if obj.next_question_id:
                        return obj.next_question_id
                    else:
                        return 0
                except:
                    return 0

            class Meta:
                model = cls
                fields = ('id', 'question', 'answer_type', 'answer_code', 'text', 'text_bd', 'order', 'next_question',
                          'last_updated')

        return AnswerSerializer

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            fields = ('text',)

        return DETranslationOptions
