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


@decorate(save_audit_log, is_object_context, expose_api('dynamic-section'),
          route(route='dynamic-section', group='Dynamic Survey', module=ModuleEnum.Administration,
                display_name='Section', group_order=5, item_order=3, hide=True))
class DynamicSection(OrganizationDomainEntity):
    survey = models.ForeignKey('dynamic_survey.DynamicSurvey', related_name='sections')
    parent = models.ForeignKey('dynamic_survey.DynamicSection', null=True)
    name = models.CharField(max_length=1024)
    name_en = models.CharField(blank=True, max_length=2048, null=True)
    name_bn = models.CharField(blank=True, max_length=2048, null=True)
    order = models.IntegerField(default=0)

    class Meta:
        app_label = 'dynamic_survey'

    @classmethod
    def table_columns(cls, *args, **kwargs):
        return 'name', 'survey', 'date_created', 'last_updated'

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        # details['name (Bangla)'] = self.name_bn
        details['survey'] = self.survey
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        return details

    def details_link_config(self, **kwargs):
        return []

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Question(s)',
                access_key='questions',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='dynamic_survey.DynamicQuestion',
                queryset_filter=Q(**{'section_id': self.pk})
            )
        ]

    @classmethod
    def get_serializer(cls):
        from dynamic_survey.serializers.entity.v_1.dynamic_section_serializer import DynamicSectionSerializer
        return DynamicSectionSerializer

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            fields = ('name',)

        return DETranslationOptions

    @classmethod
    def get_model_api_queryset(cls, queryset=None, **kwargs):
        """
        Sending only the sections of active surveys. That means the published surveys.

        :param queryset: by default gets all the objects of the model as queryset
        :return: returns only active queryset
        """
        queryset = queryset.filter(survey__latest_flag=True)
        return queryset
