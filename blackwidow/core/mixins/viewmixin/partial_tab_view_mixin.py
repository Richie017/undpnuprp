from blackwidow.engine.exceptions.exceptions import NotEnoughPermissionException
from blackwidow.engine.managers.bwpermissionmanager import BWPermissionManager


__author__ = 'Mahmud'


class PartialTabViewMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_partial'] = '1'
        return context

    def get_manage_buttons(self):
        return []

    # def apply_filters(self, request, tab, model):
    #     if tab['relation'] == 'inverted':
    #         childmodel = get_model(tab['model_name'].split('.')[0], tab['model_name'].split('.')[1])
    #         request.query = childmodel.objects.filter(Q(**{tab['property']: model.pk}))
    #         request.model = childmodel
    #     else:
    #         request.query = tab['model_name']
    #         request.model = tab['model_class']
    #     request.tab = tab
    #     request.partial_view = True
    #     request.instance = model
    #     return request

    def get(self, request, *args, pk=0, **kwargs):
        if not BWPermissionManager.has_view_permission(self.request, self.model):
            raise NotEnoughPermissionException("You do not have enough permission to view this content.")
        # Adding custom filter to manager
        try:
            if self.model.objects._filter and not self.model.objects_include_versions._filter:
                self.model.objects_include_versions._filter = self.model.objects._filter

            if self.model.objects._exclude and not self.model.objects_include_versions._exclude:
                self.model.objects_include_versions._exclude = self.model.objects._exclude
        except:
            pass
        model = self.model.objects.filter(id=int(pk))[0]
        self.request.tab = [x for x in model.tabs_config if x.access_key == kwargs['tab']][0]
        self.request.partial_view = True
        self.request.instance = model
        self.request.model = self.request.tab.get_model()
        return super().get(request, *args, **kwargs)

