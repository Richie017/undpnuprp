from django.apps.registry import apps

from blackwidow.core.models.roles.role import Role
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager

__author__ = 'zia, Sohel, Tareq'


class ProtectedDetailsLinkConfigViewMixin(object):
    def details_link_config(self, **kwargs):
        self.detail_links = self.object.details_link_config(**kwargs)

        self.decision_found = False
        m_buttons = list()

        for detail_link in self.detail_links:
            url_name = detail_link["url_name"]
            if url_name.endswith(ViewActionEnum.Approve.value):
                if not self.decision_found:
                    self.set_approval_button_decision()
                if self.show_approve_button:
                    if BWPermissionManager.has_edit_permission(self.request, self.model):
                        m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Reject.value):
                if not self.decision_found:
                    self.set_approval_button_decision()
                if self.show_reject_button:
                    if BWPermissionManager.has_edit_permission(self.request, self.model):
                        m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.StepBack.value):
                if not self.decision_found:
                    self.set_approval_button_decision()
                if self.show_stepback_button:
                    if BWPermissionManager.has_edit_permission(self.request, self.model):
                        m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Restore.value):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.RestoreReject.value):
                if not self.decision_found:
                    self.set_approval_button_decision()
                if self.show_restore_button:
                    if BWPermissionManager.has_edit_permission(self.request, self.model):
                        m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Edit.value):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Delete.value):
                if BWPermissionManager.has_delete_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Mutate.value):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Activate.value):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Deactivate.value):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.Print.value):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith(ViewActionEnum.RouteDesign.value):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]
            elif url_name.endswith("consoleuser_reset_password"):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    m_buttons += [dict(detail_link), ]

        return m_buttons

    def set_approval_button_decision(self):
        if self.decision_found:
            return

        self.decision_found = False

        self.show_approve_button = False
        self.show_reject_button = False
        self.show_stepback_button = False
        self.show_restore_button = False

        if hasattr(self.model, 'show_approve_button_first_level'):
            self.show_approve_button_first_level = self.model.show_approve_button_first_level()
        else:
            self.show_approve_button_first_level = False

        if hasattr(self.model, 'show_reject_button_first_level'):
            self.show_reject_button_first_level = self.model.show_reject_button_first_level()
        else:
            self.show_reject_button_first_level = False

        ApprovalProcess = apps.get_model('core', 'ApprovalProcess')
        approval_processes = ApprovalProcess.get_objects_by_model_name(
            model_name=self.model.__name__,
            app_label=self.model._meta.app_label
        )
        if approval_processes.exists():
            current_user = self.request.c_user
            role = current_user.role
            if role == Role.system_admin():
                approval_process = approval_processes.first()
                approval_last_action = approval_process.get_approval_last_action(object_id=self.object.pk)
                if approval_last_action:
                    self.show_approve_button = True
                    self.show_reject_button = True
                    self.show_stepback_button = True
                    self.show_restore_button = True

                    next_level = approval_process.get_next_level(object_id=self.object.pk, request=self.request)
                    first_level = approval_process.get_approval_first_level()
                    if next_level and next_level.level == first_level.level:
                        self.show_approve_button = True
                        self.show_reject_button = True
                        self.show_restore_button = True
                        self.show_stepback_button = False
                else:
                    self.show_approve_button = self.show_approve_button_first_level

                    self.show_restore_button = False
                    self.show_stepback_button = False
                    self.show_reject_button = self.show_reject_button_first_level
                self.decision_found = True
        else:
            self.show_approve_button = True
            self.show_reject_button = True
            self.show_stepback_button = True
            self.show_restore_button = True

        for detail_link in self.detail_links:
            url_name = detail_link["url_name"]
            if url_name.endswith(ViewActionEnum.Approve.value) or url_name.endswith(ViewActionEnum.Reject.value) \
                    or url_name.endswith(ViewActionEnum.StepBack.value) or url_name.endswith(
                ViewActionEnum.RestoreReject.value):
                if not self.decision_found:
                    if approval_processes.exists():
                        current_user = self.request.c_user
                        role = current_user.role

                        approval_process = approval_processes.first()
                        current_user_levels = approval_process.get_approval_levels_for_role(role)
                        next_level = approval_process.get_next_level(object_id=self.object.pk, request=self.request)
                        if next_level and current_user_levels and (next_level.level in current_user_levels):
                            self.show_approve_button = True
                            self.show_reject_button = True
                            self.show_stepback_button = True
                            self.show_restore_button = True
                            approval_last_action = approval_process.get_approval_last_action(object_id=self.object.pk)
                            first_level = approval_process.get_approval_first_level()
                            if not approval_last_action or next_level.level == first_level.level:  # This is the first level.
                                self.show_approve_button = self.show_approve_button_first_level
                                self.show_reject_button = self.show_reject_button_first_level
                                self.show_restore_button = False
                                self.show_stepback_button = False

                self.decision_found = True
