from django.apps.registry import apps

from blackwidow.core.models.common.choice_options import ApprovalStatus

__author__ = 'Sohel'


class StepBackExecuteModelMixin(object):
    def execute_step_back(self, cls=None, *args, **kwargs):

        model_name = self.__class__.__name__

        ###Check if there any approval process defined for this model
        ApprovalProcess = apps.get_model('core', 'ApprovalProcess')
        approval_process = ApprovalProcess.get_objects_by_model_name(model_name=model_name.lower())
        if approval_process.exists():
            current_user = kwargs['user']
            role = current_user.role
            approval_process = approval_process.first()
            approval_level = approval_process.get_approval_levels_for_role(role)
            if current_user.is_super:
                approval_level = [approval_level.level for approval_level in approval_process.levels.all()]
            approval_next_level = approval_process.get_next_level(object_id=self.pk)
            if approval_level or current_user.is_super:
                if not approval_next_level or (approval_next_level and approval_next_level.level in approval_level):
                    organization = kwargs['organization'] if kwargs.get('organization') else current_user.organization
                    remarks = kwargs.get("remark")
                    ApprovalAction = apps.get_model('core', 'ApprovalAction')
                    approval_action = ApprovalAction()
                    approval_action.created_by = current_user
                    approval_action.organization = organization
                    approval_action.model_name = self.__class__.__name__
                    approval_action.object_id = self.pk
                    approval_action.status = ApprovalStatus.StepBack.value
                    approval_action.level = approval_next_level.level
                    if remarks:
                        approval_action.remarks = remarks
                    approval_action.save()

                    approval_process.actions.add(approval_action)

                    method_name = "approval_level_%s_action" % approval_next_level.level
                    if hasattr(self, method_name):
                        getattr(self, method_name)("StepBack", *args, **kwargs)
        else:
            self.final_approval_action("StepBack", *args, **kwargs)

        return self
