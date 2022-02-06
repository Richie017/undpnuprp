from django.apps import apps

from blackwidow.engine.routers.database_router import BWDatabaseRouter

get_model = apps.get_model
from blackwidow.engine.enums.tab_view_enum import ModelRelationType


class TabViewAction(object):
    title = ""
    action = ""
    icon = ""
    css_class = ""
    route_name = ""
    enable_ajax = True
    enable_multiple_create = True
    enable_wide_popup = False

    @property
    def wide(self):
        return "1" if self.enable_ajax else "0"

    @property
    def ajax(self):
        return "1" if self.enable_ajax else "0"

    def __init__(self, title, action, icon, css_class, route_name,
                 enable_ajax=True, enable_multiple_create=True, enable_wide_popup=False):
        super().__init__()

        self.title = title
        self.action = action
        self.icon = icon
        self.css_class = css_class
        self.route_name = route_name
        self.enable_ajax = enable_ajax
        self.enable_multiple_create = enable_multiple_create
        self.enable_wide_popup = enable_wide_popup


class TabView(object):
    title = ""
    access_key = ""
    enable_ajax = True
    enable_inline_edit = False
    route_name = ""
    related_model = None
    child_tabs = []
    queryset_filter = None
    queryset = None
    relation_type = ModelRelationType.NORMAL
    message = ""
    model_property = None
    actions = []
    inline_actions = []
    add_more_queryset = None

    @property
    def ajax(self):
        return "1" if self.enable_ajax else "0"

    def __init__(self, title, access_key, route_name, relation_type, related_model, child_tabs='', actions=[],
                 add_more_queryset=None, enable_ajax=True, enable_inline_edit=False, property=None, message="",
                 queryset=None, queryset_filter=None):
        super().__init__()

        self.title = title
        self.access_key = access_key

        if not isinstance(enable_ajax, bool):
            raise Exception('TabView enable ajax must a boolean : True or False')

        self.enable_ajax = enable_ajax

        if isinstance(related_model, str):
            related_model = get_model(related_model.split('.')[0], related_model.split('.')[1])

        self.related_model = related_model
        self.child_tabs = child_tabs
        self.queryset = queryset
        self.queryset_filter = queryset_filter

        if related_model is None and queryset is None:
            raise Exception('You must provide at least one of this values -  related_model or queryset')

        self.relation_type = relation_type
        self.route_name = route_name
        self.message = message

        for a in actions:
            if not isinstance(a, TabViewAction):
                raise Exception('TabView actions must be instances of TabViewAction class')

        self.actions = actions
        self.model_property = property

        if self.model_property is None and self.relation_type == ModelRelationType.NORMAL:
            raise Exception("model_property must be provided for relation_type == ModelRelationType.NORMAL")

        self.enable_inline_edit = enable_inline_edit
        self.add_more_queryset = add_more_queryset

    def get_queryset(self, add_more=False, **kwargs):

        if add_more and self.add_more_queryset is None:
            raise Exception("Add more queryset is none.")
        if add_more:
            return self.add_more_queryset

        queryset = self.queryset

        if queryset is None:
            if self.relation_type == ModelRelationType.NORMAL:
                queryset = self.model_property.all()
            else:
                queryset = self.related_model.objects.all()

        if self.queryset_filter is not None:
            queryset = queryset.filter(self.queryset_filter)

        return queryset.using(BWDatabaseRouter.get_read_database_name())

    def get_model(self):
        return self.related_model

    def get_child_tabs(self):
        return self.child_tabs

    def add_item(self, item):
        if self.model_property is None:
            raise Exception("Property option must be provided to support add_item")

        for x in self.model_property.all():
            if x.pk == item.pk:
                return

        self.model_property.add(item)
        # self.save()

    def remove_item(self, item):
        if self.model_property is None:
            raise Exception("Property option must be provided to support remove_item")

        for x in self.model_property.all():
            if x.pk == item.pk:
                self.model_property.remove(item)
                # self.save()
                return
