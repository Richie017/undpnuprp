from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

from dynamic_survey.models.entity.dynamic_section import DynamicSection


class DynamicSectionSerializer(OrganizationDomainEntity.get_serializer()):
    class Meta:
        model = DynamicSection
        fields = 'id', 'name', 'name_bn', 'survey', 'order', 'date_created', 'last_updated'
        read_only_fields = 'id', 'name', 'name_bn', 'survey', 'order', 'date_created', 'last_updated'
