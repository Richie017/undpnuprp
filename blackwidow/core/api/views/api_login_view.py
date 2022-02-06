from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response

from blackwidow.core.api.athorization.imei_authentication import BWIMEIAuthentication
from blackwidow.core.api.serializers.auth_token_serializer import BWAuthTokenSerializer
from blackwidow.core.models.users.user import ConsoleUser

__author__ = 'Mahmud'


class ApiLoginView(ObtainAuthToken):
    serializer_class = BWAuthTokenSerializer

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            users = ConsoleUser.objects.filter(user=serializer.validated_data['user'], is_deleted=False, is_active=True)
            if users.exists():
                user = users[0]
                user.device_id = serializer.validated_data['device_id']
                with transaction.atomic():
                    user.save()
                    token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])
                    response = {
                        'token': token.key,
                        'success': True,
                        "auth_info": {
                            "role_id": user.role.pk,
                            "role_name": user.role.name,
                            "user_type": user.type
                        }
                    }
                    request.c_user = user
                    # check for imei authentication
                    try:
                        BWIMEIAuthentication.perform_imei_authentication(request)
                    except Exception as e:
                        return Response({'message': e.message, 'success': False},
                                        status=status.HTTP_401_UNAUTHORIZED)

                    return Response(response)
            else:
                return Response({'message': 'Your account has been disabled.', 'success': False},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Cannot login with provided credentials.', 'success': False},
                        status=status.HTTP_400_BAD_REQUEST)
