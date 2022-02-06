from blackwidow.core.generics.views import GenericListView

__author__ = 'ActiveHigh'


class GenericChartDataView(GenericListView):
    x_axis = 'created_at'

    def get_context_data(self, **kwargs):
        if self.request.GET.get("paginate_by", '10') is not None:
            self.paginate_by = int(str(self.request.GET.get("paginate_by", '10')))

        if self.request.GET.get("page", '1') is not None:
            self.page = int(str(self.request.GET.get("page", '1')))

        y_axis = self.model_name
        if y_axis == None:
            y_axis = self.model.__name__

        context = super(GenericChartDataView, self).get_context_data(**kwargs)
        data = list()

        for item in context['object_list']:
            data.append({
                'x': item.created_at,
                'y': 0
            })

        context['object_list'] = data
        return context