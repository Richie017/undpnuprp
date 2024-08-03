from django.views.generic.base import TemplateView

__author__ = 'shamil'


class ErrorView404(TemplateView):
    template_name = "error/404.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['color'] = 'green'
        return context

    def get(self, request, *args, **kwargs):
        response = super(ErrorView404, self).get(request, *args, **kwargs)
        response.status_code = 404
        return response

    def get_template_names(self):
        return ['error/404.html']
