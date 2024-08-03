from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.engine.extensions.bw_titleize import bw_decompress_name

__author__ = 'Tareq'


class GenericProxyListView(GenericListView):
    def get(self, request, *args, **kwargs):
        self.model_name = bw_decompress_name(kwargs['proxy_name'])
        self.proxy_model_name = self.model_name
        return super().get(request, *args, **kwargs)

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        return queryset.filter(type__iexact=self.model_name)
