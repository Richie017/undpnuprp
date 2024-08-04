from django.apps import apps
from django.urls import reverse
from django.db import transaction
from django.db.models.manager import Manager
from django.db.models.query_utils import Q

from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions.exceptions import EntityNotDeletableException
from blackwidow.engine.extensions.bw_titleize import bw_titleize

get_model = apps.get_model

__author__ = 'Tareq'


class RestorableModelMixin(object):
    @classmethod
    def success_url(cls):
        return reverse(cls.get_route_name(ViewActionEnum.Manage))

    def soft_delete(self, *args, force_delete=False, user=None, skip_log=False, **kwargs):
        with transaction.atomic():
            if not force_delete or user is None:
                references = []
                _get_all_related_objects = [
                    f for f in self._meta.get_fields()
                    if (f.one_to_many or f.one_to_one) and f.auto_created and not f.concrete
                ]
                for related_object in _get_all_related_objects:
                    if related_object is not None:
                        q = Q(**{"%s__id" % related_object.field.name: self.id})
                        _len = len(related_object.related_model.objects.filter(q))
                        if _len > 0:
                            references.append('<li><strong>' + str(_len) + '</strong>: ' + bw_titleize(
                                related_object.related_model.__name__) + '(s) </li>')
                if len(references) > 0:
                    references = ['Item is referred by - '] + ['<ul>'] + references + ['</ul>'] + [
                        'Please remove the referrer items before deleting this item.']
                    raise EntityNotDeletableException(''.join(references))

            d_log = get_model('core', 'DeleteLog')
            d_log.log(model=self, name=self.name if hasattr(self, 'name') else '-', is_visible=(not skip_log))
            self.deleted_level += 1  # increase delete level
            self.is_active = False
            self.is_deleted = True
            self.save()

    def restore(self, *args, user=None, skip_log=False, **kwargs):
        from blackwidow.core.models.contracts.base import DomainEntity

        with transaction.atomic():
            if len(self.__class__.get_dependent_field_list()) > 0:
                for field_name in self.__class__.get_dependent_field_list():
                    field = getattr(self, field_name)
                    if isinstance(field, Manager):
                        items = list(field.all())
                        # field.clear()
                        # for item in items:
                        #     if isinstance(item, DomainEntity):
                        #         item.restore(*args, user=user, **kwargs)
                    elif isinstance(field, DomainEntity):
                        field.restore(*args, user=user, skip_log=True, **kwargs)
                    else:
                        pass

            d_log = get_model('core', 'RestoreLog')
            d_log.log(model=self, name=self.name if hasattr(self, 'name') else 'Unspecified', is_visible=(not skip_log))

            if self.deleted_level > 0:
                self.deleted_level -= 1  # decrease delete level

            if self.deleted_level == 0:
                self.is_active = True  # if deleted level is 0, then entity active
                self.is_deleted = False
            self.save()
