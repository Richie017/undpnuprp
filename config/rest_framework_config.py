__author__ = 'Mahmud'

API_LOGIN_URL = '/api/login'

REST_FRAMEWORK = {
    'PAGE_SIZE': 500,
    'PAGINATE_BY': 500,                 # Default to 10
    'PAGINATE_BY_PARAM': 'page_size',  # Allow client to override, using `?page_size=xxx`.
    'MAX_PAGINATE_BY': 500,            # Maximum limit allowed when using `?page_size=xxx`.
    'EXCEPTION_HANDLER': 'blackwidow.core.api.exceptions.exception_handler.BWApiExceptionHandler',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'blackwidow.engine.extensions.bw_pagination.BWPagination',
}