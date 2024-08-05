import importlib

import debug_toolbar
from django.conf.urls import include
from django.urls import path, re_path
from django.conf.urls.static import static

import settings
from blackwidow.core.api.views.api_legacy_image_upload_view import ApiLegacyImageUploadView
from blackwidow.core.api.views.api_login_view import ApiLoginView
from blackwidow.core.api.views.api_status_view import ApiStatusView
from blackwidow.core.views.error.error_view import ErrorView404
from blackwidow.core.views.menu.menu_renderer_view import MenuRendererView
from blackwidow.core.views.shared.public_view import PublicView
from config.apps import INSTALLED_APPS

urlpatterns = list()

for _app in INSTALLED_APPS:
    try:
        _url_module = importlib.import_module(_app + '.urls')
        _app_urls = getattr(_url_module, 'urlpatterns')
        urlpatterns += _app_urls
    except ImportError as exp:
        pass
# ------------------------- general routes end -----------------------------------------

for _app in INSTALLED_APPS:
    try:
        _url_module = importlib.import_module(_app + '.api.urls')
        _app_urls = getattr(_url_module, 'urlpatterns')
        urlpatterns += _app_urls
    except ImportError as exp:
        pass

urlpatterns += [
    path('api/login', ApiLoginView.as_view()),
    path('api/status', ApiStatusView.as_view()),
    path('api/legacy-image-uploads/<tsync_id>/', ApiLegacyImageUploadView.as_view()),
    path('__debug__/', include(debug_toolbar.urls)),
    path('silk/', include('silk.urls', namespace='silk')),
]

urlpatterns += [
    path('language/', include('django.conf.urls.i18n')),
]

# ------------------------- menu renderer ----------------------------------------------------------
urlpatterns += [
    re_path(r'^renderer/menus/$', MenuRendererView.as_view(), name="menu-renderer"),
    re_path(r'^server-status$', PublicView.as_view(), name="server-status-page"),
]

urlpatterns += static(settings.STATIC_UPLOAD_URL, document_root=settings.STATIC_UPLOAD_ROOT)

# ------------------------- upload directory shortcut url --------------------------------------------

# --------------error 404 --- only for production-------------------

handler404 = ErrorView404.as_view()
