from blackwidow.engine.constants.access_permissions import BW_ACCESS_CREATE_MODIFY_DELETE, BW_ACCESS_CREATE_MODIFY, \
    BW_ACCESS_MODIFY_ONLY, BW_ACCESS_READ_ONLY, BW_ACCESS_NO_ACCESS
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager

__author__ = 'zia'


class ProtectedInlineManageButtonDecisionViewMixin(object):
    def get_object_inline_manage_buttons(self):
        # buttons = self.model.get_object_inline_buttons()
        buttons = self.model.get_object_inline_buttons()

        if any(filter(lambda x: x.__name__ == 'is_object_context', self.model._decorators)):
            inline_buttons = list()

            if BWPermissionManager.has_view_permission(self.request, self.model):
                if len([x for x in buttons if x == ViewActionEnum.Details]) > 0:
                    inline_buttons += [ViewActionEnum.Details]
                if len([x for x in buttons if x == ViewActionEnum.SecureDownload]) > 0:
                    inline_buttons += [ViewActionEnum.SecureDownload]

            if BWPermissionManager.has_edit_permission(self.request, self.model):
                if len([x for x in buttons if x == ViewActionEnum.Edit]) > 0:
                    inline_buttons += [ViewActionEnum.Edit]

            if BWPermissionManager.has_delete_permission(self.request, self.model):
                if len([x for x in buttons if x == ViewActionEnum.Delete]) > 0:
                    inline_buttons += [ViewActionEnum.Delete]
                if len([x for x in buttons if x == ViewActionEnum.Restore]) > 0:
                    inline_buttons += [ViewActionEnum.Restore]

            if BWPermissionManager.has_edit_permission(self.request, self.model):

                if len([x for x in buttons if x == ViewActionEnum.Mutate]) > 0:
                    inline_buttons += [ViewActionEnum.Mutate]

                if len([x for x in buttons if x == ViewActionEnum.Approve]) > 0:
                    inline_buttons += [ViewActionEnum.Approve]

                if len([x for x in buttons if x == ViewActionEnum.Reject]) > 0:
                    inline_buttons += [ViewActionEnum.Reject]

                if len([x for x in buttons if x == ViewActionEnum.Deactivate]) > 0:
                    inline_buttons += [ViewActionEnum.Deactivate]

                if len([x for x in buttons if x == ViewActionEnum.Activate]) > 0:
                    inline_buttons += [ViewActionEnum.Activate]

            return inline_buttons
        return []

    def get_inline_manage_buttons_decision(self):
        self.buttons_permitted = self.model.get_inline_manage_buttons_decision()
        self.buttons_permitted = int(self.buttons_permitted['value'])
        mname = self.model.get_model_meta('route', 'display_name')
        route = self.model.get_model_meta('route', 'route')
        if mname is None:
            mname = self.model.__name__.lower()

        m_buttons = list()

        options = self.model.get_model_meta('route', 'options')
        # check for create permission for current model
        if not any(filter(lambda x: x.__name__ == 'is_object_context', self.model._decorators)):
            return BW_ACCESS_NO_ACCESS  ###No Access
        if self.buttons_permitted == int(BW_ACCESS_CREATE_MODIFY_DELETE["value"]):  ###BW_ACCESS_CREATE_MODIFY_DELETE
            if BWPermissionManager.has_view_permission(self.request, self.model):
                no_permission = BWPermissionManager.has_no_permission(self.request, self.model)
                if BWPermissionManager.has_create_permission(self.request,
                                                             self.model) and BWPermissionManager.has_edit_permission(
                    self.request, self.model) \
                        and BWPermissionManager.has_delete_permission(self.request, self.model):
                    return BW_ACCESS_CREATE_MODIFY_DELETE
                elif BWPermissionManager.has_create_permission(self.request,
                                                               self.model) and BWPermissionManager.has_edit_permission(
                    self.request, self.model):
                    return BW_ACCESS_CREATE_MODIFY
                elif BWPermissionManager.has_edit_permission(self.request, self.model):
                    return BW_ACCESS_MODIFY_ONLY
                else:
                    return BW_ACCESS_READ_ONLY
        elif self.buttons_permitted == int(BW_ACCESS_CREATE_MODIFY["value"]):  ###BW_ACCESS_CREATE_MODIFY
            if BWPermissionManager.has_view_permission(self.request, self.model):
                if BWPermissionManager.has_create_permission(self.request,
                                                             self.model) and BWPermissionManager.has_edit_permission(
                    self.request, self.model):
                    return BW_ACCESS_CREATE_MODIFY
                elif BWPermissionManager.has_edit_permission(self.request, self.model):
                    return BW_ACCESS_MODIFY_ONLY
                else:
                    return BW_ACCESS_READ_ONLY
        elif self.buttons_permitted == int(BW_ACCESS_MODIFY_ONLY["value"]):  ###BW_ACCESS_MODIFY_ONLY
            if BWPermissionManager.has_view_permission(self.request, self.model):
                if BWPermissionManager.has_edit_permission(self.request, self.model):
                    return BW_ACCESS_MODIFY_ONLY
                else:
                    return BW_ACCESS_READ_ONLY
        elif self.buttons_permitted == int(BW_ACCESS_READ_ONLY["value"]):  ###BW_ACCESS_READ_ONLY
            if BWPermissionManager.has_view_permission(self.request, self.model):
                return BW_ACCESS_READ_ONLY
            else:
                return BW_ACCESS_NO_ACCESS
        elif self.buttons_permitted == int(BW_ACCESS_NO_ACCESS["value"]):  ###BW_ACCESS_NO_ACCESS
            return BW_ACCESS_NO_ACCESS
