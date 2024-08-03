from blackwidow.core.generics.views.edit_view import GenericEditView

__author__ = 'Mahmud'


class PartialGenericEditView(GenericEditView):
    form_kwargs = None

    def get_template_names(self):
        self.model_name = self.model_name if self.model_name else self.model.__name__.lower()
        if self.get_form_class().get_template() == '':
            return [
                self.model_name + '/_partial_create.html',
                'shared/display-templates/_partial_edit.html',
                'shared/display-templates/_partial_generic_form.html']
        return [self.get_form_class().get_template(),
                self.model_name + '/_partial_create.html',
                'shared/display-templates/_partial_edit.html',
                'shared/display-templates/_partial_generic_form.html']

    def get(self, request, *args, **kwargs):
        self.form_kwargs = kwargs
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form_kwargs = kwargs
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.form_kwargs:
            kwargs.update(self.form_kwargs)
        return kwargs

