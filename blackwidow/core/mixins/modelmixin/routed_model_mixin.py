from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.pluralize import pluralize

__author__ = 'Mahmud'


class RoutedModelMixin(object):
    @classmethod
    def get_form(cls, parent, **kwargs):
        class DynamicForm(parent):
            class Meta:
                model = cls
                fields = []

        return DynamicForm

    @classmethod
    def get_model_meta(cls, decorator_name, name):
        try:
            if name in cls._registry[cls.__name__][decorator_name]:
                return cls._registry[cls.__name__][decorator_name][name]
        except Exception as exp:
            if name == 'display_name':
                return bw_titleize(cls.__name__)

            if name == 'route':
                return pluralize(cls.__name__.lower())

            return None

    @classmethod
    def get_route_name(cls, action=ViewActionEnum.Details, parent=''):
        return parent + ('_' if parent != '' else '') + cls.__name__.lower() + '_' + str(action)

    def true_route_name(self, action=ViewActionEnum.Details, parent=''):
        return parent + ('_' if parent != '' else '') + self.get_leaf_class(
            label=self.type).route_model_name().lower() + '_' + str(
            action)

    @classmethod
    def get_routes(cls, partial=False, **kwargs):
        if partial:
            return [ViewActionEnum.PartialEdit, ViewActionEnum.PartialCreate, ViewActionEnum.PartialBulkAdd,
                    ViewActionEnum.PartialBulkRemove, ViewActionEnum.PartialDelete, ViewActionEnum.PartialFileUpload]
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Details, ViewActionEnum.Delete,
                ViewActionEnum.Tab, ViewActionEnum.Manage, ViewActionEnum.Mutate, ViewActionEnum.Print,
                ViewActionEnum.Export, ViewActionEnum.Download, ViewActionEnum.SecureDownload, ViewActionEnum.Approve,
                ViewActionEnum.Reject, ViewActionEnum.AdvancedImport, ViewActionEnum.AdvancedExport,
                ViewActionEnum.RouteDesign, ViewActionEnum.StepBack, ViewActionEnum.Restore,
                ViewActionEnum.RestoreReject, ViewActionEnum.ProxyLevel, ViewActionEnum.ProxyCreate,
                ViewActionEnum.ProxyDetails,
                ViewActionEnum.Activate, ViewActionEnum.Deactivate, ViewActionEnum.KeyInfo]

    @classmethod
    def route_model_name(cls):
        """
        If another model is used to show the content of this model, then, that model should be named here.
        :return:
        """
        return cls.__name__

    def details_link_config(self, **kwargs):
        return []

    @classmethod
    def get_optional_routes(cls, base_url=ViewActionEnum.Create, model_name='', parent=''):
        options = cls.get_model_meta('route', 'options')
        model_name = model_name if model_name != '' else cls.__name__
        if options is not None:
            option_urls = []
            for _op in options:
                option_urls.append(dict(
                    name=bw_titleize(_op[1]) + bw_titleize(model_name),
                    url_name=cls.get_route_name(base_url, parent=parent),
                    parameters='?type=' + _op[1]
                ))
            return option_urls
        return []

    @classmethod
    def get_leaf_class(cls, label=None):
        """
        Return leaf child class of a given class.
        :param root_class:
        if not None, then return the leaf child class of root_class. else return the leaf child class of the current (self) class
        :return:
        The leaf child class of root_class  (or self)
        """
        root_class = cls

        for x in root_class.__subclasses__():
            if x.__name__ == label:
                _c = x
                return _c
            if len(x.__subclasses__()) > 0:
                candidate_class = x.get_leaf_class(label=label)
                if candidate_class.__name__ == label:
                    return candidate_class

        return root_class
