from django.db import models
from django.utils.safestring import mark_safe

from blackwidow.core.mixins.modelmixin.export_model_mixin import ExportModelMixin
from blackwidow.core.models.common.location import Location
from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.enums.view_action_enum import ViewActionEnum

__author__ = 'Mahmud'


# @decorate(enable_export, enable_map, is_object_context, route(route='transport-allowances', module=ModuleEnum.CRM, display_name='Transport Allowance', group='TA'))
class TransportAllowance(OrganizationDomainEntity, ExportModelMixin):
    transport_type = models.CharField(max_length=200, null=True)
    fair = models.DecimalField(decimal_places=2, max_digits=10, null=True)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)

    @classmethod
    def get_dependent_field_list(cls):
        return ['location']

    @property
    def location_latitude(self):
        return self.location.latitude

    @property
    def location_longitude(self):
        return self.location.longitude

    @property
    def location_accuracy(self):
        return self.location.accuracy

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.Export]

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        '''
           production code
        '''
        # exporter_config, result = ExporterConfig.objects.filter(model=cls.__name__, organization=organization)
        # if result or exporter_config.columns.count() == 0:
        #  exporter_config.save(**kwargs)
        '''
        end production code
        '''
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
            ExporterColumnConfig(column=0, column_name='TA Id', property_name='reference_id', ignore=False),
            ExporterColumnConfig(column=1, column_name='TA Type', property_name='transport_type', ignore=False),
            ExporterColumnConfig(column=2, column_name='Fair', property_name='fair', ignore=False),
            ExporterColumnConfig(column=3, column_name='Latitude', property_name='location_latitude', ignore=False),
            ExporterColumnConfig(column=4, column_name='Longitude', property_name='location_longitude', ignore=False),
            ExporterColumnConfig(column=5, column_name='Accuracy', property_name='location_accuracy', ignore=False),
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
        total_fair = 0
        for item in query_set:
            total_fair += item.fair
        workbook.cell(row=row_number, column=3).value = 'Total=' + str(total_fair)
        return workbook

    def __str__(self):
        result = self.transport_type + ": " + str(self.fair)
        result += ", location: " + str(self.location)
        return result

    def render_employee(self):
        return self.created_by

    @classmethod
    def table_columns(cls):
        return 'code', 'created_by:employee', 'transport_type', 'fair', 'location', 'date_created:date_submitted'

    def get_map_view_data(self):
        return dict(
            name=str(self),
            description=mark_safe(self.transport_type + ': ' + str(self.fair) + '</br>' + str(self.location)),
            location=self.location.to_json()
        )

    @classmethod
    def get_serializer(cls):
        ss = OrganizationDomainEntity.get_serializer()

        class ODESerializer(ss):
            location = Location.get_serializer()(required=True)

            class Meta(ss.Meta):
                model = cls
                depth = 1

        return ODESerializer
