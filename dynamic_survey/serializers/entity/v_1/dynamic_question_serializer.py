from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from rest_framework import serializers

from dynamic_survey.models import DynamicQuestion


class DynamicQuestionSerializer(OrganizationDomainEntity.get_serializer()):
    survey = serializers.SerializerMethodField()

    def get_survey(self, obj):
        return obj.section.survey_id

    class Meta:
        model = DynamicQuestion
        fields = (
            'id', 'survey', 'question_code', 'question_type', 'text', 'text_bn', 'section', 'order', 'repeat_time',
            'is_required', 'constraint', 'constraint_message', 'minimum_image_number', 'default', 'hint', 'instruction',
            'translated_instruction', 'dependency_string', 'parent', 'date_created', 'last_updated',
        )
        read_only_fields = (
            'id', 'survey', 'question_code', 'question_type', 'text', 'text_bn', 'section', 'order', 'repeat_time',
            'is_required', 'constraint', 'constraint_message', 'minimum_image_number', 'default', 'hint',
            'translated_instruction', 'dependency_string', 'parent', 'date_created', 'last_updated',

        )
