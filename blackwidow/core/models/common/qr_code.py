from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models, transaction
from rest_framework import serializers

from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock

__author__ = 'bahar'


@decorate(
    is_object_context,
    enable_import, enable_export,
    route(route='qr-codes', group_order=6, item_order=2, group='Other Admin',
          module=ModuleEnum.Settings, display_name="QR Code")
)
class QRCode(OrganizationDomainEntity):
    key = models.CharField(max_length=200, unique=True)
    value = models.CharField(max_length=1000)
    is_used = models.BooleanField(default=False)

    @property
    def render_key(self):
        return self.key.replace('<', '&lt;')

    def __str__(self):
        return str(self.pk) + ': ' + self.render_key

    @property
    def render_user(self):
        from blackwidow.core.models.users.user import ConsoleUser
        from blackwidow.core.models.clients.client import Client
        qr_user = None
        if ConsoleUser.objects.filter(qr_code__id=self.id).exists():
            qr_user = ConsoleUser.objects.get(qr_code__id=self.id)
        elif Client.objects.filter(qr_code__id=self.id):
            qr_user = Client.objects.get(qr_code__id=self.id)
        else:
            pass
        if qr_user:
            return qr_user
        else:
            return 'N/A'

    @classmethod
    def check_qr_code_is_valid(cls, qr_code_id, parent_instance=None,
                               id_type="pk",
                               request_device="WEB"):  ###id_type will be either pk or key, request_device = WEB/MOBILE
        if id_type != "pk" and id_type != "key":
            raise Exception(
                "Invalid parameter value. Parameter :id_type value should be either pk or key in check_qr_code_is_valid method in QRCode")
        if id_type == "pk":
            qrcodes = QRCode.objects.filter(pk=int(qr_code_id))
        else:
            qrcodes = QRCode.objects.filter(key=qr_code_id)
        qr_code = None
        if qrcodes.exists():
            qr_code = qrcodes.first()
            current_qr_code = parent_instance.qr_code if parent_instance and hasattr(parent_instance,
                                                                                     "qr_code") else None
            if qr_code.is_used:
                if current_qr_code:
                    if qr_code != current_qr_code:
                        if request_device == "WEB":
                            raise ValueError('QR Code already used.')
                        else:
                            return False
                else:
                    if request_device == "WEB":
                        raise ValueError('QR Code already used.')
                    else:
                        return False
            qr_code.is_used = True
            qr_code.save()
            return qr_code
        else:
            if request_device == "WEB":
                raise ObjectDoesNotExist('QR Code does not exist with id: %s ' % qr_code_id)
            else:
                return False

    @classmethod
    def table_columns(cls):
        return 'code', 'id', 'key', 'is_used', 'render_user', 'last_updated'

    @property
    def details_config(self):
        details = super().details_config
        details['key'] = self.render_key
        return details

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.Import:
            return "Import"
        return button

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedExport, ViewActionEnum.AdvancedImport]

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class Serializer(ss):
            key = serializers.CharField(max_length=500, required=False)
            value = serializers.CharField(max_length=500, required=False)
            is_used = serializers.BooleanField(required=False, default=False)

            def to_representation(self, value):
                if value is None:
                    return ""
                return super(Serializer, self).to_representation(value)

            def create(self, attrs):
                attrs.update({
                    'id': '' if attrs.get('reference_id', '') == '' else attrs.get('reference_id', '0')
                })
                if QRCode.objects.filter(key=attrs.get('key', '')).exists():
                    qr_code = QRCode.objects.filter(key=attrs.get('key', '')).first()
                    if qr_code.is_used:
                        raise ValidationError('QR Code already exists and assigned to another user/client.')
                    return qr_code
                elif QRCode.objects.filter(value=attrs.get('value', '')).exists():
                    qr_code = QRCode.objects.filter(value=attrs.get('value', '')).first()
                    if qr_code.is_used:
                        raise ValidationError('QR Code already exists and assigned to another user/client.')
                    return qr_code
                elif attrs.get('reference_id', '') != '' and QRCode.objects.filter(
                        id=int(attrs.get('reference_id', ''))).exists():
                    qr_code = QRCode.objects.filter(id=int(attrs.get('reference_id', ''))).first()
                    if qr_code.is_used:
                        raise ValidationError('QR Code already exists and assigned to another user/client.')
                    return qr_code
                return super().create(attrs)

            class Meta(ss.Meta):
                model = cls
                fields = ('id', 'code', 'key', 'value', 'is_used')

        return Serializer

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
        from blackwidow.core.models.config.importer_config import ImporterConfig
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        if result or importer_config.columns.count() == 0:
            importer_config.save(**kwargs)
        else:
            for items in importer_config.columns.all():
                items.delete()
        columns = [
            ImporterColumnConfig(column=0, column_name='key', property_name='key', ignore=False),
            ImporterColumnConfig(column=1, column_name='value', property_name='value', ignore=False),
        ]
        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        with transaction.atomic():
            org = user.organization
            qr_codes = QRCode.objects.filter(key=data['0'])
            if qr_codes.exists():
                qr_code = qr_codes[0]
            else:
                qr_code = QRCode()
                qr_code.organization = org
                qr_code.key = data['0']
                qr_code.value = data['1']
                qr_code.save()
            return qr_code.pk

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):

        start_column = 1

        workbook.merge_cells(start_row=row_number, start_column=start_column, end_row=row_number,
                             end_column=start_column + 2)
        workbook.cell(row=row_number, column=start_column + 2).value = 'Generated on: ' + str(
            Clock.now().strftime('%d-%m-%Y'))

        row_number += 2
        return workbook, row_number

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        exporter_configs = ExporterConfig.objects.filter(model=cls.__name__, organization=organization)
        if not exporter_configs.exists():
            exporter_config = ExporterConfig()
            exporter_config.save(**kwargs)
        else:
            for e in exporter_configs:
                e.delete()
            exporter_config = ExporterConfig()
            exporter_config.save(**kwargs)
        columns = [
            ExporterColumnConfig(column=0, column_name='Reference ID', property_name='id', ignore=False),
            ExporterColumnConfig(column=1, column_name='Qr Code', property_name='key', ignore=False),

        ]
        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        for column in columns:
            workbook.cell(row=row_number, column=column.column + 1).value = str(getattr(self, column.property_name))
        return self.pk, row_number + 1

    @classmethod
    def finalize_export(cls, workbook=None, row_number=None, query_set=None, **kwargs):
        file_name = 'FieldBuzz_QR_Codes' + (Clock.now().strftime('%d-%m-%Y'))
        return workbook, file_name
