from django.db import models

from blackwidow.core.models.common.choice_options import ApprovalStatus
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.process.approval_action import ApprovalAction
from blackwidow.core.models.process.approval_level import ApprovalLevel
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.model_descriptor import get_model_by_name

__author__ = 'Sohel'


@decorate(is_object_context,
          route(route='approval-process', group='Other Admin', group_order=1, module=ModuleEnum.Settings,
                display_name="Approval Process", item_order=1))
class ApprovalProcess(OrganizationDomainEntity):
    model_name = models.CharField(max_length=100, blank=False)
    levels = models.ManyToManyField(ApprovalLevel)
    actions = models.ManyToManyField(ApprovalAction)

    def get_approval_levels_for_role(self, role, only_step=True):
        levels = []
        approval_levels = self.levels.filter(roles__id__in=[role.pk])
        if only_step:
            levels = [approval_level.level for approval_level in approval_levels]
        else:
            levels = [approval_level for approval_level in approval_levels]
        return levels

    def get_approval_level_for_role(self, role, only_step=True):
        approval_levels = self.levels.filter(role__id=role.pk).order_by('level')
        if approval_levels.exists():
            if not only_step:
                return approval_levels.first()
            approval_level = approval_levels.first().level
            return approval_level

    def is_first_level(self, object_id):
        return True if self.actions.filter(object_id=object_id).exists() else False

    def get_approval_first_level(self):
        levels = self.levels.all().order_by('level')
        if levels.exists():
            return levels.first()

    def get_approval_last_action(self, object_id):
        return self.actions.filter(object_id=object_id).order_by(
            '-date_created').first() if self.actions.exists() else None

    def get_last_rejected_action(self, object_id):
        return self.actions.filter(object_id=object_id, status=ApprovalStatus.Rejected.value).order_by(
            '-date_created').first() if self.actions.exists() else None

    def get_next_level(self, object_id, **kwargs):
        last_action = self.get_approval_last_action(object_id=object_id)
        if not last_action:
            return self.get_approval_first_level()
        else:
            if last_action.status == ApprovalStatus.Approved.value:
                next_level = self.levels.filter(level__gt=last_action.level).order_by('level')
                if next_level.exists():
                    return next_level.first()
            elif last_action.status == ApprovalStatus.Rejected.value:
                past_levels = self.levels.filter(level__lte=last_action.level).order_by('-level')
                if past_levels.exists():
                    return past_levels.first()
            elif last_action.status == ApprovalStatus.StepBack.value:
                past_levels = self.levels.filter(level__lt=last_action.level).order_by('-level')
                if past_levels.exists():
                    return past_levels.first()
            elif last_action.status == ApprovalStatus.Restore.value:
                last_rejected_action = self.get_last_rejected_action(object_id=object_id)
                return self.levels.filter(level=last_rejected_action.level).first()

    def get_first_level(self):
        if self.levels.exists():
            return self.levels.order_by('level').first()

    @classmethod
    def table_columns(cls):
        return "code", "model_name", "created_by", "last_updated"

    @property
    def tabs_config(self):
        tabs = [
            TabView(
                title='Approval Levels',
                access_key='approval_levels',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                related_model=ApprovalLevel,
                queryset=self.levels.all(),
                queryset_filter=None,
                property=self.levels
            )
        ]
        return tabs

    @classmethod
    def get_objects_by_model_name(cls, model_name, app_label=None):
        _model = get_model_by_name(model_name=model_name, app_label=app_label)
        while _model.__name__ != 'DomainEntity':
            approval_process = cls.objects.filter(model_name=_model.__name__, is_deleted=False)
            if approval_process.exists():
                return approval_process
            else:
                _model = _model.__base__
        return ApprovalProcess.objects.none()

    def save(self, *args, organization=None, **kwargs):
        super(ApprovalProcess, self).save(*args, organization=organization, **kwargs)
