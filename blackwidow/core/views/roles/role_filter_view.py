from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.managers.contextmanager import get_model
from blackwidow.core.models.roles.role_filter import RoleFilter
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Machine II'


@decorate(override_view(model=RoleFilter, view=ViewActionEnum.Manage))
class RoleFilterView(GenericListView):
    def get_json_response(self, content, **kwargs):
        app_label = self.request.GET.get('app_label', None)
        model_name = self.request.GET.get('model', None)
        query = self.request.GET.get('query', '')
        filter = self.request.GET.get('role', None)

        if filter is None:
            return self.get_query_strings(content, app_label, model_name, query, filter, **kwargs)
        else:
            return self.get_value_strings(content, filter, query, **kwargs)

    def get_value_strings(self, content, filter, query, **kwargs):
        role_filter = RoleFilter.objects.get(pk=filter)
        options = []
        Model = role_filter.role
        try:
            current_model = Model
            if current_model is not None:
                query_list = query.split('.')
                for q in query_list:
                    fields = current_model._meta.get_fields()
                    if q:
                        for field in fields:
                            if q == field.name:
                                if field.related_model:
                                    current_model = field.related_model
                                else:
                                    current_model = None
                                break
                        if current_model is None:
                            break
                    else:
                        break
            if current_model is None:
                options.append(query)
            else:
                options = ([query + f.name for f in current_model._meta.get_fields()])
            data_dict = dict()
            data_dict['options'] = options

            return super().get_json_response(self.convert_context_to_json(data_dict), **kwargs)

        except Exception as exp:
            return super().get_json_response(content, **kwargs)

    def get_query_strings(self, content, app_label, model_name, query, filter, **kwargs):
        options = []

        if app_label is None or model_name is None:
            return super().get_json_response(content, **kwargs)

        Model = get_model(app_label=app_label, model_name=model_name)

        try:
            current_model = Model
            if current_model is not None:
                query_list = query.split('__')
                for q in query_list:
                    fields = current_model._meta.get_fields()
                    if q:
                        for field in fields:
                            if q == field.name:
                                if field.related_model:
                                    current_model = field.related_model
                                else:
                                    current_model = None
                                break
                        if current_model is None:
                            break
                    else:
                        break
            if current_model is None:
                options.append(query)
            else:
                options = ([query + f.name for f in current_model._meta.get_fields()])
            data_dict = dict()
            data_dict['options'] = options

            return super().get_json_response(self.convert_context_to_json(data_dict), **kwargs)

        except Exception as exp:
            return super().get_json_response(content, **kwargs)
