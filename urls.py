import importlib

import debug_toolbar
from django.conf.urls import url, include
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
    url(r'^api/login', ApiLoginView.as_view()),
    url(r'^api/status', ApiStatusView.as_view()),
    url(r'^api/legacy-image-uploads/(?P<tsync_id>.+)/', ApiLegacyImageUploadView.as_view()),
    url(r'^__debug__/', include(debug_toolbar.urls)),
    # url(r'^silk/', include('silk.urls', namespace='silk')),
]

urlpatterns += [
    url(r'^language/', include('django.conf.urls.i18n')),
]

# ------------------------- menu renderer ----------------------------------------------------------
urlpatterns += [
    url(r'^renderer/menus/$', MenuRendererView.as_view(), name="menu-renderer"),
    url(r'^server-status$', PublicView.as_view(), name="server-status-page"),
]

urlpatterns += static(settings.STATIC_UPLOAD_URL, document_root=settings.STATIC_UPLOAD_ROOT)

# ------------------------- upload directory shortcut url --------------------------------------------

# --------------error 404 --- only for production-------------------

handler404 = ErrorView404.as_view()
