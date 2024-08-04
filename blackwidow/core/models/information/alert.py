from django.db import models
from django.db.models.query_utils import Q

from blackwidow.core.models.information.alert_group import AlertGroup
from blackwidow.core.models.information.information_object import InformationObject
from blackwidow.engine.decorators.route_partial_routes import is_profile_content
from blackwidow.engine.decorators.utility import decorate

__author__ = 'Mahmud'

@decorate(is_profile_content)
class Alert(InformationObject):
    group = models.ForeignKey(AlertGroup, null=True, default=None, on_delete=models.SET_NULL)
    @classmethod
    def get_queryset(cls, queryset=None, user=None, profile_filter=False, **kwargs):
        if profile_filter:
            # _q = queryset.filter(is_active=True, recipient_roles__in=[user.role.pk])
            # _q |= queryset.filter(is_active=True, recipient_users__in=[user.pk]).exclude(is_active=True, recipient_roles__in=[user.role.pk])
            _query = Q(is_active=True, recipient_roles__in=[user.role.pk]) | Q(is_active=True, recipient_users__in=[user.pk])
            return queryset.filter(_query)
        return queryset

    class Meta:
        proxy = False