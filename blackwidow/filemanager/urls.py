from django.conf.urls import url

from blackwidow.filemanager.views.fileuploader_view import FileUploaderView
from blackwidow.filemanager.views.secure_download_view import SecureFileDownloadView

__author__ = "Ziaul Haque"

urlpatterns = [
    url(r'^file-uploader/$', FileUploaderView.as_view(), name='file_uploader'),
    url(r'^document/download/(?P<pk>[0-9]+)/$', SecureFileDownloadView.as_view(),
        name='uploadfileobject_secure_download'),
]
