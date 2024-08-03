from django.apps.registry import apps

from blackwidow.core.models.common.choice_options import ApprovalStatus

__author__ = 'Sohel'

class ApprovalRestoreModelMixin(object):

    def execute_restore(self, cls=None, *args, **kwargs):

        model_name = self.__class__.__name__

        ###Check if there any approval process defined for this model
        ApprovalProcess = apps.get_model('core', 'ApprovalProcess')
        approval_process = ApprovalProcess.get_objects_by_model_name(model_name=model_name)
        if approval_process.exists():

            current_user = kwargs['user']
            role = current_user.role
            approval_process = approval_process.first()

            approval_last_action = approval_process.get_approval_last_action(object_id=self.pk)
            if not approval_last_action: ###If this is the first level and there is no action before then just ignore it.
                return self

            Role = apps.get_model("core", "Role")
            if role == Role.system_admin():
                organization = kwargs['organization'] if kwargs.get('organization') else current_user.organization
                remarks = kwargs.get("remark")
                ApprovalAction = apps.get_model('core','ApprovalAction')
                approval_action = ApprovalAction()
                approval_action.created_by = current_user
                approval_action.organization = organization
                approval_action.model_name = self.__class__.__name__
                approval_action.object_id = self.pk
                approval_action.status = ApprovalStatus.Restore.value
                approval_action.level = approval_last_action.level
                if remarks:
                    approval_action.remarks = remarks
                approval_action.save()

                approval_process.actions.add(approval_action)

                self.type = approval_last_action.model_name
                self.save()

                method_name = "approval_level_%s_action" % approval_last_action.level
                if hasattr(self, method_name):
                    getattr(self, method_name)("Restore",*args, **kwargs)

            else:
                current_user_levels = approval_process.get_approval_levels_for_role(role)
                next_level = approval_process.get_next_level(object_id=self.pk)
                should_permitted = False
                if next_level.level in current_user_levels:
                    should_permitted = True

                if should_permitted:
                    organization = kwargs['organization'] if kwargs.get('organization') else current_user.organization
                    remarks = kwargs.get("remark")
                    ApprovalAction = apps.get_model('core','ApprovalAction')
                    approval_action = ApprovalAction()
                    approval_action.created_by = current_user
                    approval_action.organization = organization
                    approval_action.model_name = self.__class__.__name__
                    approval_action.object_id = self.pk
                    approval_action.status = ApprovalStatus.Restore.value
                    approval_action.level = next_level.level
                    if remarks:
                        approval_action.remarks = remarks
                    approval_action.save()

                    approval_process.actions.add(approval_action)

                    self.type = approval_last_action.model_name
                    self.save()

                    method_name = "approval_level_%s_action" % approval_last_action.level
                    if hasattr(self, method_name):
                        last_rejected_action = approval_process.get_last_rejected_action(object_id=self.pk)
                        kwargs["model_name"]=last_rejected_action.model_name
                        getattr(self, method_name)("Restore",*args, **kwargs)

        else:
            self.final_approval_action("Restore", *args, **kwargs)
        return self
