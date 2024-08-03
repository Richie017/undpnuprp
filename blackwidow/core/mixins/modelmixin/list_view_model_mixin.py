import django_tables2 as tables
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.safestring import mark_safe
from django_tables2.utils import A

from blackwidow.core.generics.tables.inline_table import GenericInlineTable
from blackwidow.core.generics.tables.printable_table import GenericPrintableTable
from blackwidow.core.generics.tables.table import GenericTable
from blackwidow.engine.constants.access_permissions import BW_ACCESS_CREATE_MODIFY_DELETE
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_render_tags import bw_special_chars
from blackwidow.engine.extensions.bw_titleize import bw_titleize
from blackwidow.engine.extensions.model_descriptor import get_model_by_name

__author__ = 'Mahmud'


class ListViewModelMixin(object):
    @classmethod
    def searchables(cls, **kwargs):
        fields = cls._meta.concrete_fields
        return [f.name for f in fields if isinstance(f, models.CharField)]

    @classmethod
    def searchable_tabls_columns(cls, **kwargs):
        table_columns = cls.table_columns()
        temp_table_columns = []
        for c in table_columns:
            if ":" in c:
                temp_table_columns += [c.split(":")[0]]
            else:
                temp_table_columns += [c]
        table_columns = temp_table_columns

        exclude_search_fields = cls.exclude_search_fields()
        temp_exclude_columns = []
        for c in exclude_search_fields:
            if ":" in c:
                temp_exclude_columns += [c.split(":")[0]]
            else:
                temp_exclude_columns += [c]
        exclude_search_fields = temp_exclude_columns
        searchable_table_columns = list(set(table_columns) - set(exclude_search_fields))

        searchable_fields = []
        for f in searchable_table_columns:
            try:
                if ":" in f:
                    _f = f.split(":")[0]
                    field = cls._meta.get_field(_f)
                    if not isinstance(field, (
                            models.BigIntegerField, models.IntegerField, models.DateTimeField, models.DateField)):
                        searchable_fields += [_f]
                else:
                    f = f.split(":")[0]
                    field = cls._meta.get_field(f)
                    if not isinstance(field, (
                            models.BigIntegerField, models.IntegerField, models.DateTimeField, models.DateField)):
                        searchable_fields += [f]
            except Exception as exp:
                if ":" in f:
                    searchable_fields += [f.split(":")[0]]
                else:
                    searchable_fields += [f]

        return searchable_fields

    @classmethod
    def get_button(cls, button=ViewActionEnum.Details):
        return button.value

    @property
    def get_inline_manage_buttons(self):
        return [
            dict(
                name='Edit',
                action='edit',
                title="Click to edit this item",
                icon='icon-pencil',
                ajax='0',
                url_name=self.__class__.true_route_name(action=ViewActionEnum.Edit),
                classes='all-action',
                parent=None
            ), dict(
                name='Delete',
                action='delete',
                title="Click to remove this item",
                icon='icon-remove',
                ajax='0',
                url_name=self.__class__.true_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            ), dict(
                name='Details',
                action='view',
                title="Click to view this item",
                icon='icon-eye',
                ajax='0',
                url_name=self.__class__.true_route_name(action=ViewActionEnum.Details),
                classes='all-action ',
                parent=None
            )]

    @property
    def render_code(self):
        if self.is_deleted or not self.is_active:
            return self.code
        try:
            # Model = get_model_by_name(self.type)
            code_href = reverse(self.__class__.true_route_name(ViewActionEnum.Details), kwargs={'pk': self.pk})
        except:
            try:
                code_href = reverse(self.true_route_name(ViewActionEnum.Details), kwargs={'pk': self.pk})
            except:
                return self.code
        return mark_safe("<a class='inline-link' href='" + code_href + "' >" + self.code + "</a>")

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Edit, ViewActionEnum.Delete]

    @classmethod
    def get_inline_manage_buttons_decision(cls):
        return BW_ACCESS_CREATE_MODIFY_DELETE

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete]

    @classmethod
    def default_order_by(cls):
        if 'last_updated' in [x.split(':')[0] for x in cls.table_columns()]:
            return '-last_updated'
        if 'transaction_time' in [x.split(':')[0] for x in cls.table_columns()]:
            return '-transaction_time'
        if 'visit_time' in [x.split(':')[0] for x in cls.table_columns()]:
            return '-visit_time'
        return '-date_created'

    @classmethod
    def sortable_columns(cls):
        return [cn.split(":")[0] for cn in cls.table_columns()]

    @classmethod
    def table_columns(cls):
        try:
            cls._meta.get_field('name')
            return 'code', 'name', 'last_updated'
        except Exception:
            pass
        return 'code', 'last_updated'

    @classmethod
    def get_table_class(cls, request=None, **kwargs):
        tab = getattr(request, 'tab', None)
        if tab is not None:
            if len(request.tab.inline_actions) > 0:
                inline = True
            else:
                inline = False

            if len(request.tab.actions) > 0:
                selection = True
            elif request.partial_view:
                selection = False
            else:
                selection = True
        else:
            inline = True
            selection = True

            # if not selection:
        attrs = dict()
        columns = cls.table_columns()
        if tab is None:
            attrs[columns[0]] = tables.LinkColumn(cls.get_route_name(action=ViewActionEnum.Details), args=[A('pk')])

        if inline:
            columns = cls.table_columns()
            if selection:
                attrs.update({
                    'actions': tables.TemplateColumn(
                        template_name='shared/display-templates/_manage_inline_action.html')
                })
            else:
                attrs.update({
                    'actions': tables.TemplateColumn(template_name='shared/display-templates/_inline_action.html')
                })

        is_printable = request.GET.get('printable', '0')
        if is_printable == '1':
            table_class = GenericPrintableTable
        else:
            table_class = GenericTable if selection else GenericInlineTable
        for f in columns:
            if f != 'code' and f != 'actions':
                if is_printable == '1':
                    attrs[f] = tables.Column(verbose_name=bw_titleize(f.replace('render_', '')), orderable=False)
                elif f.startswith('render_'):
                    _field_name = f.replace("render_", "")
                    try:
                        _field = cls._meta.get_field(_field_name)
                    except:
                        _field = None
                    if not _field:
                        order_by_enabled = False
                        if f in cls.sortable_columns():
                            field_name = f.replace("render_", "")
                            if hasattr(cls, "order_by_%s" % field_name):
                                order_by_enabled = True
                        if order_by_enabled:
                            attrs[f] = tables.Column(verbose_name=bw_titleize(bw_special_chars(f)), order_by=f,
                                                     orderable=True)
                        else:
                            attrs[f] = tables.Column(verbose_name=bw_titleize(bw_special_chars(f)), orderable=False)
                    else:
                        if isinstance(f, models.ForeignKey) or isinstance(f, models.ManyToManyField):
                            order_by_enabled = False
                            if f in cls.sortable_columns():
                                field_name = f.replace("render_", "")
                                if hasattr(cls, "order_by_%s" % field_name):
                                    order_by_enabled = True
                            if order_by_enabled:
                                attrs[f] = tables.Column(verbose_name=bw_titleize(bw_special_chars(f)),
                                                         order_by=f, orderable=True)
                            else:
                                attrs[f] = tables.Column(verbose_name=bw_titleize(bw_special_chars(f)), orderable=False)
                        else:
                            attrs[f] = tables.Column(
                                verbose_name=bw_titleize(bw_special_chars(f)), order_by=_field_name,
                                orderable=f in cls.sortable_columns())
                else:
                    f_name = f.split(':')
                    attrs[f_name[0]] = tables.Column(
                        verbose_name=bw_titleize(bw_special_chars(f_name[len(f_name) - 1])), order_by=f_name[0],
                        orderable=f_name[0] in cls.sortable_columns())

        class Meta(table_class.Meta):
            model = cls
            fields = [x.split(':')[0] for x in columns]

        attrs['Meta'] = Meta
        klass = type('DynamicTable', (table_class,), attrs)
        return klass
