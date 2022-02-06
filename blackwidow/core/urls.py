from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from rest_framework.routers import DefaultRouter

import settings
from blackwidow.core.api.mixins.viewsetmixin.viewset_mixin import GenericApiViewSetMixin
from blackwidow.core.api.routers.router import CustomRouter
from blackwidow.core.generics.views.activate_view import GenericActivateView
from blackwidow.core.generics.views.advanced_export_view import AdvancedGenericExportView
from blackwidow.core.generics.views.advanced_import_view import AdvancedGenericImportView
from blackwidow.core.generics.views.approval_process_restore_view import GenericApprovalProcessRestoreView
from blackwidow.core.generics.views.approve_view import GenericApproveView
from blackwidow.core.generics.views.bulk_views.reject_view import GenericRejectView
from blackwidow.core.generics.views.create_view import GenericCreateView
from blackwidow.core.generics.views.dashboard_view import GenericDashboardView
from blackwidow.core.generics.views.deactivate_view import GenericDeactivateView
from blackwidow.core.generics.views.delete_view import GenericDeleteView
from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.core.generics.views.download_view import GenericDownloadView
from blackwidow.core.generics.views.edit_view import GenericEditView
from blackwidow.core.generics.views.error_view import GenericErrorView
from blackwidow.core.generics.views.export_view import GenericExportView
from blackwidow.core.generics.views.import_view import GenericImportRunnerView
from blackwidow.core.generics.views.key_info_view import GenericKeyInformationView
from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.generics.views.model_descriptor_view import GenericModelDescriptorView
from blackwidow.core.generics.views.mutation_view import GenericMutationView
from blackwidow.core.generics.views.notification_view import GenericNotificationView
from blackwidow.core.generics.views.object_version_view import GenericVersionActionView
from blackwidow.core.generics.views.partial_views.partial_add_list_view import PartialGenericAddListView
from blackwidow.core.generics.views.partial_views.partial_create_view import PartialGenericCreateView
from blackwidow.core.generics.views.partial_views.partial_delete_view import PartialGenericDeleteView
from blackwidow.core.generics.views.partial_views.partial_edit_view import PartialGenericEditView
from blackwidow.core.generics.views.partial_views.partial_file_upload_view import PartialGenericFileUploadView
from blackwidow.core.generics.views.partial_views.partial_remove_list_view import PartialGenericRemoveListView
from blackwidow.core.generics.views.partial_views.partial_tab_list_view import PartialGenericTabListView
from blackwidow.core.generics.views.printable_views.printable_details_view import GenericPrintableContentView
from blackwidow.core.generics.views.proxy_create_view import GenericProxyCreateView
from blackwidow.core.generics.views.proxy_list_view import GenericProxyListView
from blackwidow.core.generics.views.restore_view import GenericRestoreView
from blackwidow.core.generics.views.route_design_view import GenericRouteDesignView
from blackwidow.core.generics.views.secure_download_view import GenericSecureDownloadView
from blackwidow.core.generics.views.step_back_view import GenericStepBackView
from blackwidow.core.generics.views.tree_view import GenericTreeView
from blackwidow.core.models.information.news import News
from blackwidow.core.models.information.notification import Notification
from blackwidow.core.views import *
from blackwidow.core.views.account.reset_password_view import ResetPasswordRequestView
from blackwidow.core.views.users.consoleuser_reset_password_view import ConsoleUserResetPasswordView
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.menumanager import MenuManager
from config.apps import INSTALLED_APPS

# ------------------------- general routes start ---------------------------------------
# tuple information:
# ==================
# 0 -> Url Type
# 1 -> Route Url Suffix
# 2 -> Success Url Type
# 3 -> Requires Form to be mentioned?
# 4 -> The view class
operations = [(ViewActionEnum.Create, '/create', ViewActionEnum.Manage, True, GenericCreateView, None),
              (ViewActionEnum.Edit, '/edit/(?P<pk>(\d{,}))', ViewActionEnum.Manage, True, GenericEditView, None),
              (ViewActionEnum.Export, '/export', ViewActionEnum.Manage, False, GenericExportView, None),
              (ViewActionEnum.Download, '/download/(?P<pks>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericDownloadView, None),
              (ViewActionEnum.SecureDownload, '/secure-download/(?P<pk>(\d{,}))', ViewActionEnum.Manage, False,
               GenericSecureDownloadView, None),
              (ViewActionEnum.Details, '/details/(?P<pk>(\d{,}))', ViewActionEnum.Details, False, GenericDetailsView,
               None),
              (
                  ViewActionEnum.Delete, '/delete/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
                  GenericDeleteView,
                  None),
              (ViewActionEnum.Restore, '/restore/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericRestoreView, None),
              (ViewActionEnum.Mutate, '/mutate/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericMutationView, None),
              (ViewActionEnum.Approve, '/approve/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericApproveView, None),
              (
                  ViewActionEnum.Reject, '/reject/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
                  GenericRejectView,
                  None),
              (ViewActionEnum.RestoreReject, '/reject-undo/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericApprovalProcessRestoreView, None),
              (ViewActionEnum.StepBack, '/stepback/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericStepBackView, None),
              (ViewActionEnum.Tab, "/tabs/(?P<pk>(\d{,}|\w{,}))/(?P<tab>(\w{,}))", ViewActionEnum.Details, False,
               PartialGenericTabListView, None),
              (ViewActionEnum.Import, '/import', ViewActionEnum.Manage, False, GenericImportRunnerView, None),
              (
                  ViewActionEnum.RunImporter, '/run-importer', ViewActionEnum.Manage, False, GenericImportRunnerView,
                  None),
              (ViewActionEnum.Tree, '/tree', ViewActionEnum.Tree, False, GenericTreeView, None),
              (ViewActionEnum.Print, '/print/(?P<pk>(\d{,}))', ViewActionEnum.Print, False, GenericPrintableContentView,
               None),
              (ViewActionEnum.KeyInfo, '/key-information/(?P<pk>(\d{,}))', ViewActionEnum.KeyInfo, False,
               GenericKeyInformationView, None),
              (ViewActionEnum.Activate, '/activate/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericActivateView, None),
              (ViewActionEnum.Deactivate, '/deactivate/(?P<ids>((\d(\,)*){,}))', ViewActionEnum.Manage, False,
               GenericDeactivateView, None),
              (ViewActionEnum.PartialCreate, '/partial-create/(?P<parent_id>(\d{,}))/(?P<tab>(\w{,}))',
               ViewActionEnum.PartialCreate, True, PartialGenericCreateView, None),
              (ViewActionEnum.PartialFileUpload, '/partial-file-upload/(?P<parent_id>(\d{,}))/(?P<tab>(\w{,}))',
               ViewActionEnum.PartialFileUpload, True, PartialGenericFileUploadView, None),
              (ViewActionEnum.PartialDelete, '/partial-delete/(?P<parent_id>(\d{,}))/(?P<tab>(\w{,}))',
               ViewActionEnum.PartialDelete, False, PartialGenericDeleteView, None),
              (ViewActionEnum.PartialEdit, '/partial-edit/(?P<parent_id>(\d{,}))//(?P<pk>(\d{,}))',
               ViewActionEnum.PartialEdit, True, PartialGenericEditView, None),
              (ViewActionEnum.AdvancedExport, '/advanced-export/$', ViewActionEnum.AdvancedExport, True,
               AdvancedGenericExportView, None),
              (ViewActionEnum.AdvancedImport, '/advanced-import/$', ViewActionEnum.AdvancedImport, True,
               AdvancedGenericImportView, None),
              (ViewActionEnum.PartialBulkAdd, '/bulk-add/(?P<pk>(\d{,}))/(?P<tab>(\w{,}))',
               ViewActionEnum.PartialBulkAdd, False, PartialGenericAddListView, None),
              (ViewActionEnum.PartialBulkRemove, '/bulk-remove/(?P<pk>(\d{,}))/(?P<tab>(\w{,}))',
               ViewActionEnum.PartialBulkRemove, False, PartialGenericRemoveListView, None),
              (ViewActionEnum.RouteDesign, '/route-designs/(?P<pk>(\d{,}))', ViewActionEnum.Manage, True,
               GenericRouteDesignView, None),
              (ViewActionEnum.Manage, '/$', ViewActionEnum.Manage, False, GenericListView, None),

              (ViewActionEnum.ProxyLevel, '/level/(?P<proxy_name>(\w+))/$',
               ViewActionEnum.Manage, False, GenericProxyListView, None),
              (ViewActionEnum.ProxyCreate, '/level/(?P<proxy_name>(\w+))/create/$',
               ViewActionEnum.Manage, True, GenericProxyCreateView, None),
              (ViewActionEnum.ProxyDetails, '/level/(?P<proxy_name>(\w+))/details/(?P<pk>(\d{,}))',
               ViewActionEnum.Details, False, GenericDetailsView,
               None),
              ]

urlpatterns = list()
for _pa in MenuManager.generate_urls(operations):
    urlpatterns += i18n_patterns(
        _pa
    )

urlpatterns += i18n_patterns(
    url(r'^$', HomeView.as_view(), name="bw_home"),
    url(r'^account/login', LoginView.as_view(), name="bw_login"),
    url(r'^account/reset_password_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', PasswordResetConfirmView.as_view(),
        name='bw_reset_password_confirm'),
    url(r'^account/reset_password', ResetPasswordRequestView.as_view(), name="bw_reset_password"),
    url(r'^consoleuser/reset_password/(?P<id>\d+)/', ConsoleUserResetPasswordView.as_view(),
        name="consoleuser_reset_password"),
    url(r'^account/logout', LogoutView.as_view(), name="bw_logout"),
    url(r'^account/register', RegisterView.as_view(), name="bw_registration"),
    # url(r'^account/login', include('allauth.urls')),
    url(r'^no-access', GenericErrorView.as_view(template_name='shared/no-access.html'),
        name="no_access"),
    url(r'^error', GenericErrorView.as_view(template_name='shared/error.html'), name="error"),
    # -------------------- Test purpose --------
    url(r'^inprogress', GenericDashboardView.as_view(), name="coming_soon"),

    # -------------------- Dashboards ---------------------------------#
    url(r'^administration/dashboard', GenericDashboardView.as_view(), name="admin_dashboard"),
    url(r'^execute/dashboard', GenericDashboardView.as_view(), name="execute_dashboard"),
    url(r'^settings/dashboard', GenericDashboardView.as_view(), name="config_dashboard"),
    url(r'^settings', GenericDashboardView.as_view(), name="settings_coming_soon"),
    url(r'^help/dashboard', GenericDashboardView.as_view(), name="help_dashboard"),
    url(r'^help/about', GenericDashboardView.as_view(), name="help_about"),
    url(r'^users/dashboard', GenericDashboardView.as_view(), name="user_dashboard"),
    url(r'^maintenance/dashboard', GenericDashboardView.as_view(), name="maintenance_dashboard"),
    url(r'^kpi/dashboard', GenericDashboardView.as_view(), name="kpi_dashboard"),
    url(r'^communication/dashboard', GenericDashboardView.as_view(), name="communication_dashboard"),
    url(r'^surveys/dashboard', GenericDashboardView.as_view(), name="surveys"),
    url(r'^device-manager/dashboard', GenericDashboardView.as_view(), name="device-manager_dashboard"),
    url(r'^reports/dashboard', GenericDashboardView.as_view(), name="reports_dashboard"),
    url(r'^analysis/dashboard', GenericDashboardView.as_view(), name="analysis_dashboard"),

    # -------------------- Model Descriptor ------------------------ #
    url(r'^diagnostics/model_descriptor/', GenericModelDescriptorView.as_view(), name="model_descriptor"),

    url(r'^_profile/news/count/', GenericNotificationView.as_view(model=News), name='news_count_view'),
    url(r'^_profile/news/', GenericNotificationView.as_view(model=News), name='news_list_view'),
    url(r'^_profile/notifications/count/', GenericNotificationView.as_view(model=Notification),
        name='notification_count_view'),
    url(r'^_profile/notifications/', GenericNotificationView.as_view(model=Notification),
        name='notification_list_view'),

    # -------------------- Object Version Control -------------------- #
    url(
        r'^version-action/(?P<action_type>\w+)/(?P<app_label>\w+)/(?P<model>\w+)/(?P<pk>\d+)/(?P<version_pk>\d+)',
        GenericVersionActionView.as_view(),
        name="restore_version"
    ),
)

# static file urls
urlpatterns += [
    url(r'^static/' + '(.*)$', serve, {
        'document_root': settings.STATIC_ROOT,
    }),
    url(r'^static_media/' + '(.*)$', serve, {
        'document_root': settings.STATIC_ROOT,
    }),
]

# ------------------------- api routes start -------------------------------------------
router = CustomRouter()

all_models = get_models_with_decorator('expose_api', INSTALLED_APPS, include_class=True)
for m in all_models:
    viewset_subclass = type(
        'RunTime_' + m.__name__ + '_ViewSet',
        (GenericApiViewSetMixin,),
        dict(
            model=m,
            serializer_class=m.get_serializer())
    )

    router.register(r'api/' + m._url_prefix, viewset_subclass, base_name=m.__name__)

_d_router = DefaultRouter()
urlpatterns += [url(r'^api$', _d_router.get_api_root_view(), name=_d_router.root_view_name)]
urlpatterns += router.urls
