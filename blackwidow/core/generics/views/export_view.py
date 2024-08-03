from django.contrib import messages

from blackwidow.core.generics.exporter.generic_exporter import GenericExporter
from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.engine.extensions.bw_titleize import bw_titleize


class GenericExportView(GenericListView):

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(**kwargs)
        kwargs.update(request.GET)
        exporter_config = self.model.exporter_config(organization=request.c_user.organization, **kwargs)
        filename, path = GenericExporter.export_to_excel(
            queryset=queryset,
            filename=self.model.__name__,
            exporter_config=exporter_config,
            user=request.c_user,
            **kwargs
        )
        _message = bw_titleize(self.model.__name__) + " data have been successfully exported to files. <ol><li>" + \
                   filename + "</li>" + \
                   "Please visit the <strong>Exported Files</strong> section to download them." \
                   "<a class='btn btn-danger btn-small' href='/export-files/' %}'>View Exported Files</a>"
        messages.success(request, _message)
        return super(GenericExportView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(GenericExportView, self).get_context_data(**kwargs)
        context['export'] = True
        return context
