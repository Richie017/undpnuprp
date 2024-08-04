from enum import Enum

from django.apps import apps
from django.utils.safestring import mark_safe

from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.email.email_template import EmailTemplate
from blackwidow.core.models.information.alert_group import AlertGroup
from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.core.models.users.user import ConsoleUser

get_model = apps.get_model
__author__ = 'Tareq'

from django.db import models


class AlertActionEnum(Enum):
    Create = 1
    Edit = 2
    Delete = 3

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Create.value), cls.Create.name),
                 (str(cls.Edit.value), cls.Edit.name),
                 (str(cls.Delete.value), cls.Delete.name),
                 ]
        return enums

    @classmethod
    def get_name(cls, value):
        if value == cls.Create.value:
            return "create"
        if value == cls.Edit.value:
            return "edit"
        if value == cls.Delete.value:
            return 'delete'
        return ""


class Operator(Enum):
    Equals = 0
    NotEquals = 1
    GreaterThan = 10
    SmallerThan = 11
    GreaterOrEqualsTo = 20
    SmallerOrEqualsTo = 21
    Is = 2

    @classmethod
    def get_enum_list(cls):
        enums = [(str(cls.Equals.value), cls.Equals.name),
                 (str(cls.NotEquals.value), cls.NotEquals.name),
                 (str(cls.GreaterThan.value), cls.GreaterThan.name),
                 (str(cls.SmallerThan.value), cls.SmallerThan.name),
                 (str(cls.GreaterOrEqualsTo.value), cls.GreaterOrEqualsTo.name),
                 (str(cls.SmallerOrEqualsTo.value), cls.SmallerOrEqualsTo.name),
                 (str(cls.Is.value), cls.Is.name)
                 ]
        return enums

    @classmethod
    def get_name(cls, value=None):
        if value == cls.Equals.value:
            return "=="
        if value == cls.NotEquals.value:
            return "!="
        if value == cls.GreaterThan.value:
            return ">"
        if value == cls.SmallerThan.value:
            return "<"
        if value == cls.GreaterOrEqualsTo.value:
            return ">="
        if value == cls.SmallerOrEqualsTo.value:
            return "<="
        if value == cls.Is.value:
            return "Is"
        if value is None:
            enums = [
                (str(cls.Equals.value), "=="),
                (str(cls.NotEquals.value), "!="),
                (str(cls.GreaterThan.value), ">"),
                (str(cls.SmallerThan.value), "<"),
                (str(cls.GreaterOrEqualsTo.value), ">="),
                (str(cls.SmallerOrEqualsTo.value), "<="),
                (str(cls.Is.value), "Is")
            ]
            return enums


class AlertConfig(OrganizationDomainEntity):
    subject = models.CharField(max_length=255, null=True)
    body = models.CharField(max_length=2000, null=True, default=None)
    alert_group = models.ForeignKey(AlertGroup, null=True, default=None, on_delete=models.SET_NULL)
    sends_email = models.BooleanField(default=False)
    recipient_users = models.ManyToManyField(ConsoleUser, related_name="%(app_label)s_%(class)s_related")
    email_template = models.ForeignKey(EmailTemplate, null=True, on_delete=models.SET_NULL)
    model = models.CharField(max_length=255, default=None, null=True)
    app_label = models.CharField(max_length=255, default=None, null=True)
    object_id = models.BigIntegerField(default=None, null=True)
    action = models.IntegerField(default=None, null=True)
    operation = models.IntegerField(default=None, null=True)
    model_property = models.CharField(max_length=255, null=True)
    self_comparison = models.BooleanField(default=False)
    reference_value = models.CharField(max_length=255, null=True)
    counter_part = models.ForeignKey(InfrastructureUnit, null=True, default=None, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'reference_model' in dir(self):
            model = self.__class__._meta.get_field('reference_model').related_model
            columns = model.table_columns()
            for x in columns:
                if x.startswith('render'):
                    y = x.split(":")
                    setattr(self, y[0], getattr(self.reference_model, y[0]))
                else:
                    y = x.split(":")
                    if y[0] in dir(self):
                        setattr(self, 'render_' + y[0], getattr(self.reference_model, y[0]))
                    else:
                        setattr(self, y[0], getattr(self.reference_model, y[0]))

    @classmethod
    def default_order_by(cls):
        return '-date_created'

    @property
    def alert_for(self):
        try:
            return get_model(self.app_label, self.model).objects.get(pk=self.object_id)
        except:
            return 'Not Found'

    @property
    def alert_creation_time(self):
        return self.render_timestamp(self.date_created)

    @property
    def alert_detail(self):
        return mark_safe(self.body)

    @classmethod
    def get_manage_buttons(cls):
        return []

    @classmethod
    def table_columns(cls):

        if 'reference_model' in dir(cls):
            model = cls._meta.get_field('reference_model').related_model
            return model.table_columns()
        return 'code', 'date_created', 'reference_model:Related To'

    def get_alert_body(self):
        raise NotImplementedError("Alert body not implemented.")
