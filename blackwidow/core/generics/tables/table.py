import itertools

from blackwidow.engine.extensions.clock import Clock


__author__ = 'mahmudul'

import django_tables2 as tables


class GenericTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor='pk', attrs={'td__input': {'class': 'checkbox checksingle'}, 'td': {'class': 'checktogglercontainer'}, 'th__input': {'data-checktogglercontainer': 'checktogglercontainer', 'data-checktoggler': 'checksingle', 'class': 'checkbox checkalltoggle' ,'name': 'checkall-toggle'}})
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = itertools.count()

    def render_serial(self, **kwargs):
        value = next(self.counter)
        try:
            return '%d' % ((value + (self.page.number - 1) * self.paginator.per_page) + 1)
        except:
            return '%d' % (value + 1)

    def render_organization(self, **kwargs):
        return kwargs['value'].name

    def render_last_updated(self, **kwargs):
        if kwargs["value"] is not None:
            return Clock.get_user_local_time(value=kwargs["value"]).strftime('%d/%m/%Y - %I:%M %p')

    def render_date_created(self, **kwargs):
        if kwargs["value"] is not None:
            return Clock.get_user_local_time(value=kwargs["value"]).strftime('%d/%m/%Y - %I:%M %p')

    def render_start_time(self, **kwargs):
        if kwargs["value"] is not None:
            return Clock.get_user_local_time(value=kwargs["value"]).strftime('%d/%m/%Y - %I:%M %p')

    def render_end_time(self, **kwargs):
        if kwargs["value"] is not None:
            return Clock.get_user_local_time(value=kwargs["value"]).strftime('%d/%m/%Y - %I:%M %p')

    def render_transaction_time(self, **kwargs):
        if kwargs["value"] is not None:
            return Clock.get_user_local_time(value=kwargs["value"]).strftime('%d/%m/%Y - %I:%M %p')

    def render_visit_time(self, **kwargs):
        if kwargs["value"] is not None:
            return Clock.get_user_local_time(value=kwargs["value"]).strftime('%d/%m/%Y - %I:%M %p')

    class Meta:
        paginate = False
        sequence = ('selection',)
        # exclude = ("id", "created_by", "last_updated_by", "is_deleted", "is_active", "is_locked", "timestamp", "type")
        attrs = {"class": "table table-striped table-bordered table-condensed"}
