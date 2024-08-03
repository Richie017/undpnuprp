from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.mixins.viewmixin.partial_tab_view_mixin import PartialTabViewMixin


__author__ = 'Mahmud'


class PartialGenericAddListView(PartialTabViewMixin, GenericListView):
    template_name = 'shared/display-templates/_partial_list.html'

    def get_queryset(self, **kwargs):
        queryset = self.request.tab.get_queryset(add_more=True)
        queryset = queryset.order_by(self.request.model.default_order_by())
        return self.request.model.apply_search_filter(search_params=self.request.GET, queryset=queryset, **kwargs)

    def post(self, request, *args, **kwargs):
        id = kwargs['pk']
        model = self.model.objects.filter(id=int(id))[0]
        if self.request.POST.get('ids', '') != '':
             model.add_child_item(ids=self.request.POST.get('ids', ''),
                                 user=self.request.c_user,
                                 organization=self.request.c_organization, **kwargs)

             model.app_assignment(ids=self.request.POST.get('ids', ''),
                                  path=self.request.path, **kwargs)

        return self.render_json_response(dict(
            message="Items added successfully.",
            success=True,
            load="ajax",
            load_tabs=False
        ))

    # def apply_filters(self, request, tab, id):
    #     if tab['relation'] == 'inverted':
    #         childmodel = get_model(tab['model_name'].split('.')[0], tab['model_name'].split('.')[1])
    #         request.query = childmodel.objects.filter(Q(**{tab['property']: id}))
    #         request.model = childmodel
    #     else:
    #         request.query = tab['add_more_query']
    #         request.model = tab['model_class']
    #     request.tab = tab
    #     return request

    def get_template_names(self):
        return ['shared/display-templates/_partial_list.html']