from blackwidow.core.models.log.error_log import ErrorLog

__author__ = 'Mahmud'

from rest_framework.views import exception_handler


def BWApiExceptionHandler(exc, *args):
    ErrorLog.log(exc)
    response = exception_handler(exc, *args)
    if response is not None:
        response.data['status_code'] = response.status_code

    return response
