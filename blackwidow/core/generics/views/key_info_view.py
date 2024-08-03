from blackwidow.core.generics.views.details_view import GenericDetailsView

__author__ = 'Ziaul Haque'


class GenericKeyInformationView(GenericDetailsView):

    def get_template_names(self):
        return ['shared/_key_information.html']

    def get_context_data(self, **kwargs):
        context = super(GenericKeyInformationView, self).get_context_data(**kwargs)
        context['data'] = self.object
        context['model_meta']['properties'] = self.object.details_config
        return context

    def render_to_response(self, context, *args, **response_kwargs):
        return super().render_to_response(context=context, *args, **response_kwargs)