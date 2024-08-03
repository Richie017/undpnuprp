from collections import OrderedDict

from django.forms.forms import Form

from blackwidow.core.generics.views.list_view import GenericListView

__author__ = 'Tareq'


class GenericReportView(GenericListView):
    def get_template_names(self):
        return ['reports/embed-report-view.html']

    def get_wrapped_parameters(self, parameters):
        class DynamicForm(Form):
            pass

        form = DynamicForm()
        for p in parameters:
            form.fields[p['name']] = p['field']
        return form

    def get_report_parameters(self, **kwargs):
        parameters = OrderedDict()
        parameters['G1'] = self.get_wrapped_parameters([])
        parameters['G2'] = self.get_wrapped_parameters([])
        parameters['G3'] = self.get_wrapped_parameters([])
        return parameters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Report"
        context['enable_map'] = False
        context['parameters'] = self.get_report_parameters(**kwargs)
        return context
