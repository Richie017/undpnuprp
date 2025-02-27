import uuid
from collections import OrderedDict

from django.db import models

from blackwidow.core.models import ImporterConfig, ImporterColumnConfig, Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock

__author__ = 'Ziaul Haque'


@decorate(is_object_context, enable_import, route(
    route='low-cost-housing-units', group='Interactive Mapping', module=ModuleEnum.Analysis,
    display_name='Number of Low-Cost Housing Units', group_order=4, item_order=1), )
class LowCostHousingUnit(OrganizationDomainEntity):
    ward = models.ForeignKey('core.Geography')

    number_of_housing_units = models.IntegerField(null=True)
    number_of_male_pg_member_benefiting = models.IntegerField(null=True)
    number_of_female_pg_member_benefiting = models.IntegerField(null=True)
    number_of_male_non_pg_member_benefiting = models.IntegerField(null=True)
    number_of_female_non_pg_member_benefiting = models.IntegerField(null=True)
    number_of_male_with_disabilities = models.IntegerField(null=True)
    number_of_female_with_disabilities = models.IntegerField(null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedImport:
            return "Import"
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        return button

    @property
    def render_city(self):
        return self.ward.parent

    @classmethod
    def table_columns(cls):
        return [
            'code', 'render_city', 'ward', 'number_of_housing_units',
            'number_of_male_pg_member_benefiting:Number of PG Members benefiting (Male)',
            'number_of_female_pg_member_benefiting:Number of PG Members benefiting (Female)',
            'number_of_male_non_pg_member_benefiting:Number of Non-PG Members benefiting (Male)',
            'number_of_female_non_pg_member_benefiting:Number of Non-PG Members benefiting (Female)',
            'number_of_male_with_disabilities:Number of people with disabilities (Male)',
            'number_of_female_with_disabilities:Number of people with disabilities (Female)',
            'created_by', 'last_updated'
        ]

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Delete',
                action='delete',
                icon='fbx-rightnav-delete',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Delete),
                classes='manage-action all-action confirm-action',
                parent=None
            )
        ]

    @property
    def details_config(self):
        d = OrderedDict()
        d['City'] = self.render_city
        d['Ward No.'] = self.ward
        d['No. of Housing Units'] = self.number_of_housing_units
        d['Number of PG Members benefiting (Male)'] = self.number_of_male_pg_member_benefiting
        d['Number of PG Members benefiting (Female)'] = self.number_of_female_pg_member_benefiting
        d['Number of Non-PG Members benefiting (Male)'] = self.number_of_male_non_pg_member_benefiting
        d['Number of Non-PG Members benefiting (Female)'] = self.number_of_female_non_pg_member_benefiting
        d['Number of people with disabilities (Male)'] = self.number_of_male_with_disabilities
        d['Number of people with disabilities (Female)'] = self.number_of_female_with_disabilities

        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by
        audit_info['created_on'] = self.render_timestamp(self.date_created)
        d["Audit Information"] = audit_info

        return d

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.AdvancedImport, ViewActionEnum.Delete,
        ]

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
            ImporterColumnConfig(column=2, column_name='No. of Housing Units', property_name='number_of_housing_units',
                                 ignore=False),
            ImporterColumnConfig(column=3, column_name='Number of PG Members benefiting (Male)',
                                 property_name='number_of_male_pg_member_benefiting', ignore=False),
            ImporterColumnConfig(column=4, column_name='Number of PG Members benefiting (Female)',
                                 property_name='number_of_female_pg_member_benefiting', ignore=False),
            ImporterColumnConfig(column=5, column_name='Number of Non-PG Members benefiting (Male)',
                                 property_name='number_of_male_non_pg_member_benefiting', ignore=False),
            ImporterColumnConfig(column=6, column_name='Number of Non-PG Members benefiting (Female)',
                                 property_name='number_of_female_non_pg_member_benefiting', ignore=False),
            ImporterColumnConfig(column=7, column_name='Number of people with disabilities (Male)',
                                 property_name='number_of_male_with_disabilities', ignore=False),
            ImporterColumnConfig(column=8, column_name='Number of people with disabilities (Female)',
                                 property_name='number_of_female_with_disabilities', ignore=False),
        ]

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @staticmethod
    def to_int(value, default):
        int_ = value
        try:
            int_ = int(int_)
        except:
            return default
        return int_

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        current_timestamp = Clock.timestamp()
        create_list = []

        for index, item in enumerate(items):
            city = str(item['0']).strip()
            ward_no = str(item['1']).strip()
            number_of_housing_units = cls.to_int(str(item['2']).strip(), None)
            number_of_male_pg_member_benefiting = cls.to_int(str(item['3']).strip(), None)
            number_of_female_pg_member_benefiting = cls.to_int(str(item['4']).strip(), None)
            number_of_male_non_pg_member_benefiting = cls.to_int(str(item['5']).strip(), None)
            number_of_female_non_pg_member_benefiting = cls.to_int(str(item['6']).strip(), None)
            number_of_male_with_disabilities = cls.to_int(str(item['7']).strip(), None)
            number_of_female_with_disabilities = cls.to_int(str(item['8']).strip(), None)

            ward_ = Geography.objects.filter(
                name__iexact=ward_no,
                level__name='Ward',
                parent__name__iexact=city
            ).first()

            if ward_:
                new_ = LowCostHousingUnit(
                    organization=organization,
                    ward=ward_,
                    number_of_housing_units=number_of_housing_units,
                    number_of_male_pg_member_benefiting=number_of_male_pg_member_benefiting,
                    number_of_female_pg_member_benefiting=number_of_female_pg_member_benefiting,
                    number_of_male_non_pg_member_benefiting=number_of_male_non_pg_member_benefiting,
                    number_of_female_non_pg_member_benefiting=number_of_female_non_pg_member_benefiting,
                    number_of_male_with_disabilities=number_of_male_with_disabilities,
                    number_of_female_with_disabilities=number_of_female_with_disabilities,
                    date_created=current_timestamp,
                    created_by=user,
                    tsync_id=uuid.uuid4(),
                    last_updated=current_timestamp,
                    last_updated_by=user,
                    type=cls.__name__
                )

                current_timestamp += 1
                create_list.append(new_)

        if create_list:
            LowCostHousingUnit.objects.bulk_create(create_list, batch_size=200)

        empties = LowCostHousingUnit.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            LowCostHousingUnit.objects.bulk_update(update_list, batch_size=200)
