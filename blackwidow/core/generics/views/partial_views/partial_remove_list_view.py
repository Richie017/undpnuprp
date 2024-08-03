from django.apps import apps
get_model = apps.get_model
from django.db.models.query_utils import Q

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.mixins.viewmixin.partial_tab_view_mixin import PartialTabViewMixin


__author__ = 'Mahmud'


class PartialGenericRemoveListView(PartialTabViewMixin, GenericListView):
    template_name = 'shared/display-templates/_partial_list.html'

    def get_queryset(self, **kwargs):
        queryset = self.request.get_queryset()
        queryset = queryset.order_by(self.request.model.default_order_by())
        return self.request.model.apply_search_filter(search_params=self.request.GET, queryset=queryset, **kwargs)

    def get(self, request, *args, **kwargs):
        id = kwargs['pk']
        model = self.model.objects.filter(id=int(id))[0]
        if self.request.GET.get('ids', '') != '':
            model.remove_child_item(ids=self.request.GET.get('ids', ''), **kwargs)

            model.app_assignment(ids=self.request.GET.get('ids', ''),
                                 path=self.request.path, **kwargs)

        return self.render_json_response(dict(
            message="Items removed successfully.",
            success=True,
            load="ajax",
            load_tabs=False
        ))

    def apply_filters(self, request, tab, id):
        if tab['relation'] == 'inverted':
            childmodel = get_model(tab['model_name'].split('.')[0], tab['model_name'].split('.')[1])
            request.query = childmodel.objects.filter(Q(**{tab['property']: id}))
            request.model = childmodel
        else:
            request.query = tab['add_more_query']
            request.model = tab['model_class']
        return request

    def get_template_names(self):
        return ['shared/display-templates/_partial_list.html']