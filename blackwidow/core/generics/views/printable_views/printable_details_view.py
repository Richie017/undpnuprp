from blackwidow.core.generics.views.details_view import GenericDetailsView

__author__ = 'sifat'


class GenericPrintableContentView(GenericDetailsView):
    template_name = 'shared/printable_details.html'

    def get_template_names(self):
        template_names = super().get_template_names()
        if self.model.__name__ == 'PrimarySalesCompletedOrder':
            return ['shared/invoice.html']
        return ['shared/printable_details.html']
