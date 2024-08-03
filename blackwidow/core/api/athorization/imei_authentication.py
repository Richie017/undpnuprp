from blackwidow.engine.exceptions import BWException
from blackwidow.core.models.system.device import UserDevice
from django.conf import settings


class BWIMEIAuthentication(object):

    @classmethod
    def perform_imei_authentication(cls, request):
        """
        If IMEI Authentication enabled then this method checks if request user's IMEI number matches with his
        assigned device IMEI number. If not matches then rais BWException
        :param request: Request object
        :return: None
        """
        if not request:
            return

        imei_authentication = False
        if hasattr(settings, 'IMEI_AUTHENTICATION_ENABLED'):
            imei_authentication = settings.IMEI_AUTHENTICATION_ENABLED
        if imei_authentication:
            imei_number = request.META.get('HTTP_IMEI_NUMBER')
            if not imei_number:
                raise BWException('IMEI is not provided.')
            user_device = UserDevice.objects.filter(user=request.c_user).first()
            if not user_device:
                UserDevice.add_user_device(request=request)
            elif user_device.imei_number != imei_number:
                raise BWException('User is not registered with this device.')
