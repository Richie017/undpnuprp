from crequest.middleware import CrequestMiddleware
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import APIException

from blackwidow.core.api.athorization.imei_authentication import BWIMEIAuthentication
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.constants.cache_constants import CONSOLE_USER_CACHE, ONE_MONTH_TIMEOUT, SITE_NAME_AS_KEY, \
    ONE_DAY_TIMEOUT, ORGANIZATION_CACHE
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Mahmud'


class BWTokenAuthentication(TokenAuthentication):
    TOKEN_CACHE_PREFIX = SITE_NAME_AS_KEY + '_token_auth_'

    def attempt_cached_authentication(self, key):
        cache_key = self.TOKEN_CACHE_PREFIX + str(key)
        cached_token = CacheManager.get_from_cache_by_key(key=cache_key)
        if cached_token is None:
            model = self.get_model()
            try:
                token = model.objects.select_related('user').get(
                    key=key)
            except model.DoesNotExist:
                raise exceptions.AuthenticationFailed('Invalid token.')
            if not token.user.is_active:
                raise exceptions.AuthenticationFailed('User ' + str(token.user.username) + ' inactive or deleted.')
            cached_token = (token.user, token)
            CacheManager.set_cache_element_by_key(key=cache_key, value=cached_token, timeout=ONE_DAY_TIMEOUT)
        return cached_token

    def authenticate_credentials(self, key):
        if settings.CACHE_ENABLED:
            return self.attempt_cached_authentication(key=key)

        model = self.get_model()
        try:
            token = model.objects.using(BWDatabaseRouter.get_read_database_name()).select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User ' + str(token.user.username) + ' inactive or deleted.')
        return (token.user, token)

    def get_console_user_from_cache(self, user_id, database):
        permission_key = CONSOLE_USER_CACHE + str(user_id)
        cached_user = CacheManager.get_from_cache_by_key(permission_key)
        if cached_user is None:
            cached_user = ConsoleUser.objects.using(database).prefetch_related('role', 'user').filter(
                user__id=user_id).first()
            CacheManager.set_cache_element_by_key(permission_key, cached_user, ONE_MONTH_TIMEOUT)
        return cached_user

    def get_organization_from_cache(self, c_user):
        permission_key = ORGANIZATION_CACHE + str(c_user.id)
        cached_organization = CacheManager.get_from_cache_by_key(permission_key)
        if cached_organization is None:
            cached_organization = c_user.organization
            CacheManager.set_cache_element_by_key(permission_key, cached_organization, ONE_MONTH_TIMEOUT)
        return cached_organization

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or len(auth) == 0 or auth[0].lower() != b'token':
            return None

        if len(auth) <= 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            auth_user, token = self.authenticate_credentials(auth[1])
            if request.method.lower() == 'get':
                c_user = self.get_console_user_from_cache(user_id=auth_user.id,
                                                          database=BWDatabaseRouter.get_read_database_name())
            else:
                c_user = self.get_console_user_from_cache(user_id=auth_user.id,
                                                          database=BWDatabaseRouter.get_write_database_name())
            request.c_user = c_user
            request.c_organization = self.get_organization_from_cache(c_user=c_user)
            CrequestMiddleware.set_request(request)
        except Exception as exp:
            raise APIException(str(exp))

        try:
            # check for imei_authentication
            BWIMEIAuthentication.perform_imei_authentication(request)
        except Exception as e:
            raise exceptions.AuthenticationFailed(e.message)

        return (auth_user, token)
