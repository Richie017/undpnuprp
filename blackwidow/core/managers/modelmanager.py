from crequest.middleware import CrequestMiddleware
from django.db.models.query_utils import Q

from blackwidow.core.mixins.querysetmixin.bulk_update_querysetmixin import BulkUpdateModelManagerMixin

__author__ = 'Mahmud'

from django.db import models


class DomainEntityModelManager(BulkUpdateModelManagerMixin, models.Manager):
    _filter = None

    def __init__(self, *args, filter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._filter = filter

    def get_all_subclasses(self, model):
        all_subclasses = []

        for subclass in model.__subclasses__():
            all_subclasses.append(subclass.__name__)
            all_subclasses.extend(self.get_all_subclasses(subclass))

        return all_subclasses

    def prepare_queryset(self):
        if self._filter is not None:
            queryset = super().get_queryset().filter(Q(**self._filter))
        elif self.model._meta.proxy:
            subclasses = self.get_all_subclasses(self.model) + [self.model.__name__]
            if len(subclasses) <= 1:
                queryset = super().get_queryset().filter(
                    Q(
                        **{
                            self.model.discriminator_property(): self.model.__name__
                        }
                    )
                )
            else:
                queryset = super().get_queryset().filter(
                    Q(
                        **{
                            self.model.discriminator_property() + '__in': subclasses
                        }
                    )
                )
        else:
            queryset = super().get_queryset()
        return queryset

    def get_queryset(self):
        queryset = self.prepare_queryset()
        if hasattr(self, 'instance') and hasattr(self.instance, 'is_version') and self.instance.is_version:
            return queryset.filter(is_deleted=False, is_active=True)
        return queryset.filter(is_deleted=False, is_active=True, is_version=False)

    def filter_organization(self, organization_id):
        from blackwidow.core.models.organizations.organization import Organization

        queryset = self.get_queryset()

        if Organization.get_super_organization()['id'] == organization_id:
            return queryset

        if 'organization' in [f.name for f in queryset.model._meta.fields]:
            return queryset.filter(organization_id=organization_id)
        return queryset


class DomainEntityVersionModelManager(models.Manager):
    def prepare_queryset(self):
        return super(DomainEntityVersionModelManager, self).get_queryset()

    def get_queryset(self):
        queryset = self.prepare_queryset()
        return queryset.filter(is_deleted=False, is_active=True, is_version=True)


class DomainEntityIncludeVersionsModelManager(DomainEntityModelManager):
    _filter = {'is_deleted': False, 'is_active': True}

    def get_queryset(self, *args, **kwargs):
        queryset = self.prepare_queryset()
        return queryset.filter()


class OrganizationDomainEntityIncludeVersionsModelManager(DomainEntityIncludeVersionsModelManager):
    def get_queryset(self, *args, **kwargs):
        queryset = super(OrganizationDomainEntityIncludeVersionsModelManager, self).get_queryset(*args, **kwargs)
        try:
            organization = CrequestMiddleware.get_request().c_organization
            if organization and (organization.is_super_organization() is False):
                queryset = queryset.filter(organization_id=organization.pk)

        except:
            pass

        return queryset


class DomainEntityIncludeInactiveModelManager(DomainEntityModelManager):
    def get_queryset(self):
        queryset = self.prepare_queryset()
        return queryset.filter(is_deleted=False)


class DomainEntityIncludeDeletedModelManager(DomainEntityModelManager):
    def get_queryset(self):
        queryset = self.prepare_queryset()
        return queryset.filter(is_active=True)


class DomainEntityIncludeAllModelManager(DomainEntityModelManager):
    def get_queryset(self):
        return self.prepare_queryset()


class DomainEntityQuerySet(models.QuerySet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__setattr__('base_count', super().count)
        self.__setattr__('base_first', super().first)
        self.__setattr__('base_last', super().last)
        self.__setattr__('base_filter', super().filter)
        self.__setattr__('base_all', super().all)
        self.__setattr__('base_latest', super().latest)

    def _filter_or_exclude(self, negate, *args, **kwargs):
        if self.model._meta.proxy:
            # kwargs.update({
            #     self.model.discriminator_property(): self.model.__name__
            # })
            self.query.add_filter((self.model.discriminator_property(), self.model.__name__))
        return super()._filter_or_exclude(negate, *args, **kwargs)

    def exists(self):
        if self.model._meta.proxy:
            self.query.add_filter((self.model.discriminator_property(), self.model.__name__))
        return super().exists()

    def all(self):
        if self.model._meta.proxy:
            self.query.add_filter((self.model.discriminator_property(), self.model.__name__))
        return self.base_all()

    def count(self):
        if self.model._meta.proxy:
            self.query.add_filter((self.model.discriminator_property(), self.model.__name__))
        return self.base_count()

    def first(self):
        if self.model._meta.proxy:
            self.query.add_filter((self.model.discriminator_property(), self.model.__name__))
        return self.base_first()

    def latest(self, field_name=None):
        if self.model._meta.proxy:
            self.query.add_filter((self.model.discriminator_property(), self.model.__name__))
        return self.base_latest(field_name=field_name)

    def has_organization(self):
        return False


class OrganizationDomainEntityQuerySet(DomainEntityQuerySet):
    def has_organization(self):
        return True
