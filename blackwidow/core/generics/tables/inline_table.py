from blackwidow.core.generics.tables.table import GenericTable

__author__ = 'mahmudul'


class GenericInlineTable(GenericTable):
    class Meta(GenericTable.Meta):
        paginate = False
        exclude = ("selection", )
        sequence = ('...', )
        attrs = {"class": "table table-condensed table-striped table-bordered"}
