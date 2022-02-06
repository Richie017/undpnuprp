from django.contrib.contenttypes.models import ContentType

from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_compress_name

__author__ = 'Mahmud'


class ProxyModelMixin(object):
    @classmethod
    def discriminator_property(cls):
        return 'type'

    @classmethod
    def get_crud_model(cls):
        return cls

    def to_subclass(self):
        for x in self.__class__.__subclasses__():
            if x.__name__ == self.type:
                self.__class__ = x
        return self

    @classmethod
    def get_subclass_names(cls):
        names = [cls.__name__]
        for sub_class in cls.__subclasses__():
            names += sub_class.get_subclass_names()
        return names

    @classmethod
    def get_parent_class_names(cls):
        names = [cls.__name__]
        base_classes = cls.__bases__
        if len(base_classes) > 0 and base_classes[0].__name__ != 'DomainEntity':
            names += base_classes[0].get_parent_class_names()
        return names

    @classmethod
    def get_subclasses(cls):
        content_types = ContentType.objects.all()
        models = [ct.model_class() for ct in content_types]
        return [model for model in models
                if (model is not None and
                    issubclass(model, cls) and
                    model is not cls)]

    @classmethod
    def get_proxy_route_name(cls, proxy_model_name=''):
        return cls.get_model_meta('route',
                                  'route') + '/' + ViewActionEnum.ProxyLevel.value + '/' + bw_compress_name(
            proxy_model_name.lower())

    @classmethod
    def get_watchful_parent_class(cls):
        from blackwidow.core.models.contracts.base import DomainEntity
        if cls == DomainEntity or cls == object:
            return None
        parents = cls.__bases__
        for parent in parents:
            decorators = [x.__name__ for x in parent._decorators]
            if 'travarse_child_for_status' in decorators:
                return parent
            try:
                return parent.get_watchful_parent_class()
            except:
                return None
