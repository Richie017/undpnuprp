from collections import OrderedDict

from django.db import models
from django.db.models import Q
from modeltranslation.translator import TranslationOptions

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Razon'


@decorate(save_audit_log, is_object_context, expose_api('dynamic-question'),
          route(route='dynamic-question', group='Dynamic Survey', module=ModuleEnum.Administration,
                display_name='Question', group_order=5, item_order=4, hide=True))
class DynamicQuestion(OrganizationDomainEntity):
    section = models.ForeignKey('dynamic_survey.DynamicSection', related_name='questions')
    # Only the first parent is saved but a question may have multiple parents
    parent = models.ForeignKey('dynamic_survey.DynamicQuestion', null=True)
    text = models.CharField(max_length=1024, blank=True)
    text_en = models.CharField(blank=True, max_length=2048, null=True)
    text_bn = models.CharField(blank=True, max_length=2048, null=True)
    order = models.IntegerField(default=0)
    question_type = models.CharField(max_length=64, blank=True, null=True)
    question_code = models.CharField(max_length=32, blank=True, null=True)
    is_required = models.BooleanField(default=True)
    # These are the new fields that has been added by Asif Mahmud
    constraint = models.CharField(max_length=1024, blank=True, null=True, default="")
    constraint_message = models.CharField(max_length=1024, blank=True, null=True, default="")
    default = models.CharField(max_length=1024, blank=True, null=True, default="")
    hint = models.CharField(max_length=1024, blank=True, null=True, default="")
    dependency_string = models.CharField(max_length=2048, blank=True, null=True, default="")
    count_as_a_parent = models.IntegerField(default=0)
    minimum_image_number = models.IntegerField(default=0)
    repeat_time = models.IntegerField(default=-1)
    assigned_code = models.CharField(max_length=63, blank=True)
    instruction = models.TextField(blank=True)
    translated_instruction = models.TextField(blank=True)

    class Meta:
        app_label = 'dynamic_survey'

    @property
    def render_section(self):
        return self.section.name

    @property
    def render_survey(self):
        return self.section.survey

    @property
    def render_question_type(self):
        return self.question_type

    @classmethod
    def prefetch_api_objects(cls):
        return ['section']

    @classmethod
    def table_columns(cls, *args, **kwargs):
        return (
            'question_code', 'text', 'render_question_type', 'render_section', 'render_survey',
            'date_created', 'last_updated', 'constraint', 'constraint_message', 'default', 'hint', 'dependency_string',
        )

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.question_code
        details['text'] = self.text
        details['section'] = self.section
        details['survey'] = self.render_survey
        details['type'] = self.question_type
        details['constraint'] = self.constraint
        details['constraint_message'] = self.constraint_message
        details['default'] = self.default
        details['hint'] = self.hint
        details['dependency_string'] = self.dependency_string
        details['count_as_a_parent'] = self.count_as_a_parent
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)

        return details

    def details_link_config(self, **kwargs):
        return []

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Answer(s)',
                access_key='answers',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='dynamic_survey.DynamicAnswer',
                queryset_filter=Q(**{'question_id': self.pk})
            )
        ]

    @classmethod
    def get_serializer(cls):
        from dynamic_survey.serializers.entity.v_1.dynamic_question_serializer import DynamicQuestionSerializer
        return DynamicQuestionSerializer

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            fields = ('text',)

        return DETranslationOptions

    @classmethod
    def get_model_api_queryset(cls, queryset=None, **kwargs):
        """
        Sending only the questions of active surveys. That means the published surveys.

        :param queryset: by default gets all the objects of the model as queryset
        :return: returns only active queryset
        """
        queryset = queryset.filter(section__survey__latest_flag=True)
        return queryset
