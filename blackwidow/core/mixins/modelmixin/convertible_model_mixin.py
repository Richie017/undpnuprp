from django.apps.registry import apps

from blackwidow.core.models.common.choice_options import ApprovalStatus


class MutableModelMixin(object):
    def mutate_to(self, cls):
        self.type == cls.__name__
        self.__class__ = cls
        return self


class ApprovableModelMixin(object):
    """
    The approve_to method calls a hook method in each step in the following format.
    hook method format:

    approval_level_n_action

    so the method definition will be like this:
    def approval_level_0_action(self, action, *args, **kwargs):
        ###definition body will go here.

    parameters:
    The first parameter is action. It says whether it is APPROVED or REJECTED action.
    There are *args and **kwargs parameters following the action parameter.

    In the hook method name: approval_level_n_action
    n is the level number.

    For model X there is a ApprovalProcess defned with the following role.

    Approval levels:
    ===============================================
    1. role: Developer, level: 1
    2. role: Role 2, level: 3
    3. role: Role 3, level: 4

    So when developer will take any action(either approve or reject) it will look for the hook method: approval_level_1_action.
    When Role 2 will take any action it will look for the hook method with name: approval_level_3_action

    For any model if there is no approval process defined then the approve_to method look for the method final_approval_action.

    The method signature:

    def final_approval_action(self, action, *args, **kwargs):
        pass

    where action is the action taken(either APPROVED or REJECTED)

    """

    def approve_to(self, cls=None, *args, **kwargs):
        model_name = self.__class__.__name__

        ###Check if there any approval process defined for this model
        ApprovalProcess = apps.get_model('core', 'ApprovalProcess')
        approval_process = ApprovalProcess.get_objects_by_model_name(
            model_name=model_name)  # ApprovalProcess.objects.filter(model_name=model_name.lower())
        if approval_process.exists():
            current_user = kwargs['user']
            role = current_user.role
            approval_process = approval_process.first()
            Role = apps.get_model("core", "Role")
            if role == Role.system_admin():
                approval_next_level = approval_process.get_next_level(object_id=self.pk)
                if approval_next_level:
                    organization = kwargs['organization'] if kwargs.get('organization') else current_user.organization
                    remarks = kwargs.get("remark")
                    ApprovalAction = apps.get_model('core', 'ApprovalAction')
                    approval_action = ApprovalAction()
                    approval_action.created_by = current_user
                    approval_action.organization = organization
                    approval_action.model_name = self.__class__.__name__
                    approval_action.object_id = self.pk
                    approval_action.status = ApprovalStatus.Approved.value
                    approval_action.level = approval_next_level.level
                    if remarks:
                        approval_action.remarks = remarks
                    approval_action.save()

                    approval_process.actions.add(approval_action)

                    ###Now check if there is any approve_model given in the approval process.
                    ###If approve_model is given then change this model type to the new one else do nothing only call the hook method.
                    if approval_next_level.approve_model and approval_next_level.approve_model != "---":
                        self.type = approval_next_level.approve_model
                        self.save()

                    method_name = "approval_level_%s_action" % approval_next_level.level
                    if hasattr(self, method_name):
                        getattr(self, method_name)("Approved", *args, **kwargs)
            else:
                approval_levels = approval_process.get_approval_levels_for_role(role)
                approval_next_level = approval_process.get_next_level(object_id=self.pk)
                if approval_next_level:
                    if approval_next_level.level in approval_levels:
                        organization = kwargs['organization'] if kwargs.get(
                            'organization') else current_user.organization
                        remarks = kwargs.get("remark")
                        ApprovalAction = apps.get_model('core', 'ApprovalAction')
                        approval_action = ApprovalAction()
                        approval_action.created_by = current_user
                        approval_action.organization = organization
                        approval_action.model_name = self.__class__.__name__
                        approval_action.object_id = self.pk
                        approval_action.status = ApprovalStatus.Approved.value
                        approval_action.level = approval_next_level.level
                        if remarks:
                            approval_action.remarks = remarks
                        approval_action.save()

                        approval_process.actions.add(approval_action)

                        ###Now check if there is any approve_model given in the approval process.
                        ###If approve_model is given then change this model type to the new one else do nothing only call the hook method.
                        if approval_next_level.approve_model and approval_next_level.approve_model != "---":
                            self.type = approval_next_level.approve_model
                            self.save()

                        method_name = "approval_level_%s_action" % approval_next_level.level
                        if hasattr(self, method_name):
                            getattr(self, method_name)("Approved", *args, **kwargs)

        else:
            self.final_approval_action("Approved", *args, **kwargs)
        return self


class RejectableModelMixin(object):
    # def reject_to(self, cls):
    #     self.type == cls.__name__
    #     self.__class__ = cls
    #     return self

    def reject_to(self, cls=None, *args, **kwargs):
        model_class = self.__class__
        model_name = self.__class__.__name__

        ###Check if there any approval process defined for this model
        ApprovalProcess = apps.get_model('core', 'ApprovalProcess')
        approval_process = ApprovalProcess.get_objects_by_model_name(model_name=model_name)
        if approval_process.exists():
            current_user = kwargs['user']
            role = current_user.role
            approval_process = approval_process.first()

            approval_last_action = approval_process.get_approval_last_action(object_id=self.pk)

            Role = apps.get_model("core", "Role")
            if role == Role.system_admin():
                approval_next_level = approval_process.get_next_level(object_id=self.pk)
                if approval_next_level:
                    organization = kwargs['organization'] if kwargs.get('organization') else current_user.organization
                    remarks = kwargs.get("remark")
                    ApprovalAction = apps.get_model('core', 'ApprovalAction')
                    approval_action = ApprovalAction()
                    approval_action.created_by = current_user
                    approval_action.organization = organization
                    approval_action.model_name = self.__class__.__name__
                    approval_action.object_id = self.pk

                    if approval_next_level.reject_model:
                        if approval_next_level.reject_model != "---":
                            approval_action.status = ApprovalStatus.Rejected.value
                        else:
                            approval_action.status = ApprovalStatus.StepBack.value
                    approval_action.level = approval_next_level.level
                    if remarks:
                        approval_action.remarks = remarks
                    approval_action.save()

                    approval_process.actions.add(approval_action)

                    ###Now check if there is any reject_model given in the approval process.
                    ###If reject_model is given then change this model type to the new one else do nothing only call the hook method.
                    if approval_next_level.reject_model:
                        if approval_next_level.reject_model != "---":
                            self.type = approval_next_level.reject_model
                            self.save()
                        else:
                            self.type = approval_last_action.model_name
                            self.save()

                    method_name = "approval_level_%s_action" % approval_next_level.level
                    if hasattr(self, method_name):
                        if approval_next_level.reject_model:
                            if approval_next_level.reject_model != "---":
                                getattr(self, method_name)("Rejected", *args, **kwargs)
                            else:
                                getattr(self, method_name)("StepBack", *args, **kwargs)
            else:
                current_user_levels = approval_process.get_approval_levels_for_role(role)
                approval_next_level = approval_process.get_next_level(object_id=self.pk)
                if approval_next_level:
                    if approval_next_level.level in current_user_levels:
                        organization = kwargs['organization'] if kwargs.get(
                            'organization') else current_user.organization
                        remarks = kwargs.get("remark")
                        ApprovalAction = apps.get_model('core', 'ApprovalAction')
                        approval_action = ApprovalAction()
                        approval_action.created_by = current_user
                        approval_action.organization = organization
                        approval_action.model_name = self.__class__.__name__
                        approval_action.object_id = self.pk

                        if approval_next_level.reject_model:
                            if approval_next_level.reject_model != "---":
                                approval_action.status = ApprovalStatus.Rejected.value
                            else:
                                approval_action.status = ApprovalStatus.StepBack.value
                        approval_action.level = approval_next_level.level
                        if remarks:
                            approval_action.remarks = remarks
                        approval_action.save()

                        approval_process.actions.add(approval_action)

                        ###Now check if there is any reject_model given in the approval process.
                        ###If reject_model is given then change this model type to the new one else do nothing only call the hook method.
                        if approval_next_level.reject_model:
                            if approval_next_level.reject_model != "---":
                                self.type = approval_next_level.reject_model
                                self.save()
                            else:
                                self.type = approval_last_action.model_name
                                self.save()

                        method_name = "approval_level_%s_action" % approval_next_level.level
                        if hasattr(self, method_name):
                            if approval_next_level.reject_model:
                                if approval_next_level.reject_model != "---":
                                    getattr(self, method_name)("Rejected", *args, **kwargs)
                                else:
                                    getattr(self, method_name)("StepBack", *args, **kwargs)

        else:
            self.final_approval_action("Rejected", *args, **kwargs)
        return self
