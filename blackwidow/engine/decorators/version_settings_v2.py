import copy

from django.db import models
from django.db import transaction
from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.dispatch import Signal

from blackwidow.core.models.contracts.base import DomainEntity

versioned_data = Signal(providing_args=["instance"])


def version_settings(fields=[], keep_version=True):
    """
    Based on David Cramer's track_data.py
    See: http://cramer.io/2010/12/06/tracking-changes-to-fields-in-django

    Here we just add a single line to issue the track_data specific
    signal.
    """

    UNSAVED = dict()

    def _store(self, data=None):
        """Updates a local copy of attributes values"""
        if self.id:
            if data:
                self.__data = {f: getattr(data, f) for f in fields}
            else:
                self.__data = {f: getattr(self, f) for f in fields}
        else:
            self.__data = UNSAVED

    def inner(cls):
        """contains a local copy of the previous values of attributes"""
        cls.__data = {}
        cls._store = _store

        def has_changed(self, field):
            """Returns 'True' if 'field' has changed since initialization."""
            if self.__data is UNSAVED:
                return False
            return self.__data.get(field) != getattr(self, field)

        cls.has_changed = has_changed

        def old_value(self, field):
            """Returns the previous value of 'field'"""
            return self.__data.get(field)

        cls.old_value = old_value

        def whats_changed(self):
            """Returns a list of changed attributes."""
            changed = {}
            if self.__data is UNSAVED:
                return True
            version = self.versions.order_by('-pk').first()
            for k, v in self.__data.items():
                value = getattr(self, k)
                if value and isinstance(value, DomainEntity) and k in self.__data.keys():
                    if version:
                        old_item = getattr(version, k)
                        if old_item and hasattr(value, '_store') and hasattr(value, 'whats_changed'):
                            value._store(old_item)
                            value.save_version_if_changed(sender=value.__class__)
                            changed[k] = True
                        elif old_item is None:
                            value.save_version()
                            changed[k] = True
                    elif hasattr(value, 'save_version'):
                        value.save_version()
                        changed[k] = True
                elif v != value:
                    changed[k] = value
            return changed

        cls.whats_changed = whats_changed

        def save_version_if_changed(self, sender=None, **kwargs):
            if sender and self \
                    and self.whats_changed():
                self.save_version(sender=sender, **kwargs)

        cls.save_version_if_changed = save_version_if_changed

        def save_version(self):
            with transaction.atomic():
                version_instance = copy.deepcopy(self)
                version_instance.pk = None
                for field in list(version_instance._meta.fields):
                    if isinstance(field, models.OneToOneField):
                        setattr(version_instance, field.name, None)
                    elif isinstance(field, models.AutoField):
                        pass
                    elif isinstance(field, models.ForeignKey):
                        value = getattr(self, field.name, None)
                        if value and isinstance(value, DomainEntity):
                            version = value.versions.order_by('-pk').first()
                            if version:
                                setattr(
                                    version_instance, field.name + '_id',
                                    version.pk
                                )
                            else:
                                setattr(
                                    version_instance, field.name,
                                    getattr(self, field.name, None)
                                )
                    else:
                        setattr(version_instance, field.name, getattr(self, field.name, None))
                version_instance.tsync_id = None
                version_instance.is_version = True
                version_instance.save(version=False)
                for m2m_field in list(self._meta.many_to_many):
                    if m2m_field.name != 'versions':
                        version_items = getattr(version_instance, m2m_field.name)
                        original_items = getattr(self, m2m_field.name)
                        for item in original_items.all():
                            version_items.add(item)
                self.versions.add(version_instance)

        cls.save_version = save_version

        """Ensure we are updating local attributes on model pre_save"""
        def _pre_save(sender, instance, **kwargs):
            if not kwargs.get('raw', False):
                inst = None
                if instance.id:
                    # get old values
                    try:
                        inst = sender.objects.get(id=instance.id)
                    except sender.DoesNotExist:
                        pass
                _store(instance, inst)

        """Ensure we are updating local attributes on model pre_save"""
        def _post_save(sender, instance, **kwargs):
            if not kwargs.get('raw', False):
                # we emit a unique signal so that others can connect to
                if not getattr(instance, 'is_version', True):
                    versioned_data.send(sender=cls, instance=instance)

        pre_save.connect(_pre_save, sender=cls, weak=False)
        post_save.connect(_post_save, sender=cls, weak=False)

        def m2m_items_changed(sender, instance, model, **kwargs):
            pass

        for field in fields:
            attribute = getattr(cls, field, None)
            if attribute and isinstance(attribute, ManyToManyDescriptor):
                m2m_changed.connect(m2m_items_changed, sender=attribute.through, weak=False)

        def create_version_if_needed(self, **kwargs):
            new_version = False
            if self.versions.count() == 0:
                new_version = True
            else:
                previous = self.versions.all().order_by('-pk').first()
                # previous
            if new_version:
                self.save_version()
            return new_version
        cls.create_version_if_needed = create_version_if_needed

        """Ensure we are updating local attributes on model save"""
        def save(self, *args, **kwargs):
            save._original(self, *args, **kwargs)
            _store(self)

        save._original = cls.save
        cls.save = save

        @property
        def details_config(self):
            detail_dict = self._details_config
            return detail_dict
        cls._details_config = cls.details_config
        cls.details_config = details_config

        return cls

    return inner
