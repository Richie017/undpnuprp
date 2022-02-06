import copy

from django.db import models
from django.db import transaction
from django.conf import settings

__author__ = 'Razon'


class VersioningModelMixin(object):
    def initialize_default_attributes(self, *args, **kwargs):
        self.pk = None
        self.tsync_id = None
        self.code = ''

    def handle_version_creation(self, *args, **kwargs):
        model = self._meta.model
        version_settings = getattr(settings, "enable_versioning", True)
        if version_settings:
            if kwargs.get("decorator_versioning", True):
                if model._decorators is not None:
                    for decorator in model._decorators:
                        if decorator.__name__ == "enable_versioning":
                            return self.create_new_version()
            else:
                return self.create_new_version()
        return None

    @classmethod
    def version_enabled_related_fields(cls):
        return []

    def create_new_version(self, *args, **kwargs):
        master_object = self
        with transaction.atomic():
            version_instance = copy.deepcopy(master_object)
            version_instance.initialize_default_attributes()
            # versioning one to one and foreign key fields
            for field in list(version_instance._meta.fields):
                if isinstance(field, models.OneToOneField):
                    setattr(version_instance, field.name, None)
                    if field.name in self.version_enabled_related_fields():
                        related_object = getattr(master_object, field.name, None)
                        if related_object:
                            setattr(version_instance, field.name, related_object.create_new_version())
                elif isinstance(field, models.ForeignKey):
                    if field.name in self.version_enabled_related_fields():
                        related_object = getattr(master_object, field.name, None)
                        if related_object:
                            setattr(version_instance, field.name, related_object.create_new_version())
            version_instance.is_version = True
            version_instance.master_version_id = master_object.pk
            if kwargs.get("field_values"):
                for key, value in kwargs.get("field_values").items():
                    setattr(version_instance, key, value)
            version_instance.save(version=True)
            # versioning m2m fields
            for m2m_field in list(master_object._meta.many_to_many):
                version_items = getattr(version_instance, m2m_field.name)
                original_items = getattr(master_object, m2m_field.name)
                for item in original_items.all().order_by('pk'):
                    if m2m_field.name in self.version_enabled_related_fields():
                        new_item = item.create_new_version()
                        version_items.add(new_item)
                    else:
                        version_items.add(item)
            # versioning reverse foreign key fields
            for related_field in list(master_object._meta.related_objects):
                if related_field.name in self.version_enabled_related_fields():
                    for item in related_field.related_model.objects.filter(
                            **{related_field.remote_field.name: master_object}):
                        new_item = item.create_new_version(field_values={
                            related_field.remote_field.name: version_instance
                        })
            return version_instance
