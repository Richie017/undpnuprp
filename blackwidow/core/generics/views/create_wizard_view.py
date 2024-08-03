from django.contrib.formtools.wizard.views import SessionWizardView
from django.views.generic.edit import CreateView

from blackwidow.core.mixins.viewmixin.protected_view_mixin import ProtectedViewMixin


class GenericCreateWizardView(ProtectedViewMixin, SessionWizardView, CreateView):

    def get_template_names(self):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        if self.get_form_class().get_template() == '':
            return [self.model.__name__.lower() + '/create.html', 'shared/display-templates/create.html']
        return [self.get_form_class().get_template(), self.model_name + '/create.html', 'shared/display-templates/create.html']

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_form_class(self, step=0, **kwargs):
        return self.form_list[step]

    def done(self, form_list, **kwargs):
        # self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        # self.object = None
        # form = self.get_form(self.get_form_class())
        # try:
        #     if form.is_valid():
        #         result = self.form_valid(form)
        #         messages.success(request, bw_titleize(self.model_name) + ' added successfully.')
        #         return result
        #     else:
        #         messages.error(request, "Please fix the following error before continuing.")
        # except NoReverseMatch:
        #     return self.form_valid(form)
        # except Exception as err:
        #     messages.error(request, str(err))
        #     ErrorLog.log(err)
        # return self.form_invalid(form)
        return super().done(form_list, **kwargs)
