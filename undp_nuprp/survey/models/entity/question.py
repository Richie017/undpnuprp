from collections import OrderedDict

from django.db import models
from django.db.models.query_utils import Q
from modeltranslation.translator import TranslationOptions
from rest_framework import serializers

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum

__author__ = 'Tareq'


@decorate(save_audit_log, is_object_context, expose_api('question'),
          route(route='question', group='Member Registration', module=ModuleEnum.Administration,
                display_name='Question', group_order=2, item_order=3, hide=True))
class Question(OrganizationDomainEntity):
    section = models.ForeignKey('survey.Section')
    parent = models.ForeignKey('survey.Question', null=True)
    text = models.CharField(max_length=1024, blank=True)
    order = models.IntegerField(default=0)
    group = models.CharField(max_length=1024, blank=True)
    question_type = models.CharField(max_length=64, blank=True, null=True)
    question_code = models.CharField(max_length=32, blank=True, null=True)
    is_required = models.BooleanField(default=True)

    class Meta:
        app_label = 'survey'

    @property
    def render_section(self):
        return self.section.name

    @property
    def render_survey(self):
        return self.section.survey

    @property
    def render_question_type(self):
        return QuestionTypeEnum.get_question_type_from_value(self.question_type)

    @classmethod
    def table_columns(cls):
        return ('question_code', 'text', 'text_bd', 'render_question_type', 'render_section', 'render_survey',
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
        details['code'] = self.question_code
        details['text'] = self.text
        details['text (Bangla)'] = self.text_bd
        details['section'] = self.section
        details['survey'] = self.render_survey
        details['type'] = self.question_type
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
                related_model='survey.Answer',
                queryset_filter=Q(**{'question_id': self.pk})
            )
        ]

    @classmethod
    def get_serializer(cls):
        _ODESerializer = OrganizationDomainEntity.get_serializer()

        class QuestionSerializer(_ODESerializer):
            parent = serializers.SerializerMethodField()
            survey = serializers.SerializerMethodField()

            def get_parent(self, obj):
                if obj.parent_id:
                    return obj.parent_id
                return 0

            def get_survey(self, obj):
                from undp_nuprp.survey.models import Section
                try:
                    return Section.get_cached_survey_by_section_id(section_id=obj.section_id).id
                except:
                    return 0

            class Meta:
                model = cls
                fields = ('id', 'question_code', 'question_type', 'text', 'text_bd', 'section', 'survey', 'group',
                          'order', 'parent', 'is_required', 'last_updated')

        return QuestionSerializer

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            fields = ('text',)

        return DETranslationOptions
