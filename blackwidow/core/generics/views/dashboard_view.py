import django_tables2 as tables
from django.db.models.query_utils import Q
from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django_tables2.utils import A

from blackwidow.core.generics.tables.inline_table import GenericInlineTable
from blackwidow.core.generics.tables.table import GenericTable
from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin
from blackwidow.core.models.permissions.modulepermission_assignment import ModulePermissionAssignment
from blackwidow.engine.enums.enum_util import get_enum_by_property_value
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_render_tags import bw_special_chars
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.dashboard_generator import dashboard_generator
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager

__author__ = 'Imtiaz'


class GenericDashboardView(ProtectedViewMixin, TemplateView):
    template_name = "shared/dashboard.html"
    model = None

    def get_table_class(self, _model=None, **kwargs):
        selection = False
        attrs = dict()
        columns = _model.table_columns()
        attrs[columns[0]] = tables.LinkColumn(_model.get_route_name(action=ViewActionEnum.Details), args=[A('pk')])
        table_class = GenericTable if selection else GenericInlineTable
        for f in columns:
            if f != 'code' and f != 'actions':
                if f.startswith('render_'):
                    attrs[f] = tables.Column(verbose_name=bw_titleize(bw_special_chars(f)), sortable=False)
                else:
                    f_name = f.split(':')
                    attrs[f_name[0]] = tables.Column(
                        verbose_name=bw_titleize(f_name[len(f_name) - 1].replace('render_', '')), sortable=False)

        class Meta(table_class.Meta):
            model = _model
            fields = [x.split(':')[0] for x in columns]

        attrs['Meta'] = Meta
        klass = type('DynamicTable', (table_class,), attrs)
        return klass

    def filter_on_permission(self, model):
        if BWPermissionManager.has_view_permission(request=self.request, model=model):
            _user = self.request.c_user.to_business_user()
            _queryset = model.get_queryset(queryset=model.objects.all(), user=_user,
                                           profile_filter=not (_user.is_super))
            return _user.filter_model(request=self.request, queryset=_queryset)[:5]
        return None

    def dispatch(self, request, *args, **kwargs):
        current_path = self.request.get_full_path()
        module_route = request.c_request_path.replace('dashboard', '').replace('/', '')
        module = get_enum_by_property_value(ModuleEnum, 'route', module_route)
        this_model_permission = ModulePermissionAssignment.objects. \
            filter(Q(role_id=request.c_user.role_id) & Q(module__name=module.value['title'])).first()
        if this_model_permission is not None and this_model_permission.landing_model is not None:
            redirect_route = this_model_permission.landing_model.route_name
            if redirect_route != '':
                return redirect("/" + redirect_route + "/")

        if current_path.endswith("administration/dashboard"):
            return redirect("/survey/")
        elif current_path.endswith("execute/dashboard"):
            return redirect('/pending-scg-monthly-report/')
        elif current_path.endswith("surveys/dashboard"):
            return redirect('/surveys/')
        elif current_path.endswith("reports/dashboard"):
            return redirect("/pg-member-information-indicators/")
        elif current_path.endswith("settings/dashboard"):
            return redirect("/roles/")
        elif current_path.endswith("device-manager/dashboard"):
            return redirect("/devices/")
        elif current_path.endswith("communication/dashboard"):
            return redirect("/duplicate-id-alerts/")
        elif current_path.endswith("analysis/dashboard"):
            return redirect("/primary-groups/")
        return super(GenericDashboardView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        current_path = self.request.get_full_path()

        if current_path.endswith("demo_intro/dashboard"):
            return ["common/demo_intro.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_path = self.request.get_full_path()

        if current_path.endswith("kpi/dashboard"):
            self.template_name = 'shared/work_in_progress.html'
            return context

        dashboard_class = dashboard_generator(module=current_path.split('/')[1])
        _tables = []
        if len(dashboard_class) > 0:
            for x in dashboard_class:
                _dobjects = self.filter_on_permission(x)
                if _dobjects is not None:
                    _dcount = _dobjects.count()
                    _dname = x.get_model_meta('route', 'display_name')
                    if _dname is None:
                        _dname = bw_titleize(x.__name__)
                    _tables += [dict(
                        name=_dname,
                        count=_dcount,
                        url='/' + x.get_model_meta('route', 'route')
                    )]
            _items = sorted(_tables, key=lambda x: x['name'])
            context['tables'] = []
            _px = None
            for x in _items:
                if _px is None or _px['name'][0] != x['name'][0]:
                    context['tables'] += [dict(
                        name=x['name'][0],
                        count=-1,
                        url=''
                    ), x]
                else:
                    context['tables'] += [x]
                _px = x

        if len(_tables) < 1:
            self.template_name = 'shared/no_items_found.html'
        return context
