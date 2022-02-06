from blackwidow.core.generics.views.create_view import GenericCreateView
from blackwidow.engine.extensions.bw_titleize import bw_decompress_name

__author__ = 'Tareq'


class GenericProxyCreateView(GenericCreateView):
    def get(self, request, *args, **kwargs):
        self.model_name = bw_decompress_name(kwargs['proxy_name'])
        self.form_kwargs = kwargs
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model_name = bw_decompress_name(kwargs['proxy_name'])
        self.form_kwargs = kwargs
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.form_kwargs:
            kwargs.update(self.form_kwargs)
        return kwargs
