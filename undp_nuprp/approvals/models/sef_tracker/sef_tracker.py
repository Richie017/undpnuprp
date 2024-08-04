import uuid
from datetime import datetime, date

from django import forms
from django.db import models
from django.forms import Form
from django.utils.safestring import mark_safe

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import ImporterConfig, ImporterColumnConfig, Geography, ExporterConfig, ExporterColumnConfig, ErrorLog
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.models import CDCCluster, CDC


@decorate(is_object_context, route(route='sef-tracker', group='Local Economy Livelihood and Financial Inclusion',
                                   module=ModuleEnum.Analysis, display_name='SEF Tracker',
                                   group_order=3, item_order=25), enable_import, enable_export)
class SEFTracker(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True, on_delete=models.SET_NULL)
    ward = models.CharField(max_length=20, null=True, blank=True)
    contract_with_cdc_or_cluster = models.CharField(max_length=20, null=True, blank=True)
    cluster = models.ForeignKey(CDCCluster, null=True, blank=True, related_name='sef_trackers', on_delete=models.SET_NULL)
    cdc = models.ForeignKey(CDC, null=True, blank=True, on_delete=models.SET_NULL)
    contract_number = models.CharField(max_length=20, null=True, blank=True)
    contract_year = models.IntegerField(null=True, blank=True)
    category_name = models.CharField(max_length=50, blank=True, null=True)

    male_beneficiaries = models.IntegerField(blank=True, default=0)
    female_beneficiaries = models.IntegerField(blank=True, default=0)
    third_gender_beneficiaries = models.IntegerField(blank=True, default=0)
    total_beneficiaries = models.IntegerField(blank=True, default=0)

    contract_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    training_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    management_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    installment_number = models.CharField(max_length=256, blank=True, null=True)
    total_contract_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    transfer_from_cluster_cdc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_with_town = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    expenditure_made_by_cluster_cdc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    balance_with_cluster_cdc = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    actual_contract_start_date = models.DateField(null=True, blank=True)
    actual_contract_end_date = models.DateField(null=True, blank=True)

    achieved_male_beneficiaries = models.IntegerField(blank=True, default=0)
    achieved_female_beneficiaries = models.IntegerField(blank=True, default=0)
    achieved_third_gender_beneficiaries = models.IntegerField(blank=True, default=0)
    achieved_total_beneficiaries = models.IntegerField(blank=True, default=0)

    class Meta:
        app_label = 'approvals'

    def save(self, *args, organization=None, **kwargs):
        self.total_beneficiaries = self.male_beneficiaries + self.female_beneficiaries + self.third_gender_beneficiaries

        if self.contract_value is None and self.management_fee is None and self.training_cost is None:
            self.total_contract_value = None
        else:
            self.total_contract_value = (self.contract_value if self.contract_value is not None else 0) +\
                                        (self.management_fee if self.management_fee else 0) +\
                                        (self.training_cost if self.training_cost else 0)

        self.achieved_total_beneficiaries = self.achieved_male_beneficiaries + self.achieved_female_beneficiaries +\
                                            self.achieved_third_gender_beneficiaries

        super(SEFTracker, self).save(organization=organization, **kwargs)

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_cluster(self):
        return self.cluster if self.cluster is not None else "N/A"

    @property
    def export_cluster(self):
        return self.cluster.name if self.cluster is not None else "N/A"

    @property
    def render_city(self):
        return self.city if self.city is not None else "N/A"

    @property
    def export_city(self):
        return self.city.name if self.city is not None else "N/A"

    @property
    def render_ward(self):
        try:
            return self.ward if self.ward is not None and self.ward.strip() != "" else "N/A"
        except Exception as exp:
            return "N/A"

    @property
    def render_contract_with(self):
        try:
            return self.contract_with_cdc_or_cluster if self.contract_with_cdc_or_cluster is not None and\
                                                        self.contract_with_cdc_or_cluster.strip() != "" else "N/A"
        except Exception as exp:
            return "N/A"

    @property
    def render_cdc(self):
        return self.cdc if self.cdc is not None else "N/A"

    @property
    def export_cdc(self):
        return self.cdc.name if self.cdc is not None else "N/A"

    @property
    def render_contract_number(self):
        try:
            return self.contract_number if self.contract_number is not None and\
                                           self.contract_number.strip() != "" else "N/A"
        except Exception as exp:
            return "N/A"

    @property
    def render_contract_year(self):
        try:
            return self.contract_year if self.contract_year is not None else "N/A"
        except Exception as exp:
            return "N/A"

    @property
    def render_category_name(self):
        try:
            return self.category_name if self.category_name is not None and self.category_name.strip() != "" else "N/A"
        except Exception as exp:
            return "N/A"

    @property
    def render_male_beneficiaries(self):
        return self.male_beneficiaries if self.male_beneficiaries is not None else "N/A"

    @property
    def render_female_beneficiaries(self):
        return self.female_beneficiaries if self.female_beneficiaries is not None else "N/A"

    @property
    def render_third_gender_beneficiaries(self):
        return self.third_gender_beneficiaries if self.third_gender_beneficiaries is not None else "N/A"

    @property
    def render_total_beneficiaries(self):
        return self.total_beneficiaries if self.total_beneficiaries is not None else "N/A"

    @property
    def render_contract_value(self):
        return self.contract_value if self.contract_value is not None else "N/A"

    @property
    def render_training_cost(self):
        return self.training_cost if self.training_cost is not None else "N/A"

    @property
    def render_management_fee(self):
        return self.management_fee if self.management_fee is not None else "N/A"

    @property
    def render_installment_number(self):
        try:
            return self.installment_number if self.installment_number is not None and self.installment_number.strip() != "" else "N/A"
        except Exception as exp:
            return "N/A"

    @property
    def render_total_contract_value(self):
        return self.total_contract_value if self.total_contract_value is not None else "N/A"

    @property
    def render_transfer_from_cluster_cdc(self):
        return self.transfer_from_cluster_cdc if self.transfer_from_cluster_cdc is not None else "N/A"

    @property
    def render_balance_with_town(self):
        return self.balance_with_town if self.balance_with_town is not None else "N/A"

    @property
    def render_expenditure_made_by_cluster_cdc(self):
        return self.expenditure_made_by_cluster_cdc if self.expenditure_made_by_cluster_cdc is not None else "N/A"

    @property
    def render_balance_with_cluster_cdc(self):
        return self.balance_with_cluster_cdc if self.balance_with_cluster_cdc is not None else "N/A"

    @property
    def render_actual_contract_start_date(self):
        return self.actual_contract_start_date if self.actual_contract_start_date is not None else "N/A"

    @property
    def render_actual_contract_end_date(self):
        return self.actual_contract_end_date if self.actual_contract_end_date is not None else "N/A"

    @property
    def render_achieved_male_beneficiaries(self):
        return self.achieved_male_beneficiaries if self.achieved_male_beneficiaries is not None else "N/A"

    @property
    def render_achieved_female_beneficiaries(self):
        return self.achieved_female_beneficiaries if self.achieved_female_beneficiaries is not None else "N/A"

    @property
    def render_achieved_third_gender_beneficiaries(self):
        return self.achieved_third_gender_beneficiaries \
            if self.achieved_third_gender_beneficiaries is not None else "N/A"

    @property
    def render_achieved_total_beneficiaries(self):
        return self.achieved_total_beneficiaries if self.achieved_total_beneficiaries is not None else "N/A"

    @classmethod
    def table_columns(cls):
        return 'code', 'render_city', 'render_ward', 'render_contract_with', 'render_cluster', 'render_cdc',\
               'render_contract_number', 'render_contract_year', 'render_category_name', 'render_installment_number',\
               'created_by', 'date_created', 'last_updated'

    @classmethod
    def details_view_fields(cls):
        return ['detail_title', 'code', 'created_by', 'date_created', 'last_updated_by', 'last_updated:Last updated on',
                'render_city>Primary Info', 'render_ward>Primary Info',
                'render_contract_with>Primary Info', 'render_cluster>Primary Info',
                'render_cdc>Primary Info', 'render_contract_number>Primary Info', 'render_contract_year>Primary Info',
                'render_category_name>Primary Info', 'render_male_beneficiaries:Male>No of Beneficiaries',
                'render_female_beneficiaries:Female>No of Beneficiaries',
                'render_third_gender_beneficiaries:Third gender>No of Beneficiaries',
                'render_total_beneficiaries:Total>No of Beneficiaries',
                'render_contract_value>Contract Value', 'render_training_cost>Contract Value',
                'render_management_fee>Contract Value','render_installment_number>Contract Value', 'render_total_contract_value>Contract Value',
                'render_transfer_from_cluster_cdc:Transfer to Cluster/CDC>Fund Status',
                'render_balance_with_town>Fund Status',
                'render_expenditure_made_by_cluster_cdc:Expenditure made by Cluster/CDC>Fund Status',
                'render_balance_with_cluster_cdc:Balance with Cluster/CDC>Fund Status',
                'render_actual_contract_start_date>Actual Contract Date',
                'render_actual_contract_end_date>Actual Contract Date',
                'render_achieved_male_beneficiaries:Male>Achieved Beneficiaries',
                'render_achieved_female_beneficiaries:Female>Achieved Beneficiaries',
                'render_achieved_third_gender_beneficiaries:Third gender>Achieved Beneficiaries',
                'render_achieved_total_beneficiaries:Total>Achieved Beneficiaries']

    @staticmethod
    def to_int(value, default):
        int_ = value
        try:
            int_ = int(int_)
        except:
            return default
        return int_

    @staticmethod
    def to_decimal(value, default):
        dec_ = value
        try:
            dec_ = float(dec_)
        except:
            return default
        return dec_

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedImport,
                ViewActionEnum.AdvancedExport]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedImport:
            return "Import"
        if button == ViewActionEnum.AdvancedExport:
            return "Export"

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)

        columns = [
            ImporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ImporterColumnConfig(column=1, column_name='Ward No', property_name='ward', ignore=False),
            ImporterColumnConfig(column=2, column_name='Contract with CDC or Cluster',
                                 property_name='contract_with_cdc_or_cluster', ignore=False),
            ImporterColumnConfig(column=3, column_name='Cluster', property_name='cluster', ignore=False),
            ImporterColumnConfig(column=4, column_name='CDC', property_name='cdc', ignore=False),
            ImporterColumnConfig(column=5, column_name='Contract Number', property_name='contract_number',
                                 ignore=False),
            ImporterColumnConfig(column=6, column_name='Contract Year', property_name='contract_year', ignore=False),
            ImporterColumnConfig(column=7, column_name='Category Name', property_name='category_name', ignore=False),
            ImporterColumnConfig(column=8, column_name='Male', property_name='male_beneficiaries', ignore=False),
            ImporterColumnConfig(column=9, column_name='Female', property_name='female_beneficiaries', ignore=False),
            ImporterColumnConfig(column=10, column_name='Third Gender', property_name='third_gender_beneficiaries',
                                 ignore=False),
            ImporterColumnConfig(column=11, column_name='Total', property_name='total_beneficiaries', ignore=False),
            ImporterColumnConfig(column=12, column_name='Contract Value',
                                 property_name='contract_value', ignore=False),
            ImporterColumnConfig(column=13, column_name='Management Fee', property_name='management_fee', ignore=False),
            ImporterColumnConfig(column=14, column_name='Training Cost', property_name='training_cost', ignore=False),
            ImporterColumnConfig(column=15, column_name='Installment Number',
                                 property_name='installment_number', ignore=False),
            ImporterColumnConfig(column=16, column_name='Total Contract Value',
                                 property_name='total_contract_value', ignore=False),
            ImporterColumnConfig(column=17, column_name='Transfer from Cluster/CDC',
                                 property_name='transfer_from_cluster_cdc', ignore=False),
            ImporterColumnConfig(column=18, column_name='Balance with Town', property_name='balance_with_town',
                                 ignore=False),
            ImporterColumnConfig(column=19, column_name='Expenditure Made by Cluster/CDC',
                                 property_name='expenditure_made_by_cluster_cdc', ignore=False),
            ImporterColumnConfig(column=20, column_name='Balance with Cluster/CDC',
                                 property_name='balance_with_cluster_cdc', ignore=False),
            ImporterColumnConfig(column=21, column_name='Actual Contract Start Date',
                                 property_name='actual_contract_start_date', ignore=False),
            ImporterColumnConfig(column=22, column_name='Actual Contract End Date',
                                 property_name='actual_contract_end_date', ignore=False),
            ImporterColumnConfig(column=23, column_name='Achieved Male Beneficiaries',
                                 property_name='achieved_male_beneficiaries', ignore=False),
            ImporterColumnConfig(column=24, column_name='Achieved Female Beneficiaries',
                                 property_name='achieved_female_beneficiaries', ignore=False),
            ImporterColumnConfig(column=25, column_name='Achieved Third Gender Beneficiaries',
                                 property_name='achieved_third_gender_beneficiaries', ignore=False),
            ImporterColumnConfig(column=26, column_name='Achieved Total Beneficiaries',
                                 property_name='achieved_total_beneficiaries', ignore=False),
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
        timestamp = Clock.timestamp()
        create_list = []

        for index, item in enumerate(items):
            city = str(item['0']).strip()
            ward = str(item['1']).strip()
            if len(ward) == 1:
                ward = "0" + str(ward)
            contract_with_cdc_or_cluster = str(item['2']).strip()
            cluster = str(item['3']).strip()
            cdc = str(item['4']).strip()
            contract_number = str(item['5']).strip()
            contract_year = cls.to_int(str(item['6']).strip(), None)
            category_name = str(item['7']).strip()
            male_beneficiaries = cls.to_int(str(item['8']).strip(), 0)
            female_beneficiaries = cls.to_int(str(item['9']).strip(), 0)
            third_gender_beneficiaries = cls.to_int(str(item['10']).strip(), 0)
            total_beneficiaries = cls.to_int(str(item['11']).strip(), 0)
            contract_value = cls.to_decimal(str(item['12']).strip(), None)
            management_fee = cls.to_decimal(str(item['13']).strip(), None)
            training_cost = cls.to_decimal(str(item['14']).strip(), None)

            if category_name.lower() == 'nutrition':
                installment_number = str(item['15']).strip()
            else:
                installment_number = ""

            total_contract_value = cls.to_decimal(str(item['16']).strip(), None)
            transfer_from_cluster_cdc = cls.to_decimal(str(item['17']).strip(), None)
            balance_with_town = cls.to_decimal(str(item['18']).strip(), None)
            expenditure_made_by_cluster_cdc = cls.to_decimal(str(item['19']).strip(), None)
            balance_with_cluster_cdc = cls.to_decimal(str(item['20']).strip(), None)
            actual_contract_start_date = item['21'].strftime("%d/%m/%Y") if type(item['21']) == datetime else item['21']
            actual_contract_end_date = item["22"].strftime("%d/%m/%Y") \
                if isinstance(item["22"], datetime) else item["22"]
            achieved_male_beneficiaries = cls.to_int(str(item['23']).strip(), 0)
            achieved_female_beneficiaries = cls.to_int(str(item['24']).strip(), 0)
            achieved_third_gender_beneficiaries = cls.to_int(str(item['25']).strip(), 0)
            achieved_total_beneficiaries = cls.to_int(str(item['26']).strip(), 0)

            city_ = Geography.objects.filter(level__name='Pourashava/City Corporation', name__iexact=city).first()

            if city_:
                _cdc = CDC.objects.filter(assigned_code=cdc, address__geography__parent_id=city_.id).first()
                if not _cdc:
                    _cdc = CDC.objects.filter(name__iexact=cdc, address__geography__parent_id=city_.id).first()

                _cluster = CDCCluster.objects.filter(assigned_code=cluster, address__geography_id=city_.id).first()
                if not _cluster:
                    _cluster = CDCCluster.objects.filter(name__iexact=cluster, address__geography_id=city_.id).first()
                if _cdc or _cluster:
                    new_ = SEFTracker(
                        city=city_,
                        organization=organization,
                        ward=ward,
                        contract_with_cdc_or_cluster=contract_with_cdc_or_cluster,
                        cluster=_cluster,
                        cdc=_cdc,
                        contract_number=contract_number,
                        contract_year=contract_year,
                        category_name=category_name,
                        male_beneficiaries=male_beneficiaries,
                        female_beneficiaries=female_beneficiaries,
                        third_gender_beneficiaries=third_gender_beneficiaries,
                        total_beneficiaries=total_beneficiaries,
                        contract_value=contract_value,
                        management_fee=management_fee,
                        training_cost=training_cost,
                        installment_number=installment_number,
                        total_contract_value=total_contract_value,
                        transfer_from_cluster_cdc=transfer_from_cluster_cdc,
                        balance_with_town=balance_with_town,
                        expenditure_made_by_cluster_cdc=expenditure_made_by_cluster_cdc,
                        balance_with_cluster_cdc=balance_with_cluster_cdc,
                        actual_contract_start_date=actual_contract_start_date,
                        actual_contract_end_date=actual_contract_end_date,
                        achieved_male_beneficiaries=achieved_male_beneficiaries,
                        achieved_female_beneficiaries=achieved_female_beneficiaries,
                        achieved_third_gender_beneficiaries=achieved_third_gender_beneficiaries,
                        achieved_total_beneficiaries=achieved_total_beneficiaries,
                        date_created=timestamp,
                        created_by=user,
                        tsync_id=uuid.uuid4(),
                        last_updated=timestamp,
                        last_updated_by=user,
                        type=cls.__name__
                    )

                    timestamp += 1
                    create_list.append(new_)

        if create_list:
            SEFTracker.objects.bulk_create(create_list, batch_size=200)

        empties = SEFTracker.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            SEFTracker.objects.bulk_update(update_list, batch_size=200)

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='City', property_name='export_city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Ward No', property_name='render_ward', ignore=False),
            ExporterColumnConfig(column=2, column_name='Contract with CDC or Cluster',
                                 property_name='render_contract_with', ignore=False),
            ExporterColumnConfig(column=3, column_name='Cluster', property_name='export_cluster', ignore=False),
            ExporterColumnConfig(column=4, column_name='CDC', property_name='export_cdc', ignore=False),
            ExporterColumnConfig(column=5, column_name='Contract Number', property_name='render_contract_number',
                                 ignore=False),
            ExporterColumnConfig(column=6, column_name='Contract Year',
                                 property_name='render_contract_year', ignore=False),
            ExporterColumnConfig(column=7, column_name='Category Name',
                                 property_name='render_category_name', ignore=False),
            ExporterColumnConfig(column=8, column_name='Male', property_name='render_male_beneficiaries', ignore=False),
            ExporterColumnConfig(column=9, column_name='Female',
                                 property_name='render_female_beneficiaries', ignore=False),
            ExporterColumnConfig(column=10, column_name='Third Gender',
                                 property_name='render_third_gender_beneficiaries', ignore=False),
            ExporterColumnConfig(column=11, column_name='Total',
                                 property_name='render_total_beneficiaries', ignore=False),
            ExporterColumnConfig(column=12, column_name='Contract Value',
                                 property_name='render_contract_value', ignore=False),
            ExporterColumnConfig(column=13, column_name='Management Fee',
                                 property_name='render_management_fee', ignore=False),
            ExporterColumnConfig(column=14, column_name='Training Cost',
                                 property_name='render_training_cost', ignore=False),
            ExporterColumnConfig(column=15, column_name='Installment Number',
                                 property_name='installment_number', ignore=False),
            ExporterColumnConfig(column=16, column_name='Total Contract Value',
                                 property_name='render_total_contract_value', ignore=False),
            ExporterColumnConfig(column=17, column_name='Transfer from Cluster/CDC',
                                 property_name='render_transfer_from_cluster_cdc', ignore=False),
            ExporterColumnConfig(column=18, column_name='Balance with Town', property_name='render_balance_with_town',
                                 ignore=False),
            ExporterColumnConfig(column=19, column_name='Expenditure Made by Cluster/CDC',
                                 property_name='render_expenditure_made_by_cluster_cdc', ignore=False),
            ExporterColumnConfig(column=20, column_name='Balance with Cluster/CDC',
                                 property_name='render_balance_with_cluster_cdc', ignore=False),
            ExporterColumnConfig(column=21, column_name='Actual Contract Start Date',
                                 property_name='render_actual_contract_start_date', ignore=False),
            ExporterColumnConfig(column=22, column_name='Actual Contract End Date',
                                 property_name='render_actual_contract_end_date', ignore=False),
            ExporterColumnConfig(column=23, column_name='Achieved Male Beneficiaries',
                                 property_name='render_achieved_male_beneficiaries', ignore=False),
            ExporterColumnConfig(column=24, column_name='Achieved Female Beneficiaries',
                                 property_name='render_achieved_female_beneficiaries', ignore=False),
            ExporterColumnConfig(column=25, column_name='Achieved Third Gender Beneficiaries',
                                 property_name='render_achieved_third_gender_beneficiaries', ignore=False),
            ExporterColumnConfig(column=26, column_name='Achieved Total Beneficiaries',
                                 property_name='render_achieved_total_beneficiaries', ignore=False),
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
            queryset = queryset.filter(city__id__in=city_ids)

        for cdc in queryset:
            for column in columns:
                column_value = ''
                if hasattr(cdc, column.property_name):
                    if column.property_name in ['cdc', 'cluster']:
                        column_value = getattr(cdc, column.property_name)
                        column_value = column_value.name if column_value else ''
                    else:
                        column_value = str(getattr(cdc, column.property_name))

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
                        queryset=Geography.objects.using(
                            BWDatabaseRouter.get_export_database_name()
                        ).filter(level__name='Pourashava/City Corporation'),
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
