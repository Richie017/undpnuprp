from collections import OrderedDict

from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

__author__ = 'Mahmud'


class DetailsViewModelMixin(object):
    @property
    def tabs_config(self):
        return [
        ]

    @property
    def name_property(self):
        return getattr(self, 'name', '')

    def __str__(self):
        fields = self._meta.fields
        name_field = [x for x in fields if x.name == 'name']

        text = ''
        if len(name_field) > 0:
            text = str(self.code) + ": " + str(self.name)
        else:
            text = self.code
        try:
            _c = self.get_leaf_class(label=self.type)
            if _c is None:
                _c = self.__class__
            if ViewActionEnum.Details in _c.get_routes():
                return mark_safe("<a class='inline-link' href='" + reverse(_c.get_route_name(ViewActionEnum.Details),
                                                                           kwargs={
                                                                               'pk': self.pk}) + "' >" + text + "</a>")
        except:
            return text
        return text

    def get_version_detail_link(self):
        if hasattr(self, "get_base_level_class"):
            return mark_safe("<a class='inline-link' target='_blank' href='/" + self.__class__.get_model_meta(
                'route', 'route') + '/' + ViewActionEnum.ProxyLevel.value + '/' +
                             self.type + '/' + ViewActionEnum.Details.value + '/' + str(
                self.pk) + "/' >" + self.render_timestamp(self.last_updated) + "</a>")

        _c = self.get_leaf_class(label=self.type)
        if _c is None:
            _c = self.__class__
        return mark_safe(
            "<a class='inline-link' target='_blank' href='" + reverse(_c.get_route_name(ViewActionEnum.Details),
                                                                      kwargs={
                                                                          'pk': self.pk}) + "' >" + self.render_timestamp(
                self.last_updated) + "</a>")

    @classmethod
    def get_datetime_fields(cls):
        return ['date_created', 'last_updated']

    def render_timestamp(self, value):
        _d = Clock.get_user_local_time(value).strftime("%d/%m/%Y - %I:%M %p")
        return _d

    @classmethod
    def details_view_fields(cls):
        """
        this method is used to get the list of fields used in the details view
        :return: list of strings (names of fields in details view)
        """
        return [field.name for field in cls._meta.fields]

    @property
    def details_config(self):
        """
        This methos is used to prepare key-value pairs for showing data in details view
        :return: OrderedDict instance (key value pairs for details view)
        """
        fields = self.__class__.details_view_fields()

        datetime_fields = self.__class__.get_datetime_fields()  # to check if rendering date from timestamp is required

        details = OrderedDict()  # this will be the final dictionary for fields
        groups = OrderedDict()  # this dictionary is for support grouping of fields

        for f in fields:
            property_name = f.split('>')[0].split(':')[0]
            display_name = f.split('>')[0].split(':')[1] if ':' in f else property_name
            if display_name.startswith('render_'):
                display_name = display_name.replace('render_', '')
            group_name = f.split('>')[1] if '>' in f else ''

            value = getattr(self, property_name, 'N/A')

            if value is None or value == '':
                value = 'N/A'

            if property_name in datetime_fields:
                value = self.render_timestamp(value)

            assign_to_dict = details
            if group_name:
                if group_name in groups.keys():
                    assign_to_dict = groups[group_name]
                else:
                    assign_to_dict = OrderedDict()
                    groups[group_name] = assign_to_dict
            assign_to_dict[display_name] = value
        for key, dict_item in groups.items():
            details[key] = dict_item

        return details

    def merge_dicts(self, *dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    @property
    def render_versions(self):
        if not self.is_version:
            versions = ''
            version_objects = self.__class__.version_objects.filter(master_version_id=self.pk).order_by('-pk')
            version_count = version_objects.count()
            for index, version in enumerate(version_objects):
                versions += mark_safe(version.get_version_detail_link()) + ' '
            show_version_button = '<div style="min-width:200px;"><a class="show-version-links-button text-primary"><u>Click to see previous version(s)</u><br>' + str(
                version_count) + ' previous version</a></div>'
            versions = mark_safe(
                show_version_button + '<div style="display:none;">' + versions + '</div>') if versions != '' else 'No Version Saved Yet'
            return versions
