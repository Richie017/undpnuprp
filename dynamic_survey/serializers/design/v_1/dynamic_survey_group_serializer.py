from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

from dynamic_survey.models import DynamicSurveyGroup


class DynamicSurveyGroupSerializer(OrganizationDomainEntity.get_serializer()):
    class Meta:
        model = DynamicSurveyGroup
        fields = 'id', 'group_name', 'total_versions', 'publish_flag', 'date_created', 'last_updated'
