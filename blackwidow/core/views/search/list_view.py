from itertools import chain

from django_tables2.config import RequestConfig

from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.core.models.search.searchresult import SearchResult
from blackwidow.engine.decorators.utility import get_models_with_decorator
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.query_normalize import *
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from config.quick_search_config import QUICK_SEARCH_PROPERTY, QUICK_SEARCH_APP

__author__ = 'ruddra'


class SearchView(GenericListView):
    template_name = "search/search-results.html"

    def get(self, request, *args, **kwargs):
        # Permission
        return super(SearchView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        return ['search/search-results.html']

    def get_manage_buttons(self):
        return []

    def get_context_data(self, **kwargs):
        if self.request.GET.get("paginate_by", '10') is not None:
            self.paginate_by = int(str(self.request.GET.get("paginate_by", '10')))

        if self.request.GET.get("page", '1') is not None:
            self.page = int(str(self.request.GET.get("page", '1')))

        context = super(GenericListView, self).get_context_data(**kwargs)
        context['page_sizes'] = [10, 25, 50, 100, 500]

        if self.request.GET.get("sort", '') is '':
            context['table'].order_by = '-last_updated'
        context['table'] = self.get_table_class()([SearchResult(
            name=getattr(x, QUICK_SEARCH_PROPERTY[x.__class__.__name__.lower()]['title']) + " (" + bw_titleize(
                x.__class__.__name__) + ")",
            description=getattr(x, QUICK_SEARCH_PROPERTY[x.__class__.__name__.lower()]['description']),
            url=(QUICK_SEARCH_PROPERTY[x.__class__.__name__.lower()]['url'] + str(x.id))) for x in
                                                   context['object_list']])

        RequestConfig(self.request, paginate={"per_page": self.paginate_by, "silent": True}).configure(context['table'])

        return context

    def get_queryset(self):
        model_list = get_models_with_decorator('is_object_context', QUICK_SEARCH_APP, include_class=True)
        query_list = list()
        url_list = list()
        q_set = None
        query_string = self.request.GET.get('query', '')
        if query_string == "":
            self.request.session["flash_message"] = "No search input given here."
            self.request.session["flash_message_type"] = "error"
            return list()
        else:
            for model in model_list:
                if BWPermissionManager.has_view_permission(self.request,
                                                           model) and model.__name__.lower() in QUICK_SEARCH_PROPERTY:
                    if q_set is None:
                        q_set = model.objects.filter(
                            get_query(query_string, QUICK_SEARCH_PROPERTY[model.__name__.lower()]["fields"]))
                    else:
                        q_set = chain(q_set, model.objects.filter(
                            get_query(query_string, QUICK_SEARCH_PROPERTY[model.__name__.lower()]["fields"])))
            return list(q_set)
