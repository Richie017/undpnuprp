from collections import OrderedDict

from django.db import models
from django.db.models.query_utils import Q
from modeltranslation.translator import TranslationOptions

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.constants.cache_constants import SITE_NAME_AS_KEY, ONE_MONTH_TIMEOUT
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'Tareq'


@decorate(save_audit_log, is_object_context, expose_api('section'),
          route(route='section', group='Member Registration', module=ModuleEnum.Administration,
                display_name='Section', group_order=2, item_order=2, hide=True))
class Section(OrganizationDomainEntity):
    survey = models.ForeignKey('survey.Survey')
    parent = models.ForeignKey('survey.Section', null=True)
    name = models.CharField(max_length=1024)
    order = models.IntegerField(default=0)

    @classmethod
    def get_cached_survey_by_section_id(cls, section_id):
        cache_key = SITE_NAME_AS_KEY + '_section_survey_' + str(section_id)
        survey = CacheManager.get_from_cache_by_key(key=cache_key)
        if survey is None:
            section = cls.objects.prefetch_related('survey').get(pk=section_id)
            survey = section.survey
            CacheManager.set_cache_element_by_key(key=cache_key, value=survey, timeout=ONE_MONTH_TIMEOUT)
        return survey

    class Meta:
        app_label = 'survey'

    @classmethod
    def table_columns(cls):
        return 'name', 'name_bd', 'survey', 'date_created', 'last_updated'

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
        details['name (Bangla)'] = self.name_bd
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
                related_model='survey.Question',
                queryset_filter=Q(**{'section_id': self.pk})
            )
        ]

    @classmethod
    def get_serializer(cls):
        _ODESerializer = OrganizationDomainEntity.get_serializer()

        class SectionSerializer(_ODESerializer):
            class Meta:
                model = cls
                fields = 'id', 'code', 'name', 'name_bd', 'survey', 'order', 'last_updated'

        return SectionSerializer

    @classmethod
    def get_translator_options(cls):
        class DETranslationOptions(TranslationOptions):
            fields = ('name',)

        return DETranslationOptions
