from django.db import models
from rest_framework import serializers

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.file.fileobject import FileObject
from blackwidow.core.models.file.imagefileobject import ImageFileObject
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.field_type_enum import FieldTypesEnum
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize

__author__ = 'Mahmud'


@decorate(is_object_context,
          route(route='custom-fields', display_name='Custom Field', module=ModuleEnum.Settings, group='Common'))
class CustomField(DomainEntity):
    parent = models.ForeignKey('core.CustomField', null=True)
    assigned_code = models.CharField(max_length=128, blank=True)
    name = models.CharField(max_length=200)
    name_bd = models.CharField(max_length=200, blank=True)
    field_type = models.CharField(max_length=500, choices=FieldTypesEnum.get_field_types_choices(), default=None)
    is_required = models.BooleanField(default=False)
    list_values = models.TextField(help_text='For list fields only. Enter one option per line.', blank=True, null=True)
    list_values_bd = models.TextField(help_text='For list fields only. Enter one option per line.', blank=True,
                                      null=True)
    field_group = models.ForeignKey('core.FieldGroup', null=True)
    weight = models.IntegerField(default=100)
    related_model_name = models.CharField(max_length=128, blank=True)
    reachout_level = models.IntegerField(default=0)
    formula = models.CharField(max_length=512, blank=True)

    @property
    def choices_as_array(self):
        from io import StringIO
        value_buffer = StringIO(self.list_values)
        choices = [(item.strip(), bw_titleize(item.strip())) for item in value_buffer.readlines()]
        choices.insert(0, ('', '---------'))
        value_buffer.close()
        return choices

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            options = serializers.SerializerMethodField()
            options_bd = serializers.SerializerMethodField()

            def get_options(self, obj):
                if obj.list_values:
                    return obj.list_values.split('\n')
                return []

            def get_options_bd(self, obj):
                if obj.list_values_bd:
                    return obj.list_values_bd.split('\n')
                return []

            class Meta(ss.Meta):
                model = cls
                fields = (
                    'id', 'type', 'name', 'name_bd', 'assigned_code', 'field_type', 'is_required', 'options',
                    'options_bd', 'field_group', 'weight', 'formula', 'last_updated'
                )

        return Serializer

    @classmethod
    def table_columns(cls):
        return 'render_code', 'name', 'name_bd', 'model_name', 'last_updated_by', 'last_updated:Last Updated On'

    @property
    def get_inline_manage_buttons(self, **kwargs):
        return [
            dict(
                name='Edit',
                action='edit',
                icon='icon-pencil',
                ajax='1',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.PartialEdit,
                                                       parent=self.role_set.model.__name__.lower()),
                classes='manage-action load-modal',
                parent=self.role_set.all()[0]
            )
        ]


class CustomFieldValue(DomainEntity):
    value = models.CharField(max_length=8000, null=True)
    field = models.ForeignKey(CustomField)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'tsync_id', 'field', 'value')

        return Serializer


class CustomImageFieldValue(DomainEntity):
    value = models.ForeignKey(ImageFileObject, null=True)
    field = models.ForeignKey(CustomField)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            name = serializers.CharField(required=True, write_only=True)
            value = ImageFileObject.get_serializer()

            class Meta(ss.Meta):
                model = cls
                fields = ('name', 'value')

        return Serializer


class CustomDocumentFieldValue(DomainEntity):
    value = models.ForeignKey(FileObject, null=True)
    field = models.ForeignKey(CustomField)

    @classmethod
    def get_serializer(cls):
        ss = DomainEntity.get_serializer()

        class Serializer(ss):
            name = serializers.CharField(required=True, write_only=True)
            value = FileObject.get_serializer()

            class Meta(ss.Meta):
                model = cls
                fields = ('name', 'value')

        return Serializer
