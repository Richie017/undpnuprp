from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from blackwidow.core.api.athorization.is_authorized import IsAuthorized
from blackwidow.core.api.athorization.token_authentication import BWTokenAuthentication
from blackwidow.core.api.renderers.generic_renderer import GenericJsonRenderer
from blackwidow.core.models import ImageFileObject
from blackwidow.core.models.log.api_call_log import ApiCallLog

__author__ = 'Ziaul Haque'


class ApiLegacyImageUploadView(APIView):
    authentication_classes = (BWTokenAuthentication,)
    permission_classes = (IsAuthorized,)
    renderer_classes = (GenericJsonRenderer,)

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        log = ApiCallLog.log(request=request, log_time=True)
        if log:
            self._log_tsync_id = log.tsync_id
        return super(ApiLegacyImageUploadView, self).dispatch(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        _log_tsync_id = None
        if hasattr(self, '_log_tsync_id'):
            _log_tsync_id = self._log_tsync_id
        log = ApiCallLog.log(request=request, response=response, tsync_id=_log_tsync_id, log_time=False)
        if log:
            self._log_tsync_id = log.tsync_id
        return super(ApiLegacyImageUploadView, self).finalize_response(request, response, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        tsync_id = kwargs.get('tsync_id')
        request_body = request.data

        request_body.update({
            'tsync_id': tsync_id
        })

        image_file_object = ImageFileObject.objects.filter(tsync_id=tsync_id).first()
        serializer = ImageFileObject.get_serializer()(
            instance=image_file_object,
            data=request_body,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
