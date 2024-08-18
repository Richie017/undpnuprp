from django import http
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse

from blackwidow.core.managers.contextmanager import ContextManager
from blackwidow.core.models import SessionKey
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.engine.constants.cache_constants import CONSOLE_USER_CACHE, ONE_MONTH_TIMEOUT, ORGANIZATION_CACHE
from blackwidow.engine.encoders.bw_json_encoder import DynamicJsonEncoder
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.managers.cachemanager import CacheManager

__author__ = 'mahmudul'


class ProtectedFormPostMiddleWare(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def is_json_request(self, request):
        """
        check if request type is "json" or not
        :param request:
        :return: if request type is "json" then it return "True" otherwise it return "False"
        """
        if request.GET.get('format', None) == 'json' \
                or request.POST.get('format', None) == 'json':
            return True
        return False

    def has_authkey(self, request):
        """
        check if request has "authkey" attribute or not
        :param request:
        :return: return "True" if request has "authkey" attribute otherwise it return "False"
        """
        if request.GET.get('authkey', None) is not None:
            return True
        if request.POST.get('authkey', None) is not None:
            return True
        return False

    def get_authkey(self, request):
        """
        takes request and return "authkey"
        :param request:
        :return: return "authkey" if request has "authkey" attribute else it return "False"
        """
        if request.GET.get('authkey', None) is not None:
            return request.GET.get('authkey', None)
        if request.POST.get('authkey', None) is not None:
            return request.POST.get('authkey', None)
        return False

    def process_exception(self, request, exception):
        """
        takes request and django exception, then create a log entry into ErrorLog model with exceptions.
        :param request:
        :param exception:
        :return: redirect to "/no-access" or "/error" url
        """
        if hasattr(request, 'c_user'):
            ErrorLog.log(exception, request=request, organization=request.c_user.organization)
        message = str(exception)

        if self.is_json_request(request) \
                or request.is_ajax() \
                or ('CONTENT_TYPE' in request.META and request.META['CONTENT_TYPE'] == 'application/json'):
            encoder = DynamicJsonEncoder()
            return http.HttpResponse(encoder.encode({
                'message': message,
                'success': False
            }), content_type='application/json')

        if exception.__class__ == NotEnoughPermissionException:
            return redirect("/no-access")

        messages.error(request, message)
        if '/error' not in request.META['PATH_INFO']:
            return redirect('/error')

    def get_console_user_from_cache(self, user_id):
        permission_key = CONSOLE_USER_CACHE + str(user_id)
        cached_user = CacheManager.get_from_cache_by_key(permission_key)
        if cached_user is None:
            cached_user = ConsoleUser.objects.prefetch_related('role', 'user').filter(
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

    def process_request(self, request):
        """
        takes request, checks request user is anonymous or not, if not then
        initialize context manager, binding with current user and its organization
        :param request:
        :return:
        """
        if request.META.__contains__('HTTP_ACCEPT_LANGUAGE'):
            del request.META['HTTP_ACCEPT_LANGUAGE']

        if '/error' not in request.META['PATH_INFO']:
            if request.session._session:  # not request.user.is_anonymous(): # User is logged in
                if ~hasattr(request, 'c_user'):
                    try:
                        try:
                            c_user = self.get_console_user_from_cache(
                                user_id=request.session._session['_auth_user_id'])
                        except:
                            if hasattr(request, 'user') and request.user:
                                c_user = self.get_console_user_from_cache(user_id=request.user.id)
                        c_organization = self.get_organization_from_cache(c_user=c_user)
                        ContextManager.initialize_context(request, {'user': c_user, 'org': c_organization})
                    except:
                        logout(request)
                        request.session.flush()
                        if not (request.path.endswith('/login') or request.path.endswith(
                                '/login/') or '/api/' in request.path):
                            return redirect(reverse('bw_login'))
            elif self.is_json_request(request) and self.has_authkey(request):  # legacy support
                authkey = self.get_authkey(request)
                sess_key = SessionKey.objects.filter(ses_key=authkey)[0]
                c_user = sess_key.user
                ContextManager.initialize_context(request, {'user': c_user, 'org': c_user.organization})
