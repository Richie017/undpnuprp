from django.views.generic.base import TemplateView

__author__ = 'Ziaul Haque'


class PublicView(TemplateView):
    template_name = "public/staticpage.html"
