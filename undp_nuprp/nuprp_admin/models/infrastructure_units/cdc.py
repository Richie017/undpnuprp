from collections import OrderedDict
from datetime import datetime, date

from django.db import transaction
from django.db.models import Count
from django.db.models.functions import Length
from django.db.models.query_utils import Q
from rest_framework import serializers
from django import forms
from django.forms.forms import Form

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import ExporterConfig, ExporterColumnConfig, ImporterConfig, ImporterColumnConfig, \
    Geography, Organization, GeographyLevel, ContactAddress
from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_caching import enable_caching
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = "Shama"


@decorate(save_audit_log, is_object_context, enable_caching(), expose_api('cdc'), enable_export, enable_import,
          route(route='cdc', group='Social Mobilization and Community Capacity Building', module=ModuleEnum.Analysis,
                display_name='CDC', group_order=2, item_order=9))
class CDC(InfrastructureUnit):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    def to_model_data(self):
        model_data = super(CDC, self).to_model_data()
        model_data['id'] = self.pk
        model_data['name'] = self.name
        model_data['parent'] = self.parent_id
        model_data['city_id'] = self.address.geography.parent_id if self.address.geography.parent is not None else None
        return model_data

    @property
    def render_division(self):
        return self.address.geography.parent.parent.name \
            if self.address and self.address.geography and \
               self.address.geography.parent and \
               self.address.geography.parent.parent else 'N/A'

    @property
    def render_city_corporation(self):
        return self.address.geography.parent.name if self.address and self.address.geography and \
                                                     self.address.geography.parent else 'N/A'

    @property
    def render_ward(self):
        return self.address.geography.name if self.address and self.address.geography else 'N/A'

    @property
    def render_total_PG(self):
        return self.infrastructureunit_set.all().count()

    @property
    def render_total_CDC_member(self):
        return PrimaryGroupMember.objects.filter(assigned_to__parent_id=self.pk).count()

    @property
    def render_total_SCG(self):
        from undp_nuprp.nuprp_admin.models import SavingsAndCreditGroup
        return SavingsAndCreditGroup.objects.filter(primary_group__parent_id=self.pk).count()

    @property
    def render_community_facilitator(self):
        cf = ConsoleUser.objects.using(BWDatabaseRouter.get_read_database_name()).filter(assigned_to_id=self.pk).first()
        return cf if cf else 'N/A'

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(address__geography__parent__name__icontains=value)

    @classmethod
    def table_columns(cls):
        return ['render_code', 'name', 'assigned_code:CDC ID', 'date_of_formation:Formation Date',
                'render_city_corporation', 'render_total_CDC_member', 'render_total_PG', 'render_total_SCG',
                'date_created:Created On', 'last_updated']

    @property
    def general_information(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['type'] = self.remarks
        details['formation_date'] = self.date_of_formation
        details['assigned_community_facilitator'] = self.render_community_facilitator
        details['CDC_cluster'] = self.parent
        details['city_corporation'] = self.render_city_corporation
        details['CDC_ID'] = self.assigned_code
        details['Ward'] = self.address.geography.select2_string if self.address and self.address.geography else "N/A"
        details['primary_groups'] = self.render_total_PG
        details['location'] = self.address.location
        return details

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        details['general_information'] = self.general_information
        details['other_information'] = self.other_information
        return details

    @classmethod
    def get_button_title(cls, button):
        if button == ViewActionEnum.AdvancedExport:
            return 'Export'
        if button == ViewActionEnum.AdvancedImport:
            return 'Import'
        return 'N/A'

    @classmethod
    def get_manage_buttons(cls):
        manage_buttons = InfrastructureUnit.get_manage_buttons()
        return manage_buttons + [ViewActionEnum.AdvancedExport, ViewActionEnum.AdvancedImport]

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Primary Group(s)',
                access_key='primary_group',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='nuprp_admin.PrimaryGroup',
                queryset_filter=Q(**{'pk__in': self.infrastructureunit_set.values_list('pk', flat=True)})
            ),
            TabView(
                title='Primary Group Member(s)',
                access_key='primary_group_member',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='nuprp_admin.PrimaryGroupMember',
                queryset_filter=Q(**{'assigned_to__parent_id': self.pk})
            )
        ]

    @classmethod
    def get_export_dependant_fields(cls):

        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                today = date.today()
                year_choices = tuple()
                for y in range(2000, 2100):
                    year_choices += ((y, str(y)),)

                self.fields['city'] = \
                    GenericModelChoiceField(
                        queryset=Geography.objects.filter(level__name='Pourashava/City Corporation'),
                        label='Select City',
                        required=False,
                        widget=forms.Select(
                            attrs={
                                'class': 'select2 kpi-filter',
                                'width': '220',
                                'data-kpi-filter-role': 'city'
                            }
                        )
                    )

                self.fields['year'] = forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )

        return AdvancedExportDependentForm

    @classmethod
    def get_serializer(cls):
        _InfrastructureUnitSerializer = InfrastructureUnit.get_serializer()

        class CDCSerializer(_InfrastructureUnitSerializer):
            members = serializers.SerializerMethodField()
            total_scg = serializers.SerializerMethodField()
            date_of_formation = serializers.SerializerMethodField()

            def __init__(self, *args, fields=None, context=None, **kwargs):
                from undp_nuprp.nuprp_admin.models import PrimaryGroupMember, SavingsAndCreditGroup

                super(CDCSerializer, self).__init__(*args, fields=fields, context=context, **kwargs)
                member_queryset = PrimaryGroupMember.objects.using(BWDatabaseRouter.get_read_database_name()).values(
                    'assigned_to__parent_id').annotate(count=Count('pk', distinct=True))
                scg_queryset = SavingsAndCreditGroup.objects.using(BWDatabaseRouter.get_read_database_name()).values(
                    'primary_group__parent_id').annotate(count=Count('pk', distinct=True))

                self.member_dict = dict()
                for member in member_queryset:
                    self.member_dict[member['assigned_to__parent_id']] = member['count']
                self.scg_dict = dict()
                for scg in scg_queryset:
                    self.scg_dict[scg['primary_group__parent_id']] = scg['count']

            def get_date_of_formation(self, obj):
                try:
                    if obj.date_of_formation:
                        formation_date = obj.date_of_formation
                    else:
                        formation_date = ''
                    return formation_date
                except:
                    return ''

            def get_members(self, obj):
                try:
                    return self.member_dict[obj.pk]
                except:
                    return 0

            def get_total_scg(self, obj):
                try:
                    return self.scg_dict[obj.pk]
                except:
                    return 0

            class Meta:
                model = cls
                fields = 'id', 'tsync_id', 'name', 'parent', 'date_of_formation', 'assigned_code', \
                         'members', 'total_scg', 'date_created', 'last_updated'

        return CDCSerializer

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, created = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ImporterColumnConfig(column=0, column_name='CDC ID', property_name='assigned_code', ignore=False),
            ImporterColumnConfig(column=1, column_name='CDC Name', property_name='name', ignore=False),
            ImporterColumnConfig(column=2, column_name='Division', property_name='render_division', ignore=False),
            ImporterColumnConfig(column=3, column_name='City Corporation', property_name='render_city_corporation',
                                 ignore=False),
            ImporterColumnConfig(column=4, column_name='Ward', property_name='render_ward',
                                 ignore=False),
            ImporterColumnConfig(column=5, column_name='Date of Formation',
                                 property_name='date_of_formation', ignore=False),
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        cdc_id = str(data['0']) if data['0'] else ''
        cdc_name = str(data['1'])
        division = str(data['2'])
        city = str(data['3'])
        ward = str(data['4'])
        date_of_formation = str(data['5']) if data['5'] else ''

        organization = Organization.objects.first()

        with transaction.atomic():
            country, created = Geography.objects.get_or_create(
                name='Bangladesh', parent=None, level_id=GeographyLevel.objects.filter(name='Country').first().pk,
                type='Country', organization=organization)

            if division:
                division, created = Geography.objects.get_or_create(
                    name=division, parent=country, level_id=GeographyLevel.objects.filter(name='Division').first().pk,
                    type='Division', organization=organization)

                if city:
                    city, created = Geography.objects.get_or_create(
                        name=city, parent=division,
                        level_id=GeographyLevel.objects.filter(name='Pourashava/City Corporation').first().pk,
                        type='Pourashava/City Corporation', organization=organization)

                    if ward:
                        ward, created = Geography.objects.get_or_create(
                            name=ward, parent=city,
                            level_id=GeographyLevel.objects.filter(name='Ward').first().pk,
                            type='Ward', organization=organization)

                        if not cdc_id:
                            ward_code = ward.name
                            city_code = city.short_code
                            cdc_number = CDC.all_objects.annotate(code_len=Length('assigned_code')).filter(
                                address__geography__pk=ward.pk, code_len=8).count()
                            if len(ward_code) < 2:
                                ward_code = '0' + ward_code
                            if len(city_code) < 3:
                                city_code = '0' + city_code
                            cdc_serial = str((cdc_number + 1) % 1000)
                            if len(cdc_serial) <= 2:
                                cdc_serial = cdc_serial.zfill(3)
                            cdc_id = '%3s%2s%3s' % (city_code, ward_code, cdc_serial)

                        cdc, created = CDC.objects.get_or_create(name=cdc_name, assigned_code=cdc_id,
                                                                 organization=organization)
                        if date_of_formation:
                            df = datetime.strptime(date_of_formation, '%m/%Y')
                            cdc.date_of_formation = df
                        address = cdc.address if cdc.address else ContactAddress()
                        address.geography = ward
                        address.save()
                        cdc.address = address
                        cdc.save()
        return data

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='CDC ID', property_name='assigned_code', ignore=False),
            ExporterColumnConfig(column=1, column_name='CDC Name', property_name='name', ignore=False),
            ExporterColumnConfig(column=2, column_name='Division', property_name='render_division', ignore=False),
            ExporterColumnConfig(column=3, column_name='City Corporation', property_name='render_city_corporation',
                                 ignore=False),
            ExporterColumnConfig(column=4, column_name='Ward', property_name='render_ward',
                                 ignore=False),
            ExporterColumnConfig(column=5, column_name='Total CDC Member', property_name='render_total_CDC_member',
                                 ignore=False),
            ExporterColumnConfig(column=6, column_name='Date of Formation',
                                 property_name='date_of_formation', ignore=False),
            ExporterColumnConfig(column=7, column_name='Created on', property_name='render_date_created',
                                 ignore=False),
            ExporterColumnConfig(column=8, column_name='Total PG', property_name='render_total_PG',
                                 ignore=False)
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        return self.pk, row_number + 1

    @classmethod
    def finalize_export(cls, workbook=None, row_number=None, query_set=None, **kwargs):
        return workbook

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):

        for column in columns:
            workbook.cell(row=1, column=column.column + 1).value = column.column_name

        row_number += 1

        query_params = kwargs.get('query_params')
        _today = date.today()
        target_year = int(query_params.get('year', _today.year))
        city_param = query_params.get('city', None)

        city_ids = None
        if city_param:
            city_ids = [int(x) for x in city_param.split(',')]

        queryset = cls.objects.using(BWDatabaseRouter.get_export_database_name()).all()

        if city_ids:
            queryset = queryset.filter(address__geography__parent__id__in=city_ids)

        if target_year:
            _from_datetime = datetime(year=target_year, month=1, day=1).timestamp() * 1000
            _to_datetime = datetime(year=target_year + 1, month=1, day=1).timestamp() * 1000 - 1
            queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        for cdc in queryset:
            for column in columns:
                column_value = ''
                if hasattr(cdc, column.property_name):
                    column_value = str(getattr(cdc, column.property_name))

                workbook.cell(row=row_number, column=column.column + 1).value = column_value
            row_number += 1

        return workbook, row_number

    def get_choice_name(self):
        return self.name
