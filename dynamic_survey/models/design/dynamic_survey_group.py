from django.db import models

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate, save_audit_log

__author__ = 'Razon'


@decorate(save_audit_log, expose_api('dynamic-survey-group'), )
class DynamicSurveyGroup(OrganizationDomainEntity):
    group_name = models.CharField(max_length=1024, blank=True, null=True, default="")
    total_versions = models.IntegerField(default=1)
    publish_flag = models.BooleanField(default=False)

    @classmethod
    def get_serializer(cls):
        from dynamic_survey.serializers.design.v_1.dynamic_survey_group_serializer import DynamicSurveyGroupSerializer
        return DynamicSurveyGroupSerializer

    class Meta:
        app_label = 'dynamic_survey'
