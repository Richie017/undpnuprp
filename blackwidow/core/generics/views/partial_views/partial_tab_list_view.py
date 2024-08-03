from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.mixins.viewmixin.partial_tab_view_mixin import PartialTabViewMixin
from blackwidow.engine.routers.database_router import BWDatabaseRouter

__author__ = 'Mahmud'


class PartialGenericTabListView(PartialTabViewMixin, GenericListView):
    template_name = 'shared/display-templates/_partial_list.html'

    def get_queryset(self, **kwargs):
        queryset = self.request.tab.get_queryset()
        queryset = queryset.order_by(self.request.model.default_order_by())
        return self.request.model.apply_search_filter(search_params=self.request.GET, queryset=queryset, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_partial'] = '1'
        context['tab'] = self.request.tab
        context['data'] = self.request.instance
        return context

    def get_template_names(self):
        return ['shared/display-templates/_partial_list.html']
