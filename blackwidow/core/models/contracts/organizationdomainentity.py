from crequest.middleware import CrequestMiddleware
from django.db import models
from django.apps import apps
from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
get_model = apps.get_model

__author__ = 'mahmudul'


class OrganizationDomainEntity(DomainEntity):
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class ODESerializer(ss):
            def create(self, attrs):
                org = self.context[
                    'request'].c_user.organization if self.context is not None else CrequestMiddleware.get_request().c_user.organization
                attrs.update({
                    "organization": org
                })
                return super().create(attrs)

            class Meta(ss.Meta):
                model = cls
                read_only_fields = ss.Meta.read_only_fields + ('organization',)

        return ODESerializer

    def get_choice_name(self):
        return self.code + " : " + self.name

    def get_language_dict(self):
        lang_dict = dict()
        for x in self.language_dict.all():
            lang_dict[x.key] = x.value

        return lang_dict

    @property
    def get_rename(self):
        return self.name

    def load_initial_data(self, **kwargs):
        super().load_initial_data(**kwargs)
        self.organization = kwargs['org']

    def save(self, *args, organization=None, **kwargs):
        if organization is not None and self.pk is None:
            self.organization = organization
        elif self.pk is None or self.pk == 0:
            try:
                self.organization = CrequestMiddleware.get_request().c_organization
            except:
                self.organization = get_model('core', 'Organization').objects.first()
        super().save(*args, **kwargs)

    @property
    def tabs_config(self):
        return [
        ]

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Edit',
                action='edit',
                icon='fbx-rightnav-edit',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit)
            ),
            dict(
                name='Delete',
                action='delete',
                icon='fbx-rightnav-delete',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            )
        ]

    class Meta:
        abstract = True
