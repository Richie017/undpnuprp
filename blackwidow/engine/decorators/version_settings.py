import copy

from django.db import models
from django.db import transaction
from django.db.models.query_utils import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import Signal
from django.utils.safestring import mark_safe

versioned_data = Signal(providing_args=["instance"])


def version_settings(fields=[], keep_version=False, tracking_key=None):
    """
    Based on David Cramer's track_data.py
    See: http://cramer.io/2010/12/06/tracking-changes-to-fields-in-django

    Here we just add a single line to issue the track_data specific
    signal.
    """

    def version_settings(original_class):
        UNSAVED = dict()
        original_class.__data = {}
        original_class.__tracking_fields = fields
        original_class.__tracking_key = tracking_key

        def _store(self, data=None):
            """Updates a local copy of attributes values"""
            if self.id:
                if data:
                    self.__data = {f: getattr(data, f) for f in fields}
                else:
                    self.__data = {f: getattr(self, f) for f in fields}
            else:
                self.__data = UNSAVED

        original_class._store = _store

        @property
        def details_config(self):
            detail_dict = self._details_config
            if not self.is_version:
                versions = ''
                varsion_objects = original_class.version_objects.filter(master_version_id=self.pk).order_by('-pk')[1:]
                for index, version in enumerate(varsion_objects[::-1]):
                    versions += self.get_version_detail_link(
                        version=version,
                        text='Version:' + str(index + 1)
                    ) + ', '
                detail_dict['versions'] = mark_safe(versions) if versions != '' else 'No Version Saved Yet'
            return detail_dict

        def save_version(self, copy_m2m=True):
            with transaction.atomic():
                version_instance = copy.deepcopy(self)
                version_instance.pk = None
                for field in list(version_instance._meta.fields):
                    if isinstance(field, models.OneToOneField):
                        setattr(version_instance, field.name, None)
                    elif isinstance(field, models.AutoField):
                        pass
                    elif isinstance(field, models.ForeignKey):
                        pass
                    else:
                        setattr(version_instance, field.name, getattr(self, field.name, None))
                version_instance.tsync_id = None
                version_instance.is_version = True
                version_instance.save(version=False)
                for m2m_field in list(self._meta.many_to_many):
                    if m2m_field.name != 'versions':
                        version_items = getattr(version_instance, m2m_field.name)
                        original_items = getattr(self, m2m_field.name)
                        for item in original_items.all().order_by('pk'):
                            if copy_m2m:
                                new_item = copy.deepcopy(item)
                                new_item.pk = None
                                new_item.tsync_id = None
                                new_item.is_version = True
                                new_item.save()
                                version_items.add(new_item)
                            else:
                                version_items.add(item)
                self.versions.add(version_instance)

        def create_version_if_needed(self, **kwargs):
            master_object = self
            if self.type != original_class.__name__:
                models = [model for model in original_class.get_subclasses() if self.type == model.__name__]
                if len(models) == 1:
                    master_object = models[0].objects.get(pk=self.pk)
            previous = original_class.version_objects.filter(master_version_id=master_object.pk).last()
            if getattr(kwargs, 'created', False) or previous is None:
                self.save_version(copy_m2m=True, master_object=master_object)
                if hasattr(master_object, 'on_object_change'):
                    master_object.on_object_change(created=True)
            else:
                _store(self)
                for field in self.__data.keys():
                    old_value = getattr(previous, field, None)
                    new_value = getattr(master_object, field, None)
                    if new_value and new_value.__class__.__name__ == 'ManyRelatedManager':
                        old_dict = {}
                        for o_item in old_value.model.version_objects.filter(**old_value.core_filters).order_by('pk'):
                            o_item.__class__._store(o_item)
                            old_dict[getattr(o_item, o_item.__class__.__tracking_key, o_item.pk)] = o_item.__data
                        new_dict = {}
                        for n_item in new_value.all().order_by('pk'):
                            n_item.__class__._store(n_item)
                            new_dict[getattr(n_item, n_item.__class__.__tracking_key, n_item.pk)] = n_item.__data
                        if not old_dict == new_dict:
                            self.save_version(copy_m2m=True, master_object=master_object)
                            if hasattr(master_object, 'on_object_change'):
                                master_object.on_object_change(updated=True)
                    else:
                        pass

        def restore_version(self, version_object=None, keep_version=False, *args, **kwargs):
            if version_object:
                with transaction.atomic():
                    for field in self.__tracking_fields:
                        version_value = getattr(version_object, field, None)
                        master_value = getattr(self, field, None)
                        if master_value and master_value.__class__.__name__ == 'ManyRelatedManager':
                            master_item_pks = list(master_value.all().values_list('pk', flat=True))
                            for version_item in \
                                    version_value.model.version_objects.filter(**version_value.core_filters):
                                master_item = None
                                if version_item.__tracking_key:
                                    master_item = master_value.filter(Q(**{
                                        version_item.__tracking_key:
                                            getattr(version_item, version_item.__tracking_key)
                                    })).first()
                                if master_item is None:
                                    master_item = copy.deepcopy(version_item)
                                    master_item.pk = None
                                    master_item.tsync_id = None
                                    master_item.save()
                                    master_value.add(master_item)
                                else:
                                    master_item.restore_version(version_object=version_item, keep_version=False)
                                    master_item_pks.remove(master_item.pk)
                            removing_items = master_value.filter(pk__in=master_item_pks)
                            for r_item in removing_items:
                                master_value.remove(r_item)
                        else:
                            setattr(self, field, version_value)
                    self.save()
                    if keep_version:
                        self.save_version()
                        if hasattr(self, 'on_object_change'):
                            self.on_object_change(version_restored=True, **kwargs)
            return self

        def save(self, *args, **kwargs):
            save._original(self, *args, **kwargs)
            _store(self)

        def soft_delete(self, *args, **kwargs):
            soft_delete._original(self, *args, **kwargs)
            if hasattr(self, 'on_object_change'):
                self.on_object_change(deleted=True, **kwargs)

        def restore(self, *args, **kwargs):
            restore._original(self, *args, **kwargs)
            if hasattr(self, 'on_object_change'):
                self.on_object_change(delete_restored=True, **kwargs)

        def _pre_save(sender, instance, **kwargs):
            pass

        def _post_save(sender, instance, **kwargs):
            pass

        # Override Pre Save Method
        pre_save.connect(_pre_save, sender=original_class, weak=False)
        # Override Post Save Method
        post_save.connect(_post_save, sender=original_class, weak=False)
        # If eligible for version
        if keep_version:
            # Override Model Save Method
            save._original = original_class.save
            original_class.save = save
            # Add Save Version Method
            original_class.save_version = save_version
            # Add Create Version Method
            original_class.create_version_if_needed = create_version_if_needed
            # Override Soft Delete Method
            soft_delete._original = original_class.soft_delete
            original_class.soft_delete = soft_delete
            # Override Restore Method
            restore._original = original_class.restore
            original_class.restore = restore
        # Add Restore Version Method
        original_class.restore_version = restore_version
        # Override Details Config Method
        original_class._details_config = original_class.details_config
        original_class.details_config = details_config

        return original_class

    return version_settings
