from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.renderers import BrowsableAPIRenderer

from blackwidow.core.api.athorization.is_authorized import IsAuthorized
from blackwidow.core.api.athorization.token_authentication import BWTokenAuthentication
from blackwidow.core.api.mixins.viewsetmixin.approve_view_set import GenericApiApproveViewSetMixin
from blackwidow.core.api.mixins.viewsetmixin.mutation_view_set import GenericApiMutableViewSetMixin
from blackwidow.core.api.mixins.viewsetmixin.reject_view_set import GenericApiRejectViewSetMixin
from blackwidow.core.api.renderers.generic_renderer import GenericJsonRenderer
from blackwidow.core.mixins.viewmixin.protected_queryset_mixin import ProtectedQuerySetMixin
from blackwidow.core.models.log.api_call_log import ApiCallLog
from blackwidow.engine.enums.restricted_user_role_enum import RESTRICTED_USER_ROLE_NAME_ENUM
from blackwidow.engine.exceptions.exceptions import BWException

__author__ = 'Mahmud'


class GenericApiViewSetMixin(ProtectedQuerySetMixin, GenericApiMutableViewSetMixin, GenericApiApproveViewSetMixin,
                             GenericApiRejectViewSetMixin, viewsets.ModelViewSet):
    authentication_classes = (BWTokenAuthentication,)
    permission_classes = (IsAuthorized,)
    renderer_classes = (GenericJsonRenderer, BrowsableAPIRenderer)
    parser_classes = (MultiPartParser, FormParser, JSONParser,)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        log = ApiCallLog.log(request=request, log_time=True)
        if log:
            self._api_log = log
        return super(GenericApiViewSetMixin, self).dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        _api_log = None
        if hasattr(self, '_api_log'):
            _api_log = self._api_log
        log = ApiCallLog.log(request=request, response=response, log_instance=_api_log, log_time=False)
        if log:
            self._api_log = log
        return super(GenericApiViewSetMixin, self).finalize_response(request, response, *args, **kwargs)

    def metadata(self, request):
        ret = super(GenericApiViewSetMixin, self).metadata(request)
        return ret

    def create(self, request, *args, **kwargs):
        user_role = request.c_user.role

        if user_role.name in RESTRICTED_USER_ROLE_NAME_ENUM:
            raise BWException('Permission Denied')

        _api_log = None
        if hasattr(self, '_api_log'):
            _api_log = self._api_log
        log = ApiCallLog.log(request=request, log_instance=_api_log)
        if log:
            self._api_log = log
        return super(GenericApiViewSetMixin, self).create(
            request, *args, **kwargs
        )

    def update(self, request, *args, partial=True, **kwargs):
        user_role = request.c_user.role

        if user_role.name in RESTRICTED_USER_ROLE_NAME_ENUM:
            raise BWException('Permission Denied')

        _api_log = None
        if hasattr(self, '_api_log'):
            _api_log = self._api_log
        log = ApiCallLog.log(request=request, log_instance=_api_log)
        if log:
            self._api_log = log
        return super(GenericApiViewSetMixin, self).update(request, *args, partial=partial, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user_role = request.c_user.role

        if user_role.name in RESTRICTED_USER_ROLE_NAME_ENUM:
            raise BWException('Permission Denied')

        return super(GenericApiViewSetMixin, self).partial_update(request, *args, **kwargs)

    def options(self, request, *args, **kwargs):
        return super(GenericApiViewSetMixin, self).options(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # return super(GenericApiViewSetMixin, self).destroy(request, *args, **kwargs)
        raise BWException("Delete not allowed.")

    def list(self, request, *args, **kwargs):
        response = super(GenericApiViewSetMixin, self).list(request, *args, **kwargs)
        return response

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = super().get_api_queryset(queryset=queryset, **kwargs)
        return queryset


class GenericApiReadOnlyViewSetMixin(ProtectedQuerySetMixin, viewsets.ReadOnlyModelViewSet):
    authentication_classes = (BWTokenAuthentication,)
    permission_classes = (IsAuthorized,)
    renderer_classes = (GenericJsonRenderer, BrowsableAPIRenderer)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(GenericApiReadOnlyViewSetMixin, self).dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        ApiCallLog.log(request=request, response=response)
        return super(GenericApiReadOnlyViewSetMixin, self).finalize_response(request, response, *args, **kwargs)
