import json
from collections import OrderedDict
from datetime import datetime, date

from django import forms
from django.db.models import Count, Max
from django.db.models.functions import Length
from django.db.models.query_utils import Q
from django.forms.forms import Form
from rest_framework import serializers

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models import ImporterConfig, ImporterColumnConfig, Organization, ExporterConfig, \
    ExporterColumnConfig, Geography, ContactAddress, ErrorLog
from blackwidow.core.models.structure.infrastructure_unit import InfrastructureUnit
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.constants.cache_constants import SITE_NAME_AS_KEY, ONE_HOUR_TIMEOUT
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = "Shama"


@decorate(save_audit_log, is_object_context, expose_api('primary-groups'), enable_import, enable_export,
          route(route='primary-groups', group='Social Mobilization and Community Capacity Building',
                module=ModuleEnum.Analysis,
                display_name='Primary Groups', group_order=2, item_order=8))
class PrimaryGroup(InfrastructureUnit):
    class Meta:
        app_label = 'nuprp_admin'
        proxy = True

    @classmethod
    def prefetch_objects(cls):
        return ["parent__address__geography__parent"]

    @property
    def render_division(self):
        try:
            return self.parent.address.geography.parent.parent.name
        except:
            return 'N/A'

    @property
    def render_city_corporation(self):
        try:
            return self.parent.address.geography.parent.name
        except:
            return 'N/A'

    @property
    def render_city_corporation_id(self):
        try:
            return self.parent.address.geography.parent.short_code
        except:
            return 'N/A'

    @property
    def render_cdc_id(self):
        try:
            return self.parent.assigned_code
        except:
            return 'N/A'

    @property
    def render_cdc_name(self):
        try:
            return self.parent.name
        except:
            return 'N/A'

    @property
    def render_cdc_formation_date(self):
        return self.parent.date_of_formation.strftime(
            '%d/%m/%Y') if self.parent and self.parent.date_of_formation else "N/A"

    @property
    def render_cdc_ward(self):
        _cdc = self.parent
        if _cdc:
            _address = _cdc.address
            if _address:
                return _address.geography.name if _address.geography_id and _address.geography.name else "N/A"
        return "N/A"

    @property
    def render_cluster_id(self):
        _cdc = self.parent
        if _cdc:
            _cluster = _cdc.parent
            if _cluster:
                return _cluster.assigned_code if _cluster.assigned_code else 'N/A'
        return 'N/A'

    @property
    def render_cluster_name(self):
        _cdc = self.parent
        if _cdc:
            _cluster = _cdc.parent
            if _cluster:
                return _cluster.name if _cluster.name else 'N/A'
        return 'N/A'

    @property
    def render_total_members(self):
        cache_key = SITE_NAME_AS_KEY + '_pg_members_' + str(self.pk)
        cached_member_count = CacheManager.get_from_cache_by_key(key=cache_key)
        if cached_member_count is None:
            cached_member_count = self.client_set.all().count()
            CacheManager.set_cache_element_by_key(key=cache_key, value=cached_member_count,
                                                  timeout=ONE_HOUR_TIMEOUT * 2)
        return cached_member_count

    @property
    def render_created_on(self):
        return self.date_of_formation.strftime(
            '%d/%m/%Y') if self.date_of_formation else super(PrimaryGroup, self).render_date_created

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(parent__address__geography__parent__name__icontains=value)

    @property
    def render_cdc(self):
        return self.parent if self.parent_id else "N/A"

    @classmethod
    def search_cdc(cls, queryset, value):
        return queryset.filter(parent__name__icontains=value)

    @classmethod
    def order_by_cdc(cls):
        return ['parent__name']

    @property
    def general_information(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['primary_group_ID'] = self.assigned_code
        details['CDC'] = self.parent
        details['city_corporation'] = self.render_city_corporation
        details['total_members'] = self.render_total_members
        details['date_of_formation'] = self.date_of_formation
        return details

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'name', 'assigned_code:Primary Group ID', 'render_cdc', 'render_total_members',
            'render_city_corporation', 'render_created_on', 'last_updated')

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        details['general_information'] = self.general_information
        details['other_information'] = self.other_information
        return details

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Primary Group Members(s)',
                access_key='members',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='nuprp_admin.PrimaryGroupMember',
                queryset=PrimaryGroupMember.get_role_based_queryset(queryset=PrimaryGroupMember.objects.filter()),
                queryset_filter=Q(**{'assigned_to_id': self.pk})
            )
        ]

    @property
    def select2_string(self):
        return self.assigned_code

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

        class PrimaryGroupSerializer(_InfrastructureUnitSerializer):
            member_count = serializers.SerializerMethodField()
            last_pg_member_no = serializers.SerializerMethodField()

            def __init__(self, *args, fields=None, context=None, **kwargs):
                super(PrimaryGroupSerializer, self).__init__(*args, fields=fields, context=context, **kwargs)

                cache_key = SITE_NAME_AS_KEY + '_pg_member_count_dict'
                cached_member_dict = CacheManager.get_from_cache_by_key(key=cache_key)
                if cached_member_dict is None:
                    member_queryset = PrimaryGroupMember.objects.using(
                        BWDatabaseRouter.get_read_database_name()).values(
                        'assigned_to_id').annotate(count=Count('pk'),
                                                   last_pg_member_no=Max('last_2_digits_of_assigned_code'))

                    self.member_dict = dict()
                    for member in member_queryset:
                        self.member_dict[member['assigned_to_id']] = {
                            'member_count': member['count'],
                            'last_pg_member_no': member['last_pg_member_no']
                        }
                    CacheManager.set_cache_element_by_key(
                        key=cache_key,
                        value=json.dumps(self.member_dict),
                        timeout=ONE_HOUR_TIMEOUT * 2
                    )
                else:
                    self.member_dict = json.loads(cached_member_dict)

            def get_member_count(self, obj):
                try:
                    return self.member_dict[obj.pk]['member_count']
                except:
                    try:
                        return self.member_dict[str(obj.pk)]['member_count']
                    except:
                        return 0

            def get_last_pg_member_no(self, obj):
                try:
                    return self.member_dict[obj.pk]['last_pg_member_no']
                except:
                    try:
                        return self.member_dict[str(obj.pk)]['last_pg_member_no']
                    except:
                        return 0

            class Meta:
                model = cls
                fields = 'id', 'tsync_id', 'name', 'assigned_code', 'parent', 'member_count', 'date_created', \
                         'last_updated', 'last_pg_member_no'

        return PrimaryGroupSerializer

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

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, created = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ImporterColumnConfig(column=0, column_name='Primary Group ID', property_name='assigned_code', ignore=False),
            ImporterColumnConfig(column=1, column_name='Primary Group Name', property_name='name', ignore=False),
            ImporterColumnConfig(column=2, column_name='Division Name', property_name='render_division', ignore=False),
            ImporterColumnConfig(column=3, column_name='City Corporation ID',
                                 property_name='render_city_corporation_id', ignore=False),
            ImporterColumnConfig(column=4, column_name='City Corporation Name', property_name='render_city_corporation',
                                 ignore=False),
            ImporterColumnConfig(column=5, column_name='Cluster ID', property_name='render_cluster_id', ignore=False),
            ImporterColumnConfig(column=6, column_name='Cluster Name', property_name='render_cluster_name',
                                 ignore=False),
            ImporterColumnConfig(column=7, column_name='CDC ID', property_name='render_cdc_id', ignore=False),
            ImporterColumnConfig(column=8, column_name='CDC Name', property_name='render_cdc_name', ignore=False),
            ImporterColumnConfig(column=9, column_name='Ward No', property_name='render_cdc_ward', ignore=False),
            ImporterColumnConfig(column=10, column_name='CDC Reformation Date',
                                 property_name='render_cdc_formation_date', ignore=False),
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def get_column_list(cls, items):
        _pg_ids = _pg_names = _division_names = _city_ids = _city_names = _cluster_ids = \
            _cluster_names = _cdc_ids = _cdc_names = _cdc_wards = _cdc_formation_date = []

        for data in items:
            primary_group_id = str(data['0']) if data['0'] else ''
            primary_group_name = str(data['1']) if data['1'] else ''
            division_name = str(data['2']) if data['2'] else ''
            city_id = str(data['3']) if data['3'] else ''
            city_name = str(data['4']) if data['4'] else ''
            cluster_id = str(data['5']) if data['5'] else ''
            cluster_name = str(data['6']) if data['6'] else ''
            cdc_id = str(data['7']) if data['7'] else ''
            cdc_name = str(data['8']) if data['8'] else ''
            cdc_ward = str(data['9']) if data['9'] else ''
            cdc_formation_date = str(data['10']) if data['10'] else ''

            if not cdc_id or not division_name or not city_id or not cdc_ward or not cluster_id or city_name or cdc_ward:
                continue

            _pg_ids.append(primary_group_id)
            _pg_names.append(primary_group_name)
            _division_names.append(division_name)
            _city_ids.append(city_id)
            _city_names.append(city_name)
            _cluster_ids.append(cluster_id)
            _cluster_names.append(cluster_name)
            _cdc_ids.append(cdc_id)
            _cdc_names.append(cdc_name)
            _cdc_wards.append(cdc_ward)
            _cdc_formation_date.append(cdc_formation_date)

        return _pg_ids, _pg_names, _division_names, _city_ids, _city_names, _cluster_ids, _cluster_names, _cdc_ids, \
               _cdc_names, _cdc_wards, _cdc_formation_date

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        _pg_ids, _pg_names, _division_names, _city_ids, _city_names, _cluster_ids, _cluster_names, _cdc_ids, \
        _cdc_names, _cdc_wards, _cdc_formation_date = cls.get_column_list(items)

        # TODO: Create City, Division, Primary group, CDC, CDC Cluster, Savings and credit group each in seprate funcition

        geography_queryset = Geography.objects.filter(type='Ward').values('parent__name', 'name', 'pk', 'parent_id')
        cdc_cluster_queryset = CDCCluster.objects.values('assigned_code', 'pk')
        cdc_queryset = CDC.objects.values('assigned_code', 'pk')
        pg_queryset = PrimaryGroup.objects.values('assigned_code', 'pk')
        pg_count_queryset = PrimaryGroup.all_objects.annotate(
            code_len=Length('assigned_code')
        ).filter(code_len=10).values('parent_id').annotate(count=Count('pk'))

        geography_dict = dict()
        cdc_cluster_dict = dict()
        cdc_dict = dict()
        pg_dict = dict()
        pg_count_dict = dict()
        city_corporation_dict = dict()

        for gq in geography_queryset:
            geography_dict[gq['parent__name'], gq['name']] = gq['pk']
            city_corporation_dict[gq['parent__name']] = gq['parent_id']

        for cq in cdc_cluster_queryset:
            cdc_cluster_dict[cq['assigned_code']] = cq['pk']
        for cq in cdc_queryset:
            cdc_dict[cq['assigned_code']] = cq['pk']
        for pq in pg_queryset:
            pg_dict[pq['assigned_code']] = pq['pk']
        for pq in pg_count_queryset:
            pg_count_dict[pq['parent_id']] = pq['count']

        organization = Organization.get_organization_from_cache()

        # Create CDC Cluster
        creatable_cdc_cluster_list = list()
        for data in items:
            primary_group_id = str(data['0']) if data['0'] else ''
            primary_group_name = str(data['1']) if data['1'] else ''
            division_name = str(data['2']) if data['2'] else ''
            city_id = str(data['3']) if data['3'] else ''
            city_name = str(data['4']) if data['4'] else ''
            cluster_id = str(data['5']) if data['5'] else ''
            cluster_name = str(data['6']) if data['6'] else ''
            cdc_id = str(data['7']) if data['7'] else ''
            cdc_name = str(data['8']) if data['8'] else ''
            cdc_ward = str(data['9']) if data['9'] else ''
            cdc_formation_date = str(data['10']) if data['10'] else ''

            if not cdc_id or not division_name or not city_id or not cdc_ward or not cluster_id:
                continue

            if (city_name, cdc_ward) not in geography_dict.keys():
                continue

            if city_name not in city_corporation_dict.keys():
                continue

            if cluster_id:
                if cluster_id not in cdc_cluster_dict.keys():
                    city_corporation_id = city_corporation_dict[city_name]
                    _address_obj = ContactAddress.objects.create(geography_id=city_corporation_id)
                    cdc_cluster = CDCCluster(
                        assigned_code=cluster_id, organization_id=organization.id,
                        name=cluster_name, remarks='Old', address=_address_obj,
                        date_created=Clock.timestamp(), type=CDCCluster.__name__
                    )
                    creatable_cdc_cluster_list.append(cdc_cluster)
                    cdc_cluster_dict[cluster_id] = None

        if len(creatable_cdc_cluster_list) > 0:
            CDCCluster.objects.bulk_create(creatable_cdc_cluster_list)
            CDCCluster.generate_missing_codes()
        cdc_cluster_queryset = CDCCluster.objects.using(BWDatabaseRouter.get_default_database_name()).values(
            'assigned_code', 'pk')
        cdc_cluster_dict = dict()
        for cq in cdc_cluster_queryset:
            cdc_cluster_dict[cq['assigned_code']] = cq['pk']

        # Create CDC
        creatable_cdc_list = list()
        for data in items:
            primary_group_id = str(data['0']) if data['0'] else ''
            primary_group_name = str(data['1']) if data['1'] else ''
            division_name = str(data['2']) if data['2'] else ''
            city_id = str(data['3']) if data['3'] else ''
            city_name = str(data['4']) if data['4'] else ''
            cluster_id = str(data['5']) if data['5'] else ''
            cluster_name = str(data['6']) if data['6'] else ''
            cdc_id = str(data['7']) if data['7'] else ''
            cdc_name = str(data['8']) if data['8'] else ''
            cdc_ward = str(data['9']) if data['9'] else ''
            cdc_formation_date = str(data['10']) if data['10'] else ''

            if not cdc_id or not division_name or not city_id or not cdc_ward or not cluster_id:
                continue

            if (city_name, cdc_ward) not in geography_dict.keys():
                continue

            if cdc_id:
                try:
                    if cdc_id not in cdc_dict.keys():
                        ward_id = geography_dict[(city_name, cdc_ward)]
                        _address_obj = ContactAddress.objects.create(geography_id=ward_id)
                        cdc = CDC(
                            assigned_code=cdc_id, organization_id=organization.id, date_created=Clock.timestamp(),
                            name=cdc_name, remarks='Old', parent_id=cdc_cluster_dict[cluster_id],
                            address=_address_obj, type=CDC.__name__
                        )
                        cdc_dict[cdc_id] = None
                        if cdc_formation_date:
                            try:
                                cdc.date_of_formation = datetime.strptime(cdc_formation_date, '%d/%m/%Y')
                            except:
                                pass
                        creatable_cdc_list.append(cdc)
                except Exception as exp:
                    ErrorLog.log(exp=exp)

        if len(creatable_cdc_list) > 0:
            CDC.objects.bulk_create(creatable_cdc_list)
            CDC.generate_missing_codes()

        cdc_queryset = CDC.objects.using(BWDatabaseRouter.get_default_database_name()).values('assigned_code', 'pk')
        cdc_dict = dict()
        for cq in cdc_queryset:
            cdc_dict[cq['assigned_code']] = cq['pk']

        # Create PG
        creatable_pg_list = list()
        for data in items:
            primary_group_id = str(data['0']) if data['0'] else ''
            primary_group_name = str(data['1']) if data['1'] else ''
            division_name = str(data['2']) if data['2'] else ''
            city_id = str(data['3']) if data['3'] else ''
            city_name = str(data['4']) if data['4'] else ''
            cluster_id = str(data['5']) if data['5'] else ''
            cluster_name = str(data['6']) if data['6'] else ''
            cdc_id = str(data['7']) if data['7'] else ''
            cdc_name = str(data['8']) if data['8'] else ''
            cdc_ward = str(data['9']) if data['9'] else ''
            cdc_formation_date = str(data['10']) if data['10'] else ''

            if not cdc_id or not division_name or not city_id or not cdc_ward or not cluster_id:
                continue

            if (city_name, cdc_ward) not in geography_dict.keys():
                continue
            try:
                if not primary_group_id:
                    pg_count_dict[cdc_dict[cdc_id]] += 1
                    pg_serial = str(pg_count_dict[cdc_dict[cdc_id]])

                    if len(pg_serial) < 2:
                        pg_serial = '0' + pg_serial
                    primary_group_id = '%s%2s' % (cdc_id, pg_serial)

                if primary_group_id not in pg_dict.keys():
                    pg = PrimaryGroup(
                        assigned_code=primary_group_id, parent_id=cdc_dict[cdc_id], organization=organization,
                        date_created=Clock.timestamp(), name=primary_group_name, type=PrimaryGroup.__name__)
                    pg_dict[primary_group_id] = None
                    creatable_pg_list.append(pg)
            except Exception as exp:
                ErrorLog.log(exp=exp)
        if len(creatable_pg_list) > 0:
            PrimaryGroup.objects.bulk_create(creatable_pg_list)
            PrimaryGroup.generate_missing_codes()

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='Primary Group ID', property_name='assigned_code', ignore=False),
            ExporterColumnConfig(column=1, column_name='Primary Group Name', property_name='name', ignore=False),
            ExporterColumnConfig(column=2, column_name='Division Name', property_name='render_division', ignore=False),
            ExporterColumnConfig(column=3, column_name='City Corporation ID',
                                 property_name='render_city_corporation_id', ignore=False),
            ExporterColumnConfig(column=4, column_name='City Corporation Name', property_name='render_city_corporation',
                                 ignore=False),
            ExporterColumnConfig(column=5, column_name='Cluster ID', property_name='render_cluster_id', ignore=False),
            ExporterColumnConfig(column=6, column_name='Cluster Name', property_name='render_cluster_name',
                                 ignore=False),
            ExporterColumnConfig(column=7, column_name='CDC ID', property_name='render_cdc_id', ignore=False),
            ExporterColumnConfig(column=8, column_name='CDC Name', property_name='render_cdc_name', ignore=False),
            ExporterColumnConfig(column=9, column_name='Ward No', property_name='render_cdc_ward', ignore=False),
            ExporterColumnConfig(column=10, column_name='Total member No', property_name='render_total_members',
                                 ignore=False),
            ExporterColumnConfig(column=11, column_name='CDC Reformation Date',
                                 property_name='render_cdc_formation_date', ignore=False),
            ExporterColumnConfig(column=11, column_name='Created on', property_name='render_created_on',
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
        if target_year:
            _from_datetime = datetime(year=target_year, month=1, day=1).timestamp() * 1000
            _to_datetime = datetime(year=target_year + 1, month=1, day=1).timestamp() * 1000 - 1
            queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        if city_ids:
            queryset = queryset.filter(parent__address__geography__parent__id__in=city_ids)

        for _object in queryset:
            for column in columns:
                column_value = ''
                if hasattr(_object, column.property_name):
                    column_value = str(getattr(_object, column.property_name))

                workbook.cell(row=row_number, column=column.column + 1).value = column_value
            row_number += 1

        return workbook, row_number
