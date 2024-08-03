from django_tables2.config import RequestConfig
from django_tables2.views import SingleTableView

from blackwidow.core.generics.tables.table import GenericTable
from blackwidow.core.mixins.viewmixin.protected_queryset_mixin import ProtectedQuerySetMixin
from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.extensions import pluralize
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from django.db.models import Sum, F

__author__ = 'mahmudul'


class GenericListView(ProtectedViewMixin, SingleTableView):
    allow_empty = True
    queryset = None
    model_name = None
    table_class = GenericTable
    data_type = "html"
    paginate_by = 999999
    page = 1
    buttons = ['new', 'edit', 'delete']
    configurable_models = dict()
    view_model = None
    template_name = ''

    def get(self, request, *args, **kwargs):
        if not BWPermissionManager.has_view_permission(self.request, self.model):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")
        return super(GenericListView, self).get(request, *args, **kwargs)

    def get_template_names(self):
        current_path = self.request.get_full_path()

        if current_path.endswith("demo_intro/"):
            return ["common/demo_intro.html"]
        elif self.template_name != '':
            return [self.template_name]
        if self.request.GET.get('is_partial', False):
            return ['shared/display-templates/_generic_list.html']
        return ['shared/display-templates/list.html']

    def get_table_data(self):
        data = super().get_table_data()
        if self.view_model:
            return [self.view_model.init(x) for x in data]
        return data

    def get_table_class(self, **kwargs):
        _model = getattr(self.request, 'model', self.model)
        return _model.get_table_class(request=self.request, **kwargs)

    def get_context_data(self, **kwargs):
        if self.request.GET.get('disable_pagination', False):
            self.paginate_by = 999999
        else:
            self.paginate_by = self.request.GET.get("paginate_by", 25)
        self.page = self.request.GET.get("page", 1)
        context_data = super().get_context_data(**kwargs)
        return self.build_context(context_data, **kwargs)

    def get_predefined_searches(self, model):
        dds = [x.__name__ for x in model._decorators]
        if 'enable_search' in dds:
            return model.get_model_meta('enable_search', 'predefined')
        return []

    def build_context(self, context, **kwargs):
        # import pdb
        # pdb.set_trace()
        mname = self.model_name
        if mname is None:
            mname = self.model.__name__

        _r_model = getattr(self.request, 'model', self.model)
        context['model_data'] = [f.name for f in self.model._meta.get_fields()]
        context['search_template'] = 'shared/display-templates/_search.html'
        context['count'] = self.object_list.count()
        context['newcount'] = self.object_list.count()
        if mname.lower()=='grantees by ward prioritization index':
            d = self.get_queryset().aggregate(Sum('total_family_member_benefited_int'))
            if d['total_family_member_benefited_int__sum']:
                context['newcount'] = d['total_family_member_benefited_int__sum']
        context['now'] = Clock.timestamp()
        context['model'] = mname.lower()
        context['display_model'] = pluralize(mname.title()) if 'model_meta' not in context or 'model_name' not in \
                                                               context['model_meta'] else \
            context['model_meta']['model_name']
        context['manage_buttons'] = self.get_manage_buttons()
        context['get_inline_manage_buttons_decision'] = self.get_inline_manage_buttons_decision()
        context['page_sizes'] = [10, 25, 50, 100, 500]
        context['predefined_search'] = self.get_predefined_searches(_r_model)
        context["object_inline_buttons"] = self.get_object_inline_manage_buttons()
        context['searchables'] = ProtectedQuerySetMixin.build_search_fields(model=_r_model,
                                                                            columns=context['table'].columns)
        context['search_form'] = _r_model.get_search_form(context['searchables'],
                                                          _r_model.get_search_fields(self.request.GET),
                                                          _r_model.get_custom_search_fields(self.request.GET))
        context['enable_map'] = True if 'enable_map' in [x.__name__ for x in self.model._decorators] else False
        if context['enable_map']:
            context['map_object_list'] = self.convert_context_to_json(
                [x.to_json(depth=1, expand=('location',)) for x in context['object_list']])
        context['search_fields'] = self.model.get_search_fields(search_params=self.request.GET)

        RequestConfig(self.request, paginate={"per_page": self.paginate_by, "silent": True}).configure(context['table'])
        return context

    def flatten_request_parameters(self):
        obj = dict()
        for p in self.request.GET:
            value = self.request.GET.get(p)
            if isinstance(value, list):
                value = value[0]
            if isinstance(value, str):
                try:
                    obj[p] = int(value)
                except ValueError:
                    try:
                        obj[p] = float(value)
                    except ValueError:
                        obj[p] = value

        for p in self.request.POST:
            value = self.request.POST.get(p)
            if isinstance(value, list):
                value = value[0]
            if isinstance(value, str):
                try:
                    obj[p] = int(value)
                except ValueError:
                    try:
                        obj[p] = float(value)
                    except ValueError:
                        obj[p] = value
        return obj

    def render_to_response(self, context, **response_kwargs):
        context['page_sizes'] = [10, 25, 50, 100, 500]
        context['prev_pages'] = []
        start = context['page_obj'].number - 2
        if start > 1:
            context['prev_pages'].append('...')
        if start <= 0:
            start = 1
        for i in range(start, context['page_obj'].number):
            context['prev_pages'].append(i)

        context['next_pages'] = []
        for i in range(context['page_obj'].number + 1, context['page_obj'].number + 3):
            if context['page_obj'].paginator.num_pages >= i:
                context['next_pages'].append(i)

        if context['page_obj'].paginator.num_pages >= context['page_obj'].number + 3:
            context['next_pages'].append('...')

        if self.request.GET.get('format', 'html') == 'json':
            items = list(context['object_list'])
            data = {
                "items": self.json_serialize_array(items, **self.flatten_request_parameters()),
                "total_items": context['count'],
                "current_items": len(items),
                "current_page": context['page_obj'].number,
                "per_page": context['paginator'].per_page,
                "total_pages": context['paginator'].num_pages
            }
            return self.render_json_response(data)
        else:
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                **response_kwargs
            )

    def dispatch(self, request, *args, **kwargs):
        return super(GenericListView, self).dispatch(request, *args, **kwargs)
