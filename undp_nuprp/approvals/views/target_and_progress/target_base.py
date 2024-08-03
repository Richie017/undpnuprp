from collections import OrderedDict

from django.forms.forms import Form

from blackwidow.core.generics.views.list_view import GenericListView

__author__ = 'Ziaul Haque'


class TargetBaseView(GenericListView):

    def get_context_data(self, **kwargs):
        context = super(TargetBaseView, self).get_context_data(**kwargs)
        context["manage_buttons"] = self.get_manage_buttons()
        context["display_model"] = self.model.get_page_title()
        context["parameters"] = self.get_search_parameters()
        return context

    def get_search_parameters(self):
        return OrderedDict()

    def get_wrapped_parameters(self, parameters):
        class DynamicForm(Form):
            pass

        form = DynamicForm()
        for p in parameters:
            form.fields[p['name']] = p['field']
        return form
