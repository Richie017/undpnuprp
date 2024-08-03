from blackwidow.core.generics.tables.table import GenericTable

__author__ = 'ruddra'


class GenericPrintableTable(GenericTable):
    class Meta(GenericTable.Meta):
        paginate = False
        sortable = False
        exclude = ("selection", "actions")
        sequence = ('...',)
        attrs = {"class": "table table-condensed table-striped table-bordered"}
