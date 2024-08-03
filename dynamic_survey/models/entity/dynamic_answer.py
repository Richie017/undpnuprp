from collections import OrderedDict

from django.db import models
from modeltranslation.translator import TranslationOptions

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Razon'


@decorate(save_audit_log, is_object_context, expose_api('dynamic-answer'),
          route(route='dynamic-answer', group='Dynamic Survey', module=ModuleEnum.Administration,
                display_name='Answer', group_order=5, item_order=5, hide=True))
class DynamicAnswer(OrganizationDomainEntity):
    question = models.ForeignKey('dynamic_survey.DynamicQuestion', related_name='answers')
    text = models.CharField(max_length=2048, blank=True)
    text_en = models.CharField(blank=True, max_length=2048, null=True)
    text_bn = models.CharField(blank=True, max_length=2048, null=True)
    order = models.IntegerField(default=0)
    answer_type = models.CharField(max_length=64, blank=True, null=True)
    answer_code = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        app_label = 'dynamic_survey'

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
        return self.answer_type

    @classmethod
    def table_columns(cls, *args, **kwargs):
        return (
            'text', 'answer_code', 'render_answer_type', 'render_question', 'render_section',
            'render_survey',
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
        # details['text (Bangla)'] = self.text_bn
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
        from dynamic_survey.serializers.entity.v_1.dynamic_answer_serializer import DynamicAnswerSerializer
        return DynamicAnswerSerializer

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            fields = ('text',)

        return DETranslationOptions

    @classmethod
    def get_model_api_queryset(cls, queryset=None, **kwargs):
        """
        Sending only the answers of active surveys. That means the published surveys.
        We are  also discarding the answers that doesn't have any choice/option. (Like: text, number, phone, etc)
        :param queryset: by default gets all the objects of the model as queryset
        :return: returns only active queryset
        """

        queryset = queryset.filter(question__section__survey__latest_flag=True).exclude(text="")
        return queryset
