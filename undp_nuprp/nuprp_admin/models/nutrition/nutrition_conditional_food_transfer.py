import calendar
import uuid
from datetime import datetime, date

from crequest.middleware import CrequestMiddleware
from django import forms
from django.db import models
from django.forms import Form
from django.utils.safestring import mark_safe

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography, ImporterConfig, ImporterColumnConfig, ExporterConfig, ExporterColumnConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter


@decorate(is_object_context, route(route='nutrition-conditional-food-transfer',
                                   group='Local Economy Livelihood and Financial Inclusion',
                                   module=ModuleEnum.Analysis,
                                   display_name='Nutrition Conditional Food Transfer', group_order=3, item_order=22),
          enable_import, enable_export)
class NutritionConditionalFoodTransfer(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True)
    month = models.IntegerField(default=1)
    year = models.IntegerField(default=2020)
    no_of_pregnant_women_by_age_lt_20 = models.IntegerField(null=True)
    no_of_pregnant_women_by_age_20_25 = models.IntegerField(null=True)
    no_of_pregnant_women_by_age_26_30 = models.IntegerField(null=True)
    no_of_pregnant_women_by_age_31_35 = models.IntegerField(null=True)
    no_of_pregnant_women_by_age_36_40 = models.IntegerField(null=True)
    no_of_pregnant_women_by_age_41_45 = models.IntegerField(null=True)
    no_of_pregnant_women_by_age_46_50 = models.IntegerField(null=True)
    no_of_pregnant_women_by_age_gt_50 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_lt_20 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_20_25 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_26_30 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_31_35 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_36_40 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_41_45 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_46_50 = models.IntegerField(null=True)
    no_of_lactating_mothers_by_age_gt_50 = models.IntegerField(null=True)
    no_of_child_0_6_months_by_male = models.IntegerField(null=True)
    no_of_child_0_6_months_by_female = models.IntegerField(null=True)
    no_of_child_0_6_months_by_transgender = models.IntegerField(null=True)
    no_of_child_7_24_months_by_male = models.IntegerField(null=True)
    no_of_child_7_24_months_by_female = models.IntegerField(null=True)
    no_of_child_7_24_months_by_transgender = models.IntegerField(null=True)

    class Meta:
        app_label = 'nuprp_admin'

    @property
    def detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_month(self):
        return calendar.month_name[self.month]

    @classmethod
    def table_columns(cls):
        return ['code', 'city', 'render_month', 'year',
                # 'no_of_pregnant_women_by_age_lt_20:No of pregnant women by age < 20',
                # 'no_of_pregnant_women_by_age_20_25:No of pregnant women by age 20-25',
                # 'no_of_pregnant_women_by_age_26_30:No of pregnant women by age 26-30',
                # 'no_of_pregnant_women_by_age_31_35:No of pregnant women by age 31-35',
                # 'no_of_pregnant_women_by_age_36_40:No of pregnant women by age 36-40',
                # 'no_of_pregnant_women_by_age_41_45:No of pregnant women by age 41-45',
                # 'no_of_pregnant_women_by_age_46_50:No of pregnant women by age 46-50',
                # 'no_of_pregnant_women_by_age_gt_50:No of pregnant women by age > 50',
                # 'no_of_lactating_mothers_by_age_lt_20:No of lactating mothers by age < 20',
                # 'no_of_lactating_mothers_by_age_20_25:No of lactating mothers by age 20-25',
                # 'no_of_lactating_mothers_by_age_26_30:No of lactating mothers by age 26-30',
                # 'no_of_lactating_mothers_by_age_31_35:No of lactating mothers by age 31-35',
                # 'no_of_lactating_mothers_by_age_36_40:No of lactating mothers by age 36-40',
                # 'no_of_lactating_mothers_by_age_41_45:No of lactating mothers by age 41-45',
                # 'no_of_lactating_mothers_by_age_46_50:No of lactating mothers by age 46-50',
                # 'no_of_lactating_mothers_by_age_gt_50:No of lactating mothers by age > 50',
                # 'no_of_child_0_6_months_by_male:No of child 0-6 months Male',
                # 'no_of_child_0_6_months_by_female:No of child 0-6 months Female',
                # 'no_of_child_0_6_months_by_transgender:No of child 0-6 months Transgender',
                # 'no_of_child_7_24_months_by_male:No of child 7-24 months Male',
                # 'no_of_child_7_24_months_by_female:No of child 7-24 months Female',
                # 'no_of_child_7_24_months_by_transgender:No of child 7-24 months Transgender',
                'created_by', 'date_created', 'last_updated:Last Updated On']

    @classmethod
    def details_view_fields(cls):
        return [
            'detail_title',
            'code', 'city', 'render_month', 'year',
            'no_of_pregnant_women_by_age_lt_20:No of pregnant women by age below 20',
            'no_of_pregnant_women_by_age_20_25:No of pregnant women by age 20-25',
            'no_of_pregnant_women_by_age_26_30:No of pregnant women by age 26-30',
            'no_of_pregnant_women_by_age_31_35:No of pregnant women by age 31-35',
            'no_of_pregnant_women_by_age_36_40:No of pregnant women by age 36-40',
            'no_of_pregnant_women_by_age_41_45:No of pregnant women by age 41-45',
            'no_of_pregnant_women_by_age_46_50:No of pregnant women by age 46-50',
            'no_of_pregnant_women_by_age_gt_50:No of pregnant women by age above 50',
            'no_of_lactating_mothers_by_age_lt_20:No of lactating mothers by age below 20',
            'no_of_lactating_mothers_by_age_20_25:No of lactating mothers by age 20-25',
            'no_of_lactating_mothers_by_age_26_30:No of lactating mothers by age 26-30',
            'no_of_lactating_mothers_by_age_31_35:No of lactating mothers by age 31-35',
            'no_of_lactating_mothers_by_age_36_40:No of lactating mothers by age 36-40',
            'no_of_lactating_mothers_by_age_41_45:No of lactating mothers by age 41-45',
            'no_of_lactating_mothers_by_age_46_50:No of lactating mothers by age 46-50',
            'no_of_lactating_mothers_by_age_gt_50:No of lactating mothers by age above 50',
            'no_of_child_0_6_months_by_male:No of child 0-6 months Male',
            'no_of_child_0_6_months_by_female:No of child 0-6 months Female',
            'no_of_child_0_6_months_by_transgender:No of child 0-6 months Transgender',
            'no_of_child_7_24_months_by_male:No of child 7-24 months Male',
            'no_of_child_7_24_months_by_female:No of child 7-24 months Female',
            'no_of_child_7_24_months_by_transgender:No of child 7-24 months Transgender',
            'created_by', 'date_created', 'last_updated:Last Updated On'
        ]

    @staticmethod
    def month_converter(month):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        try:
            idx = months.index(month) + 1
        except:
            idx = 1
        return idx

    @staticmethod
    def to_int(value, default):
        int_ = value
        try:
            int_ = int(int_)
        except:
            return default
        return int_

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
            ImporterColumnConfig(column=1, column_name='Month', property_name='month', ignore=False),
            ImporterColumnConfig(column=2, column_name='Year', property_name='year', ignore=False),
            ImporterColumnConfig(column=3, column_name='No of pregnant women by age below 20',
                                 property_name='no_of_pregnant_women_by_age_lt_20', ignore=False),
            ImporterColumnConfig(column=4, column_name='No of pregnant women by age 20-25',
                                 property_name='no_of_pregnant_women_by_age_20_25', ignore=False),
            ImporterColumnConfig(column=5, column_name='No of pregnant women by age 26-30',
                                 property_name='no_of_pregnant_women_by_age_26_30', ignore=False),
            ImporterColumnConfig(column=6, column_name='No of pregnant women by age 31-35',
                                 property_name='no_of_pregnant_women_by_age_31_35', ignore=False),
            ImporterColumnConfig(column=7, column_name='No of pregnant women by age 36-40',
                                 property_name='no_of_pregnant_women_by_age_36_40', ignore=False),
            ImporterColumnConfig(column=8, column_name='No of lactating mothers by age 41-45',
                                 property_name='no_of_pregnant_women_by_age_41_45', ignore=False),
            ImporterColumnConfig(column=9, column_name='No of pregnant women by age 46-50',
                                 property_name='no_of_pregnant_women_by_age_46_50', ignore=False),
            ImporterColumnConfig(column=10, column_name='No of pregnant women by age above 50',
                                 property_name='no_of_pregnant_women_by_age_gt_50', ignore=False),
            ImporterColumnConfig(column=11, column_name='No of lactating mothers by age below 20',
                                 property_name='no_of_lactating_mothers_by_age_lt_20', ignore=False),
            ImporterColumnConfig(column=12, column_name='No of lactating mothers by age 20-25',
                                 property_name='no_of_lactating_mothers_by_age_20_25', ignore=False),
            ImporterColumnConfig(column=13, column_name='No of lactating mothers by age 26-30',
                                 property_name='no_of_lactating_mothers_by_age_26_30', ignore=False),
            ImporterColumnConfig(column=14, column_name='No of lactating mothers by age 31-35',
                                 property_name='no_of_lactating_mothers_by_age_31_35', ignore=False),
            ImporterColumnConfig(column=15, column_name='No of lactating mothers by age 36-40',
                                 property_name='no_of_lactating_mothers_by_age_36_40', ignore=False),
            ImporterColumnConfig(column=16, column_name='No of lactating mothers by age 41-45',
                                 property_name='no_of_lactating_mothers_by_age_41_45', ignore=False),
            ImporterColumnConfig(column=17, column_name='No of lactating mothers by age 46-50',
                                 property_name='no_of_lactating_mothers_by_age_46_50', ignore=False),
            ImporterColumnConfig(column=18, column_name='No of lactating mothers by age above 50',
                                 property_name='no_of_lactating_mothers_by_age_gt_50', ignore=False),
            ImporterColumnConfig(column=19, column_name='No of child 0-6 months Male',
                                 property_name='no_of_child_0_6_months_by_male', ignore=False),
            ImporterColumnConfig(column=20, column_name='No of child 0-6 months Female',
                                 property_name='no_of_child_0_6_months_by_female', ignore=False),
            ImporterColumnConfig(column=21, column_name='No of child 0-6 months Transgender',
                                 property_name='no_of_child_0_6_months_by_transgender', ignore=False),
            ImporterColumnConfig(column=22, column_name='No of child 7-24 months Male',
                                 property_name='no_of_child_7_24_months_by_male', ignore=False),
            ImporterColumnConfig(column=23, column_name='No of child 7-24 months Female',
                                 property_name='no_of_child_7_24_months_by_female', ignore=False),
            ImporterColumnConfig(column=24, column_name='No of child 7-24 months Transgender',
                                 property_name='no_of_child_7_24_months_by_transgender', ignore=False)
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
        update_list = []

        for index, item in enumerate(items):
            city = str(item['0']).strip()
            month = str(item['1']).strip()
            month = cls.month_converter(month)
            year = cls.to_int(str(item['2']).strip(), 2020)
            item_4 = cls.to_int(str(item['3']).strip(), None)
            item_5 = cls.to_int(str(item['4']).strip(), None)
            item_6 = cls.to_int(str(item['5']).strip(), None)
            item_7 = cls.to_int(str(item['6']).strip(), None)
            item_8 = cls.to_int(str(item['7']).strip(), None)
            item_9 = cls.to_int(str(item['8']).strip(), None)
            item_10 = cls.to_int(str(item['9']).strip(), None)
            item_11 = cls.to_int(str(item['10']).strip(), None)
            item_12 = cls.to_int(str(item['11']).strip(), None)
            item_13 = cls.to_int(str(item['12']).strip(), None)
            item_14 = cls.to_int(str(item['13']).strip(), None)
            item_15 = cls.to_int(str(item['14']).strip(), None)
            item_16 = cls.to_int(str(item['15']).strip(), None)
            item_17 = cls.to_int(str(item['16']).strip(), None)
            item_18 = cls.to_int(str(item['17']).strip(), None)
            item_19 = cls.to_int(str(item['18']).strip(), None)
            item_20 = cls.to_int(str(item['19']).strip(), None)
            item_21 = cls.to_int(str(item['20']).strip(), None)
            item_22 = cls.to_int(str(item['21']).strip(), None)
            item_23 = cls.to_int(str(item['22']).strip(), None)
            item_24 = cls.to_int(str(item['23']).strip(), None)
            item_25 = cls.to_int(str(item['24']).strip(), None)

            city_ = Geography.objects.filter(level__name='Pourashava/City Corporation', name__iexact=city).first()

            if city_:
                old_ = NutritionConditionalFoodTransfer.objects.filter(city=city_, month=month, year=year).first()
                if old_:
                    old_.no_of_pregnant_women_by_age_lt_20 = item_4
                    old_.no_of_pregnant_women_by_age_20_25 = item_5
                    old_.no_of_pregnant_women_by_age_26_30 = item_6
                    old_.no_of_pregnant_women_by_age_31_35 = item_7
                    old_.no_of_pregnant_women_by_age_36_40 = item_8
                    old_.no_of_pregnant_women_by_age_41_45 = item_9
                    old_.no_of_pregnant_women_by_age_46_50 = item_10
                    old_.no_of_pregnant_women_by_age_gt_50 = item_11
                    old_.no_of_lactating_mothers_by_age_lt_20 = item_12
                    old_.no_of_lactating_mothers_by_age_20_25 = item_13
                    old_.no_of_lactating_mothers_by_age_26_30 = item_14
                    old_.no_of_lactating_mothers_by_age_31_35 = item_15
                    old_.no_of_lactating_mothers_by_age_36_40 = item_16
                    old_.no_of_lactating_mothers_by_age_41_45 = item_17
                    old_.no_of_lactating_mothers_by_age_46_50 = item_18
                    old_.no_of_lactating_mothers_by_age_gt_50 = item_19
                    old_.no_of_child_0_6_months_by_male = item_20
                    old_.no_of_child_0_6_months_by_female = item_21
                    old_.no_of_child_0_6_months_by_transgender = item_22
                    old_.no_of_child_7_24_months_by_male = item_23
                    old_.no_of_child_7_24_months_by_female = item_24
                    old_.no_of_child_7_24_months_by_transgender = item_25
                    old_.last_updated = timestamp
                    old_.last_updated_by = user

                    timestamp += 1
                    update_list.append(old_)
                else:
                    new_ = NutritionConditionalFoodTransfer(
                        organization=organization,
                        city=city_,
                        month=month,
                        year=year,
                        no_of_pregnant_women_by_age_lt_20=item_4,
                        no_of_pregnant_women_by_age_20_25=item_5,
                        no_of_pregnant_women_by_age_26_30=item_6,
                        no_of_pregnant_women_by_age_31_35=item_7,
                        no_of_pregnant_women_by_age_36_40=item_8,
                        no_of_pregnant_women_by_age_41_45=item_9,
                        no_of_pregnant_women_by_age_46_50=item_10,
                        no_of_pregnant_women_by_age_gt_50=item_11,
                        no_of_lactating_mothers_by_age_lt_20=item_12,
                        no_of_lactating_mothers_by_age_20_25=item_13,
                        no_of_lactating_mothers_by_age_26_30=item_14,
                        no_of_lactating_mothers_by_age_31_35=item_15,
                        no_of_lactating_mothers_by_age_36_40=item_16,
                        no_of_lactating_mothers_by_age_41_45=item_17,
                        no_of_lactating_mothers_by_age_46_50=item_18,
                        no_of_lactating_mothers_by_age_gt_50=item_19,
                        no_of_child_0_6_months_by_male=item_20,
                        no_of_child_0_6_months_by_female=item_21,
                        no_of_child_0_6_months_by_transgender=item_22,
                        no_of_child_7_24_months_by_male=item_23,
                        no_of_child_7_24_months_by_female=item_24,
                        no_of_child_7_24_months_by_transgender=item_25,
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
            NutritionConditionalFoodTransfer.objects.bulk_create(create_list, batch_size=200)

        if update_list:
            NutritionConditionalFoodTransfer.objects.bulk_update(update_list, batch_size=200)

        empties = NutritionConditionalFoodTransfer.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            NutritionConditionalFoodTransfer.objects.bulk_update(update_list, batch_size=200)

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ExporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ExporterColumnConfig(column=1, column_name='Month', property_name='month', ignore=False),
            ExporterColumnConfig(column=2, column_name='Year', property_name='year', ignore=False),
            ExporterColumnConfig(column=3, column_name='No of pregnant women by age below 20',
                                 property_name='no_of_pregnant_women_by_age_lt_20', ignore=False),
            ExporterColumnConfig(column=4, column_name='No of pregnant women by age 20-25',
                                 property_name='no_of_pregnant_women_by_age_20_25', ignore=False),
            ExporterColumnConfig(column=5, column_name='No of pregnant women by age 26-30',
                                 property_name='no_of_pregnant_women_by_age_26_30', ignore=False),
            ExporterColumnConfig(column=6, column_name='No of pregnant women by age 31-35',
                                 property_name='no_of_pregnant_women_by_age_31_35', ignore=False),
            ExporterColumnConfig(column=7, column_name='No of pregnant women by age 36-40',
                                 property_name='no_of_pregnant_women_by_age_36_40', ignore=False),
            ExporterColumnConfig(column=8, column_name='No of lactating mothers by age 41-45',
                                 property_name='no_of_pregnant_women_by_age_41_45', ignore=False),
            ExporterColumnConfig(column=9, column_name='No of pregnant women by age 46-50',
                                 property_name='no_of_pregnant_women_by_age_46_50', ignore=False),
            ExporterColumnConfig(column=10, column_name='No of pregnant women by age above 50',
                                 property_name='no_of_pregnant_women_by_age_gt_50', ignore=False),
            ExporterColumnConfig(column=11, column_name='No of lactating mothers by age below 20',
                                 property_name='no_of_lactating_mothers_by_age_lt_20', ignore=False),
            ExporterColumnConfig(column=12, column_name='No of lactating mothers by age 20-25',
                                 property_name='no_of_lactating_mothers_by_age_20_25', ignore=False),
            ExporterColumnConfig(column=13, column_name='No of lactating mothers by age 26-30',
                                 property_name='no_of_lactating_mothers_by_age_26_30', ignore=False),
            ExporterColumnConfig(column=14, column_name='No of lactating mothers by age 31-35',
                                 property_name='no_of_lactating_mothers_by_age_31_35', ignore=False),
            ExporterColumnConfig(column=15, column_name='No of lactating mothers by age 36-40',
                                 property_name='no_of_lactating_mothers_by_age_36_40', ignore=False),
            ExporterColumnConfig(column=16, column_name='No of lactating mothers by age 41-45',
                                 property_name='no_of_lactating_mothers_by_age_41_45', ignore=False),
            ExporterColumnConfig(column=17, column_name='No of lactating mothers by age 46-50',
                                 property_name='no_of_lactating_mothers_by_age_46_50', ignore=False),
            ExporterColumnConfig(column=18, column_name='No of lactating mothers by age above 50',
                                 property_name='no_of_lactating_mothers_by_age_gt_50', ignore=False),
            ExporterColumnConfig(column=19, column_name='No of child 0-6 months Male',
                                 property_name='no_of_child_0_6_months_by_male', ignore=False),
            ExporterColumnConfig(column=20, column_name='No of child 0-6 months Female',
                                 property_name='no_of_child_0_6_months_by_female', ignore=False),
            ExporterColumnConfig(column=21, column_name='No of child 0-6 months Transgender',
                                 property_name='no_of_child_0_6_months_by_transgender', ignore=False),
            ExporterColumnConfig(column=22, column_name='No of child 7-24 months Male',
                                 property_name='no_of_child_7_24_months_by_male', ignore=False),
            ExporterColumnConfig(column=23, column_name='No of child 7-24 months Female',
                                 property_name='no_of_child_7_24_months_by_female', ignore=False),
            ExporterColumnConfig(column=24, column_name='No of child 7-24 months Transgender',
                                 property_name='no_of_child_7_24_months_by_transgender', ignore=False)
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

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for cdc in queryset:
            for column in columns:
                column_value = ''
                if hasattr(cdc, column.property_name):
                    column_value = str(getattr(cdc, column.property_name))
                    if column.property_name == 'month':
                        column_value = months[cls.to_int(column_value, 1) - 1]

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
