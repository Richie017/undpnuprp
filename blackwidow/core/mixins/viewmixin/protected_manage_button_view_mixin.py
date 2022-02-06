from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager

__author__ = 'Mahmud'


class ProtectedManageButtonViewMixin(object):
    def get_manage_buttons(self):
        self.buttons = self.model.get_manage_buttons()
        mname = self.model.get_model_meta('route', 'display_name') if not hasattr(
            self, 'proxy_model_name') else bw_titleize(
            self.proxy_model_name)
        route = self.model.get_model_meta('route', 'route') if not hasattr(
            self, 'proxy_model_name') else (
            self.model.get_model_meta(
                'route', 'route') + '/' + ViewActionEnum.ProxyLevel.value + '/' + self.proxy_model_name)
        if mname is None:
            mname = self.model.__name__.lower()

        m_buttons = list()

        options = self.model.get_model_meta('route', 'options')
        # check for create permission for current model
        if BWPermissionManager.has_create_permission(self.request, self.model):
            if options is not None:
                if len([x for x in self.buttons if x == ViewActionEnum.Create]) > 0:
                    option_urls = self.model.get_opitional_routes(model_name=mname)
                    m_buttons += (
                        {
                            'name': 'New ',
                            'link': 'javascript://',
                            'unique_name': 'new-multiple',
                            'action_type': 'all-multi-action',
                            'icon': 'fbx-rightnav-new',
                            'items': option_urls
                        },
                    )
            else:
                if len([x for x in self.buttons if x == ViewActionEnum.Create]) > 0:
                    m_buttons += (
                        {
                            'name': 'New ',
                            'link': '/' + route.lower() + '/create',
                            'action_type': 'all-action',
                            'icon': 'fbx-rightnav-new'
                        },
                    )

                if len([x for x in self.buttons if x == ViewActionEnum.RunImporter]) > 0:
                    m_buttons += (
                        {
                            'name': 'Run Importer',
                            'link': '/' + route.lower() + '/run-importer',
                            'action_type': 'all-action run-importer',
                            'icon': 'fbx-rightnav-import'
                        },
                    )

                if len([x for x in self.buttons if x == ViewActionEnum.Mutate]) > 0:
                    m_buttons += (
                        {
                            'name': self.model.get_button_title(ViewActionEnum.Mutate),
                            'link': '/' + route.lower() + '/mutate/{0}',
                            'action_type': 'multi-action mutate confirm-action',
                            'icon': 'fbx-rightnav-convert'
                        },
                    )

                if len([x for x in self.buttons if x == ViewActionEnum.Import]) > 0:
                    m_buttons += (
                        {
                            'name': 'Import',
                            'link': '/' + route.lower() + '/import?' + self.request.GET.urlencode(),
                            'action_type': 'all-action import',
                            'icon': 'fbx-rightnav-import'
                        },
                    )

                if len([x for x in self.buttons if x == ViewActionEnum.AdvancedImport]) > 0:
                    m_buttons += (
                        {
                            'name': self.model.get_button_title(ViewActionEnum.AdvancedImport),
                            'link': '/' + route.lower() + '/import?' + self.request.GET.urlencode(),
                            'action_type': 'all-action load-import-modal',
                            'icon': 'fbx-rightnav-import'
                        },
                    )

        if BWPermissionManager.has_edit_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.Edit]) > 0:
                m_buttons += (
                    {
                        'name': 'Edit',
                        'link': '/' + route.lower() + '/edit/{0}',
                        'action_type': 'single-action',
                        'icon': 'fbx-rightnav-edit'
                    },
                )

        if BWPermissionManager.has_edit_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.Approve]) > 0:
                m_buttons += (
                    {
                        'name': 'Approve',
                        'link': '/' + route.lower() + '/approve/{0}',
                        'action_type': 'multi-action',
                        'icon': 'fbx-rightnav-tick'
                    },
                )

        if BWPermissionManager.has_edit_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.StepBack]) > 0:
                m_buttons += (
                    {
                        'name': 'Step Back',
                        'link': '/' + route.lower() + '/step_back/{0}',
                        'action_type': 'multi-action',
                        'icon': 'fbx-rightnav-back'
                    },
                )

        if BWPermissionManager.has_edit_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.Activate]) > 0:
                m_buttons += (
                    {
                        'name': 'Re-Activate',
                        'link': '/' + route.lower() + '/activate/{0}',
                        'action_type': 'multi-action',
                        'icon': 'fbx-rightnav-tick'
                    },
                )

        if BWPermissionManager.has_edit_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.Deactivate]) > 0:
                m_buttons += (
                    {
                        'name': 'Deactivate',
                        'link': '/' + route.lower() + '/deactivate/{0}',
                        'action_type': 'multi-action',
                        'icon': 'fbx-rightnav-cancel'
                    },
                )

        if BWPermissionManager.has_edit_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.Reject]) > 0:
                m_buttons += (
                    {
                        'name': 'Reject',
                        'link': '/' + route.lower() + '/reject/{0}',
                        'action_type': 'multi-action',
                        'icon': 'fbx-rightnav-cancel'
                    },
                )

        if len([x for x in self.buttons if x == ViewActionEnum.BackUp]) > 0:
            m_buttons += (
                {
                    'name': 'Back Up Now',
                    'link': '/' + route.lower() + '/backup',
                    'action_type': 'all-action',
                    'icon': 'fbx-rightnav-download'
                },
            )

        if BWPermissionManager.has_delete_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.Delete]) > 0:
                m_buttons += (
                    {
                        'name': 'Delete',
                        'link': '/' + route.lower() + '/delete/{0}',
                        'action_type': 'multi-action',
                        'icon': 'fbx-rightnav-delete'
                    },
                )

        if len([x for x in self.buttons if x == ViewActionEnum.Export]) > 0:
            m_buttons += (
                {
                    'name': 'Export',
                    'link': '/' + route.lower() + '/export?' + self.request.GET.urlencode(),
                    'action_type': 'all-action',
                    'icon': 'fbx-rightnav-convert'
                },
            )

        if len([x for x in self.buttons if x == ViewActionEnum.AdvancedExport]) > 0:
            m_buttons += (
                {
                    'name': self.model.get_button_title(ViewActionEnum.AdvancedExport),
                    'link': "advanced-export/",
                    'action_type': 'all-action load-export-modal',
                    # +(" load-export-modal" if self.model.get_export_dependant_fields() else ""),
                    'icon': 'fbx-rightnav-convert'
                },
            )

        if len([x for x in self.buttons if x == ViewActionEnum.Download]) > 0:
            m_buttons += (
                {
                    'name': 'Download',
                    'link': '/' + route.lower() + '/download/{0}',
                    'action_type': 'multi-action',
                    'icon': 'fbx-rightnav-download'
                },
            )

        if len([x for x in self.buttons if x == ViewActionEnum.Reload]) > 0:
            m_buttons += (
                {
                    'name': 'Refresh',
                    'link': self.request.META['PATH_INFO'],
                    'action_type': 'all-action',
                    'icon': 'icon-refresh'
                },
            )

        if BWPermissionManager.has_edit_permission(self.request, self.model):
            if len([x for x in self.buttons if x == ViewActionEnum.RouteDesign]) > 0:
                m_buttons += (
                    {
                        'name': 'Design Route',
                        'link': '/route-designs/edit/{0}',
                        'action_type': 'single-action',
                        'icon': 'fbx-rightnav-edit'
                    },
                )

        return m_buttons
