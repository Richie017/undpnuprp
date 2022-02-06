from django.db.models.query_utils import Q

from blackwidow.core.models.information.information_object import InformationObject
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Mahmud'


# @decorate(is_profile_content, is_object_context, expose_api('notifications'), save_audit_log,
#           route(route='notifications', display_name='Notifications', group='News & Notifications',
#                 module=ModuleEnum.Alert),
#           partial_route(relation='normal', models=[Role, ConsoleUser]))
class Notification(InformationObject):
    @classmethod
    def get_queryset(cls, queryset=None, user=None, profile_filter=False, **kwargs):
        if profile_filter:
            _query = Q(is_active=True, recipient_roles__in=[user.role.pk]) | Q(is_active=True,
                                                                               recipient_users__in=[user.pk])
            return queryset.filter(_query)
        return queryset

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Delete]

    @classmethod
    def get_serializer(cls):
        InformationObjectSerializer = InformationObject.get_serializer()

        class NotificationSerializer(InformationObjectSerializer):
            class Meta:
                model = cls
                fields = ('id', 'name', 'details', 'start_time', 'end_time', 'last_updated')

        return NotificationSerializer

    class Meta:
        proxy = False
