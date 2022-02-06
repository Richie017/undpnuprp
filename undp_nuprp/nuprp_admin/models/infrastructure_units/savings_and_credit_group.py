import json
import uuid
from collections import OrderedDict
from datetime import datetime, date

from django.db import models
from django.db.models import Count
from django.db.models.query_utils import Q
from django import forms
from django.forms.forms import Form
from django.utils.safestring import mark_safe
from rest_framework import serializers
from unidecode import unidecode

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models import ImporterConfig, ImporterColumnConfig, Geography, GeographyLevel, \
    ExporterConfig, ExporterColumnConfig, MaxSequence
from blackwidow.core.models import Organization
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.users.user import ConsoleUser
from blackwidow.core.viewmodels.tabs_config import TabView, TabViewAction
from blackwidow.engine.constants.cache_constants import SITE_NAME_AS_KEY, ONE_HOUR_TIMEOUT
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import partial_route
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.decorators.utility import save_audit_log
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember

__author__ = "Shama, Ziaul Haque"


@decorate(save_audit_log, is_object_context, expose_api('savings-and-credit-groups'), enable_export, enable_import,
          route(route='savings-and-credit-groups', group='Social Mobilization and Community Capacity Building',
                module=ModuleEnum.Analysis,
                display_name='Savings & Credit Groups', group_order=2, item_order=7),
          partial_route(relation=['normal'], models=[PrimaryGroupMember]))
class SavingsAndCreditGroup(OrganizationDomainEntity):
    name = models.CharField(max_length=200)
    address = models.ForeignKey(ContactAddress, null=True, on_delete=models.SET_NULL)
    primary_group = models.ForeignKey(PrimaryGroup, null=True, on_delete=models.SET_NULL)
    scg_report = models.ForeignKey('nuprp_admin.SavingsAndCreditReport', null=True, on_delete=models.SET_NULL)
    date_of_formation = models.DateTimeField(default=None, null=True)
    members = models.ManyToManyField('nuprp_admin.PrimaryGroupMember')

    def __init__(self, *args, **kwargs):
        super(SavingsAndCreditGroup, self).__init__(*args, **kwargs)
        from undp_nuprp.nuprp_admin.models.reports.savings_and_credit_report import SavingsAndCreditReport
        self.cumulative_report = SavingsAndCreditReport.objects.filter(scg_id=self.pk, type='CumulativeReport').first()

    class Meta:
        app_label = 'nuprp_admin'

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_formation_date(self):
        return self.date_of_formation.strftime("%d/%m/%Y") if self.date_of_formation else "N/A"

    @property
    def render_division(self):
        return self.address.geography.parent.name if self.address and self.address.geography else "N/A"

    @property
    def render_city_corporation(self):
        return self.address.geography.name if self.address else 'N/A'

    @classmethod
    def search_city_corporation(cls, queryset, value):
        return queryset.filter(address__geography__name__icontains=value)

    @property
    def render_total_member(self):
        cache_key = SITE_NAME_AS_KEY + '_scg_report_' + str(self.pk)
        cached_member_count = CacheManager.get_from_cache_by_key(key=cache_key)
        if cached_member_count is None:
            cached_member_count = self.members.count()
            CacheManager.set_cache_element_by_key(
                key=cache_key, value=cached_member_count, timeout=ONE_HOUR_TIMEOUT * 2)
        return cached_member_count

    @property
    def render_male_members(self):
        return self.members.filter(client_meta__gender__iexact='M').count()

    @property
    def render_female_members(self):
        return self.members.filter(client_meta__gender__iexact='F').count()

    @property
    def render_disabled_members(self):
        return self.members.filter(client_meta__is_disabled=True).count()

    @property
    def render_balance(self):
        if self.render_total_bank_balance or self.render_total_cash_in_hand:
            return self.render_total_bank_balance + self.render_total_cash_in_hand
        else:
            return 0

    @property
    def render_total_savings(self):
        return self.cumulative_report.deposited_savings if self.cumulative_report else 0

    @property
    def render_total_loan_disbursed(self):
        return self.cumulative_report.loan_disbursed if self.cumulative_report else 0

    @property
    def render_total_loan_disbursed_number(self):
        return self.cumulative_report.loan_disbursed_number if self.cumulative_report else 0

    @property
    def render_total_bank_balance(self):
        return self.cumulative_report.bank_banlance if self.cumulative_report else 0

    @property
    def render_total_cash_in_hand(self):
        return self.cumulative_report.cash_in_hand if self.cumulative_report else 0

    @classmethod
    def exclude_search_fields(cls):
        return ['render_total_member', 'render_balance']

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'name', 'render_city_corporation', 'render_CDC', 'render_total_member',
            'render_balance', 'date_created:Created On', 'last_updated')

    @property
    def general_information(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['city_corporation'] = self.render_city_corporation
        details['primary_group'] = self.primary_group
        details['date_of_formation'] = self.render_formation_date
        return details

    @property
    def basic_information(self):
        details = OrderedDict()
        details['total_members'] = self.render_total_member
        details['total_male_members'] = self.render_male_members
        details['total_female_members'] = self.render_female_members
        details['total_disabled_members'] = self.render_disabled_members
        return details

    @property
    def transaction_information(self):
        details = OrderedDict()
        details['total_value_of_savings'] = self.render_total_savings
        details['total_value_of_loan_disbursed'] = self.render_total_loan_disbursed
        details['total_loan_disbursed_number'] = self.render_total_loan_disbursed_number
        details['total_bank_balance'] = self.render_total_bank_balance
        details['total_cash_in_hand'] = self.render_total_cash_in_hand
        return details

    @property
    def other_information(self):
        details = OrderedDict()
        details['last_updated'] = self.render_timestamp(self.last_updated)
        details['last_updated_by'] = self.last_updated_by
        details['created_at'] = self.render_timestamp(self.date_created)
        details['created_by'] = self.created_by
        return details

    @property
    def details_config(self):
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        details['general_information'] = self.general_information
        details['basic_information'] = self.basic_information
        details['transaction_information'] = self.transaction_information
        details['other_information'] = self.other_information
        return details

    @classmethod
    def get_serializer(cls):
        IUSerializer = OrganizationDomainEntity.get_serializer()

        class SavingsAndCreditGroupSerializer(IUSerializer):
            pg_members = serializers.SerializerMethodField()
            pg_id = serializers.SerializerMethodField()
            members = serializers.SerializerMethodField()

            def __init__(self, *args, fields=None, context=None, **kwargs):
                super(SavingsAndCreditGroupSerializer, self).__init__(*args, fields=fields, context=context, **kwargs)

                cache_key = SITE_NAME_AS_KEY + '_scg_member_count_dict'
                cached_count_dictionary = CacheManager.get_from_cache_by_key(key=cache_key)
                if cached_count_dictionary is None:
                    pg_member_queryset = PrimaryGroupMember.objects.using(
                        BWDatabaseRouter.get_read_database_name()).values(
                        'assigned_to__savingsandcreditgroup__pk').annotate(count=Count('pk', distinct=True))
                    pg_id_queryset = PrimaryGroup.objects.using(BWDatabaseRouter.get_read_database_name()).values(
                        'assigned_code', 'savingsandcreditgroup__pk')
                    members_queryset = PrimaryGroupMember.objects.using(
                        BWDatabaseRouter.get_read_database_name()).values(
                        'savingsandcreditgroup__pk').annotate(count=Count('pk', distinct=True))

                    self.pg_member_dict = dict()
                    for pg_member in pg_member_queryset:
                        self.pg_member_dict[pg_member['assigned_to__savingsandcreditgroup__pk']] = pg_member['count']
                    self.pg_id_dict = dict()
                    for pg_id in pg_id_queryset:
                        self.pg_id_dict[pg_id['savingsandcreditgroup__pk']] = pg_id['assigned_code']
                    self.member_dict = dict()
                    for member in members_queryset:
                        self.member_dict[member['savingsandcreditgroup__pk']] = member['count']

                    cached_count_dictionary = {
                        'pg_member_dict': self.pg_member_dict,
                        'pg_id_dict': self.pg_id_dict,
                        'member_dict': self.member_dict
                    }
                    CacheManager.set_cache_element_by_key(
                        key=cache_key, value=json.dumps(cached_count_dictionary), timeout=ONE_HOUR_TIMEOUT * 2)
                else:
                    count_dict = json.loads(cached_count_dictionary)
                    self.pg_member_dict = count_dict['pg_member_dict']
                    self.pg_id_dict = count_dict['pg_id_dict']
                    self.member_dict = count_dict['member_dict']

            def get_pg_members(self, obj):
                try:
                    return self.pg_member_dict[str(obj.pk)]
                except:
                    return 0

            def get_pg_id(self, obj):
                try:
                    return self.pg_id_dict[str(obj.pk)]
                except:
                    return 0

            def get_members(self, obj):
                try:
                    return self.member_dict[str(obj.pk)]
                except:
                    return 0

            class Meta:
                model = cls
                fields = 'id', 'code', 'name', 'pg_id', 'primary_group', 'members', \
                         'pg_members', 'date_of_formation', 'last_updated'

        return SavingsAndCreditGroupSerializer

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Member(s)',
                access_key='members',
                route_name=self.__class__.get_route_name(action=ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                property=self.members,
                add_more_queryset=PrimaryGroupMember.objects.filter(assigned_to_id=self.primary_group_id,
                                                                    is_active=True).exclude(
                    pk__in=self.members.values_list('pk', flat=True)),
                related_model=PrimaryGroupMember,
                actions=[
                    TabViewAction(
                        title='Add',
                        action='add',
                        icon='icon-plus',
                        route_name=PrimaryGroupMember.get_route_name(action=ViewActionEnum.PartialBulkAdd,
                                                                     parent=self.__class__.__name__.lower()),
                        css_class='manage-action load-modal fis-plus-ico',
                        enable_wide_popup=True
                    ),
                    TabViewAction(
                        title='Remove',
                        action='partial-remove',
                        icon='icon-remove',
                        route_name=PrimaryGroupMember.get_route_name(action=ViewActionEnum.PartialBulkRemove,
                                                                     parent=self.__class__.__name__.lower()),
                        css_class='manage-action delete-item fis-remove-ico'
                    )
                ]
            ),

            TabView(
                title='Monthly Report(s)',
                access_key='reports',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='approvals.ApprovedSCGMonthlyReport',
                queryset_filter=Q(**{'scg_id': self.pk})
            ),

            TabView(
                title='Action Approval(s)',
                access_key='actions',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='approvals.SavingsAndCreditReportlog',
                queryset_filter=Q(**{'scg_report__scg_id': self.pk})
            ),
        ]

    @classmethod
    def get_button_title(cls, button):
        if button == ViewActionEnum.AdvancedExport:
            return 'Export'
        if button == ViewActionEnum.AdvancedImport:
            return 'Import'
        return 'N/A'

    @classmethod
    def get_manage_buttons(cls):
        manage_buttons = super(SavingsAndCreditGroup, cls).get_manage_buttons()
        return manage_buttons + [ViewActionEnum.AdvancedExport, ViewActionEnum.AdvancedImport]

    @property
    def render_primary_group_id(self):
        return self.primary_group.assigned_code if self.primary_group else ''

    @property
    def render_CDC(self):
        return self.primary_group.parent if self.primary_group and self.primary_group.parent else 'N/A'

    @classmethod
    def search_CDC(cls, queryset, value):
        return queryset.filter(
            Q(**{'primary_group__parent__code__icontains': value}) |
            Q(**{'primary_group__parent__name__icontains': value})
        )

    @property
    def render_cdc_id(self):
        return self.primary_group.parent.assigned_code if self.primary_group and self.primary_group.parent else ''

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, created = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ImporterColumnConfig(column=0, column_name='SCG Name', property_name='name', ignore=False),
            ImporterColumnConfig(column=1, column_name='Primary Group ID', property_name='render_primary_group_id',
                                 ignore=False),
            ImporterColumnConfig(column=2, column_name='CDC ID', property_name='render_cdc_id', ignore=False),
            ImporterColumnConfig(column=3, column_name='Division', property_name='render_division', ignore=False),
            ImporterColumnConfig(column=4, column_name='City Corporation', property_name='render_city_corporation',
                                 ignore=False),
            ImporterColumnConfig(column=5, column_name='Date of Formation', property_name='render_formation_date',
                                 ignore=False),
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        cls.process_scg_import(items=items, user=user, organization=organization, **kwargs)

    @classmethod
    def process_scg_import(cls, items, user=None, organization=None, **kwargs):
        organization = organization if organization else Organization.get_organization_from_cache()

        country, created = Geography.objects.get_or_create(
            name='Bangladesh', parent=None, type='Country', organization_id=organization.pk,
            level_id=GeographyLevel.objects.filter(name='Country').first().pk
        )

        # Division - Start
        division_dict = OrderedDict()
        divisions_create = list()
        creatable_division_names = list()

        for division in Geography.objects.filter(level__name='Division'):
            _division_name = unidecode(division.name).lower()
            division_dict[_division_name] = division

        time_now = Clock.timestamp()
        _error_count = 0
        for index, item in enumerate(items):
            try:
                division_name = str(item['3'])
                if division_name:
                    _division_name = unidecode(division_name).lower()
                    if _division_name not in division_dict.keys() and _division_name not in creatable_division_names:
                        division = Geography(
                            name=division_name, parent_id=country.id, type='Division', organization_id=organization.pk,
                            level_id=GeographyLevel.objects.filter(name='Division').first().pk,
                        )
                        division.created_by_id = user.id
                        division.date_created = time_now
                        time_now += 1
                        division.tsync_id = uuid.uuid4() if division.tsync_id is None else division.tsync_id
                        division.last_updated_by_id = user.id
                        division.last_updated = time_now
                        time_now += 1
                        divisions_create.append(division)
                        creatable_division_names.append(_division_name)
            except:
                _error_count += 1

        if len(divisions_create) > 0:
            Geography.objects.bulk_create(divisions_create)

        division_dict = OrderedDict()
        for division in Geography.objects.filter(level__name='Division'):
            _division_name = unidecode(division.name).lower()
            division_dict[_division_name] = division
        # Division - End

        # City - Start
        city_dict = OrderedDict()
        city_create = list()
        creatable_city_names = list()

        for city in Geography.objects.filter(level__name='Pourashava/City Corporation'):
            _city_name = unidecode(city.name).lower()
            _division_name = unidecode(city.parent.name).lower() if city.parent else ''
            _city_key = (_division_name, _city_name)
            city_dict[_city_key] = city

        time_now = Clock.timestamp()
        for index, item in enumerate(items):
            try:
                division_name = str(item['3'])
                if division_name:
                    division = None
                    _division_name = unidecode(division_name).lower()
                    if _division_name in division_dict.keys():
                        division = division_dict[_division_name]
                    city_name = str(item['4'])
                    if city_name:
                        _city_name = unidecode(city_name).lower()
                        _city_key = (_division_name, _city_name)
                        if _city_key not in city_dict.keys() and _city_key not in creatable_city_names:
                            city = Geography(
                                name=city_name, type='Pourashava/City Corporation', organization_id=organization.pk,
                                level_id=GeographyLevel.objects.filter(name='Pourashava/City Corporation').first().pk,
                            )
                            city.date_created = time_now
                            city.created_by_id = user.id
                            time_now += 1
                            city.parent_id = division.pk if division else None
                            city.tsync_id = uuid.uuid4() if city.tsync_id is None else city.tsync_id
                            city.last_updated = time_now
                            city.last_updated_by_id = user.id
                            time_now += 1
                            city_create.append(city)
                            creatable_city_names.append(_city_key)
            except:
                pass
        if len(city_create) > 0:
            Geography.objects.bulk_create(city_create)

        city_dict = OrderedDict()
        for city in Geography.objects.filter(level__name='Pourashava/City Corporation'):
            _city_name = unidecode(city.name).lower()
            _division_name = unidecode(city.parent.name).lower() if city.parent else ''
            _city_key = (_division_name, _city_name)
            city_dict[_city_key] = city
        # City - End

        # SCG - Start
        scg_dict = OrderedDict()
        scg_create = list()
        scg_update = list()
        creatable_scg_names = list()
        updatable_scg_names = list()
        reusable_pg_assigned_codes = list()

        scg_max_seqs, created = MaxSequence.objects.get_or_create(context=SavingsAndCreditGroup.__name__)
        scg_seqs_value = scg_max_seqs.value

        pg_dict = OrderedDict()
        for pg in PrimaryGroup.objects.all():
            _pg_assigned_code = unidecode(pg.assigned_code).lower() if pg.assigned_code else ''
            pg_dict[_pg_assigned_code] = pg

        for scg in SavingsAndCreditGroup.objects.all():
            _scg_name = unidecode(scg.name).lower()
            _pg_assigned_code = unidecode(scg.primary_group.assigned_code).lower() if scg.primary_group else ''
            _scg_key = (_scg_name, _pg_assigned_code)
            scg_dict[_scg_key] = scg

        time_now = Clock.timestamp()
        for index, item in enumerate(items):
            try:
                scg_name = str(item['0'])
                pg_assigned_code = str(item['1']) if item['1'] else ''
                cdc_assigned_code = str(item['2']) if item['2'] else ''
                division_name = str(item['3'])
                city_name = str(item['4'])
                date_of_formation = str(item['5']) if item['5'] else ''

                if division_name and city_name and scg_name and pg_assigned_code:
                    pg = None
                    _pg_assigned_code = unidecode(pg_assigned_code).lower()
                    if _pg_assigned_code in pg_dict.keys():
                        pg = pg_dict[_pg_assigned_code]

                    if pg:
                        _scg_name = unidecode(scg_name).lower()
                        _scg_key = (_scg_name, _pg_assigned_code)
                        if _scg_key in scg_dict.keys():
                            scg = scg_dict[_scg_key]
                            if date_of_formation:
                                scg.date_of_formation = datetime.strptime(date_of_formation, '%d/%m/%Y')
                            if scg.code is None or scg.code == '':
                                scg.code = scg.code_prefix + scg.code_separator + str(scg_seqs_value).zfill(5)
                                scg_seqs_value += 1
                            scg.tsync_id = uuid.uuid4() if scg.tsync_id is None else scg.tsync_id
                            scg.last_updated = time_now
                            time_now += 1
                            if _scg_key not in updatable_scg_names:
                                scg_update.append(scg)
                                updatable_scg_names.append(_scg_key)
                        elif _scg_key not in creatable_scg_names:
                            scg = SavingsAndCreditGroup(
                                name=scg_name, primary_group_id=pg.pk,
                                organization_id=organization.pk
                            )
                            scg.date_created = time_now
                            scg.created_by_id = user.pk
                            time_now += 1
                            scg.type = SavingsAndCreditGroup.__name__
                            scg.tsync_id = uuid.uuid4() if scg.tsync_id is None else scg.tsync_id
                            scg.last_updated = time_now
                            scg.last_updated_by_id = user.pk
                            time_now += 1
                            if date_of_formation:
                                scg.date_of_formation = datetime.strptime(date_of_formation, '%d/%m/%Y')
                            scg.code = scg.code_prefix + scg.code_separator + str(scg_seqs_value).zfill(5)
                            scg_seqs_value += 1
                            scg_create.append(scg)
                            creatable_scg_names.append(_scg_key)
                            reusable_pg_assigned_codes.append(_pg_assigned_code)
            except:
                pass
        scg_max_seqs.value = scg_seqs_value
        scg_max_seqs.save()
        if len(scg_create) > 0:
            SavingsAndCreditGroup.objects.bulk_create(scg_create)
        if len(scg_update) > 0:
            SavingsAndCreditGroup.objects.bulk_update(scg_update)

        scg_dict = OrderedDict()
        for scg in SavingsAndCreditGroup.objects.all():
            _scg_name = unidecode(scg.name).lower()
            _pg_assigned_code = unidecode(scg.primary_group.assigned_code).lower() if scg.primary_group else ''
            _scg_key = (_scg_name, _pg_assigned_code)
            scg_dict[_scg_key] = scg
        # SCG - End

        # SCG Address - Start
        scg_address_time_map = OrderedDict()
        address_create = list()
        creatable_address_names = list()

        time_now = Clock.timestamp()
        for index, item in enumerate(items):
            try:
                scg_name = str(item['0'])
                pg_assigned_code = str(item['1']) if item['1'] else ''
                division_name = str(item['3'])
                city_name = str(item['4'])
                if city_name and scg_name and pg_assigned_code:
                    scg = None
                    _scg_name = unidecode(scg_name).lower()
                    _pg_assigned_code = unidecode(pg_assigned_code).lower()
                    _scg_key = (_scg_name, _pg_assigned_code)
                    if _scg_key in scg_dict.keys():
                        scg = scg_dict[_scg_key]

                    city = None
                    _division_name = unidecode(division_name).lower()
                    _city_name = unidecode(city_name).lower()
                    _city_key = (_division_name, _city_name)
                    if _city_key in city_dict.keys():
                        city = city_dict[_city_key]

                    if scg and city and scg.address is None:
                        if _scg_key not in creatable_address_names:
                            address = ContactAddress()
                            address.geography_id = city.pk
                            address.date_created = time_now
                            address.created_by_id = user.id
                            time_now += 1
                            address.tsync_id = uuid.uuid4() if address.tsync_id is None else address.tsync_id
                            address.last_updated = time_now
                            address.last_updated_by_id = user.id
                            time_now += 1
                            address_create.append(address)
                            creatable_address_names.append(_scg_key)
                            scg_address_time_map[_scg_key] = str(address.tsync_id)
            except:
                pass
        if len(address_create) > 0:
            ContactAddress.objects.bulk_create(address_create)

        address_dict = OrderedDict()
        for address in ContactAddress.objects.filter(tsync_id__in=scg_address_time_map.values()):
            _address_key = address.tsync_id
            address_dict[_address_key] = address
        # SCG Address - End

        # SCG Address assignment - Start
        scg_assignment_update = list()
        updatable_scg_assignment_names = list()

        time_now = Clock.timestamp()
        for index, item in enumerate(items):
            try:
                scg_name = str(item['0'])
                pg_assigned_code = str(item['1']) if item['1'] else ''
                division_name = str(item['3'])
                city_name = str(item['4'])

                city = None
                _division_name = unidecode(division_name).lower()
                _city_name = unidecode(city_name).lower()
                _city_key = (_division_name, _city_name)
                if _city_key in city_dict.keys():
                    city = city_dict[_city_key]

                if scg_name and pg_assigned_code and city_name:
                    _scg_name = unidecode(scg_name).lower()
                    _pg_assigned_code = unidecode(pg_assigned_code).lower()
                    _scg_key = (_scg_name, _pg_assigned_code)

                    if _scg_key in scg_dict.keys():
                        scg = scg_dict[_scg_key]
                        if scg.address:
                            scg.address.geography_id = city.pk
                        else:
                            scg.address = address_dict[scg_address_time_map[_scg_key]]
                        scg.last_updated = time_now
                        time_now += 1
                        if _scg_key not in updatable_scg_assignment_names:
                            scg_assignment_update.append(scg)
                            updatable_scg_assignment_names.append(_scg_key)
            except:
                pass
        if len(scg_assignment_update) > 0:
            SavingsAndCreditGroup.objects.bulk_update(scg_assignment_update)
        # SCG Address assignment - End

        if len(creatable_scg_names) > 0:
            pg_member_queryset = PrimaryGroupMember.objects.filter(
                assigned_to__assigned_code__in=reusable_pg_assigned_codes
            ).values('id', 'assigned_to')

            pg_member_dict = OrderedDict()
            for pg_member in pg_member_queryset:
                pg_member_id = pg_member['id']
                pg_id = pg_member['assigned_to']
                if pg_id not in pg_member_dict.keys():
                    pg_member_dict[pg_id] = list()
                pg_member_dict[pg_id].append(pg_member_id)

            for _scg_key in creatable_scg_names:
                if _scg_key in scg_dict.keys():
                    scg = scg_dict[_scg_key]
                    if scg.primary_group_id in pg_member_dict.keys():
                        pg_members = pg_member_dict[scg.primary_group_id]
                        scg.members.add(*pg_members)

        print('error %d' % _error_count)
        print('creatable division %d' % len(divisions_create))
        print('creatable city %d' % len(city_create))
        print('creatable SCG %d' % len(scg_create))
        print('updateable SCG %d' % len(scg_update))
        print('creatable address %d' % len(address_create))
        print('updateable SCG address assignment %d' % len(scg_assignment_update))

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='SCG Name', property_name='name', ignore=False),
            ExporterColumnConfig(column=1, column_name='Primary Group ID', property_name='render_primary_group_id',
                                 ignore=False),
            ExporterColumnConfig(column=2, column_name='CDC ID', property_name='render_cdc_id', ignore=False),
            ExporterColumnConfig(column=3, column_name='Division', property_name='render_division', ignore=False),
            ExporterColumnConfig(column=4, column_name='City Corporation', property_name='render_city_corporation',
                                 ignore=False),
            ExporterColumnConfig(column=5, column_name='Total Member', property_name='render_total_member',
                                 ignore=False),
            ExporterColumnConfig(column=6, column_name='Date of Formation', property_name='render_formation_date',
                                 ignore=False),
            ExporterColumnConfig(column=7, column_name='Created on', property_name='render_date_created',
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
            queryset = queryset.filter(address__geography__id__in=city_ids)

        for scg in queryset:
            for column in columns:
                column_value = ''
                if hasattr(scg, column.property_name):
                    column_value = str(getattr(scg, column.property_name))

                workbook.cell(row=row_number, column=column.column + 1).value = column_value
            row_number += 1

        return workbook, row_number

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
    def create_scg_for_newly_created_pg(cls):
        _city_wise_contact_id = dict()
        _creatable_scg_list = list()
        _reusable_pg_assigned_codes = list()
        _creatable_pg_ids = list()
        time_now = Clock.timestamp()
        organization = Organization.get_organization_from_cache()
        bw_user = ConsoleUser.objects.filter(user__username='BackgroundUser').first()
        scg_max_seqs, created = MaxSequence.objects.get_or_create(context=SavingsAndCreditGroup.__name__)
        scg_seqs_value = scg_max_seqs.value

        city_address_queryset = ContactAddress.objects.filter(geography__type='Pourashava/City Corporation').distinct(
            'geography_id').values('pk', 'geography__name')

        # prepare a dictionary where key will be city name and value will be ID of contact address instance
        for city_address_contact_dict in city_address_queryset:
            _contact_id = city_address_contact_dict['pk']
            _city_name = city_address_contact_dict['geography__name']
            _city_wise_contact_id[_city_name] = _contact_id

        _pg_queryset = PrimaryGroup.objects.filter(savingsandcreditgroup__isnull=True)

        # Create scg objects for newly created pg
        for _pg in _pg_queryset:
            scg = SavingsAndCreditGroup(
                name=_pg.name, primary_group_id=_pg.pk,
                organization_id=organization.pk,
                address=_pg.address
            )
            scg.date_created = time_now
            scg.created_by_id = bw_user.pk
            scg.type = SavingsAndCreditGroup.__name__
            scg.tsync_id = uuid.uuid4() if scg.tsync_id is None else scg.tsync_id
            scg.last_updated = time_now
            scg.last_updated_by_id = bw_user.pk
            time_now += 1
            if _pg.date_of_formation:
                scg.date_of_formation = _pg.date_of_formation
            scg.code = scg.code_prefix + scg.code_separator + str(scg_seqs_value).zfill(5)
            scg_seqs_value += 1
            _creatable_scg_list.append(scg)
            _reusable_pg_assigned_codes.append(_pg.assigned_code)
            _creatable_pg_ids.append(_pg.pk)

        if len(_creatable_scg_list) > 0:
            cls.objects.bulk_create(_creatable_scg_list)

            # Prepare a dict where key is primary group id and value is list of primary group member
            pg_member_dict = OrderedDict()
            pg_member_queryset = PrimaryGroupMember.objects.filter(
                assigned_to__assigned_code__in=_reusable_pg_assigned_codes
            ).values('id', 'assigned_to')

            for pg_member in pg_member_queryset:
                pg_member_id = pg_member['id']
                pg_id = pg_member['assigned_to']
                if pg_id not in pg_member_dict.keys():
                    pg_member_dict[pg_id] = list()
                pg_member_dict[pg_id].append(pg_member_id)

            # Assign PGM to scg
            for scg in SavingsAndCreditGroup.objects.filter(primary_group_id__in=_creatable_pg_ids):
                if scg.primary_group_id in pg_member_dict.keys():
                    pg_members = pg_member_dict[scg.primary_group_id]
                    scg.members.add(*pg_members)
