from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.engine.extensions.bw_titleize import bw_decompress_name

__author__ = 'Tareq'


class GenericProxyDetailsView(GenericDetailsView):
    def get(self, request, *args, **kwargs):
        self.model_name = bw_decompress_name(kwargs['proxy_name'])
        return super().get(request, *args, **kwargs)
