from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity

from dynamic_survey.models import DynamicAnswer


class DynamicAnswerSerializer(OrganizationDomainEntity.get_serializer()):
    class Meta:
        model = DynamicAnswer
        fields = ('id', 'question', 'answer_type', 'text', 'text_bn', 'order', 'date_created', 'last_updated',)
        read_only_fields = (
            'id', 'question', 'answer_type', 'text', 'text_bn', 'order', 'date_created', 'last_updated',)
