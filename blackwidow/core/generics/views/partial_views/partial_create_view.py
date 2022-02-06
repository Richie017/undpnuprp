from django.contrib import messages
from django.core.urlresolvers import NoReverseMatch

from blackwidow.core.generics.views.create_view import GenericCreateView
from blackwidow.core.models.log.error_log import ErrorLog

__author__ = 'Mahmud'


class PartialGenericCreateView(GenericCreateView):
    form_kwargs = None

    def get_template_names(self):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        if self.get_form_class().get_template() == '':
            return [
                self.model_name + '/_partial_create.html',
                'shared/display-templates/_partial_create.html',
                'shared/display-templates/_partial_generic_form.html']
        return [self.get_form_class().get_template(),
                self.model_name + '/_partial_create.html',
                'shared/display-templates/_partial_create.html',
                'shared/display-templates/_partial_generic_form.html']

    def get(self, request, *args, **kwargs):
        self.form_kwargs = kwargs
        self.form_kwargs['partial_view'] = True
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form_kwargs = kwargs
        self.form_kwargs['partial_view'] = True

        if 'tab' in kwargs:
            id = kwargs['parent_id']
            model = self.model.objects.filter(id=int(id))[0]
            self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
            self.object = None
            form = self.get_form(self.get_form_class())
            try:
                if form.is_valid():
                    result = self.form_valid(form)
                    model.add_child_item(ids=str(form.instance.pk), user=self.request.c_user,
                                         organization=self.request.c_organization, **kwargs)
                    return result
                else:
                    messages.error(request, "Please fix the following error before continuing.")
            except NoReverseMatch:
                return self.form_valid(form)
            except Exception as err:
                messages.error(request, str(err))
                ErrorLog.log(err)
                return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.form_kwargs:
            kwargs.update(self.form_kwargs)
        return kwargs
