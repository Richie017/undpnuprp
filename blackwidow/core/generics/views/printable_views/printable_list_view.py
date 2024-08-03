import django_tables2 as tables

from blackwidow.core.generics.tables.printable_table import GenericPrintableTable
from blackwidow.core.generics.views.list_view import GenericListView
from blackwidow.engine.extensions.bw_render_tags import bw_special_chars
from blackwidow.engine.extensions.bw_titleize import bw_titleize


__author__ = 'ruddra'


class GenericPrintableListView(GenericListView):

    def get_table_class(self, **kwargs):
        # tab = getattr(self.request, 'tab', None)
        # inline = False
        # selection = False
        _model = getattr(self.request, 'model', self.model)

        attrs = dict(
            # actions=tables.TemplateColumn(template_name='shared/display-templates/_inline_action.html')
        )
        columns = _model.table_columns()
        table_class = GenericPrintableTable
        for f in columns:
            if f != 'code' and f != 'actions':
                if f.startswith('render_'):
                    attrs[f] = tables.Column(verbose_name=bw_titleize(bw_special_chars(f)), sortable=False)
                else:
                    attrs[f] = tables.Column(verbose_name=bw_titleize(bw_special_chars(f)), sortable=False)

        class Meta(table_class.Meta):
            model = _model
            fields = columns

        attrs['Meta'] = Meta
        klass = type('DynamicTable', (table_class,), attrs)
        return klass