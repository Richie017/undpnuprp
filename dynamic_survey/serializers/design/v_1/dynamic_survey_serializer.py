from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from rest_framework import serializers

from dynamic_survey.models.design.dynamic_survey import DynamicSurvey


class DynamicSurveySerializer(OrganizationDomainEntity.get_serializer()):
    survey_group = serializers.SerializerMethodField()

    def get_survey_group(self, obj):
        return obj.survey_id if obj.survey_id else 0

    class Meta:
        model = DynamicSurvey
        fields = 'id', 'name', 'version', 'date_published', 'date_created', 'last_updated', 'survey_group'
        read_only_fields = 'id', 'name', 'version', 'date_published', 'date_created', 'last_updated', 'survey_group'
