"""This module handles the custom authentication for csrf exempt session authentication"""
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Derived from SessionAuthentication, only overrides a `enforce_csrf` method to stop checking for csrf token"""

    def enforce_csrf(self, request):
        """
        Does nothing. Intention is to use all the functionality of SessionAuthentication of DRF. Except
        not to check for any kind of CSRF token.
        :param request: HttpRequest
        :type request: HttpRequest
        :return: None
        :rtype: None
        """
        return  # To not perform the csrf check previously happening
