import uuid
from collections import OrderedDict

from django.db import models

from blackwidow.core.models import ImporterColumnConfig, ImporterConfig, Geography
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock

__author__ = 'Kaikobud'


@decorate(is_object_context, route(
    route='value-of-total-savings', group='Interactive Mapping', module=ModuleEnum.Analysis,
    display_name='Value of Total Savings', group_order=4, item_order=4), enable_import)
class TotalSaving(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography')
    value_of_total_savings = models.DecimalField(max_digits=20, decimal_places=2, null=True)

    class Meta:
        app_label = 'approvals'

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedImport:
            return "Import"

    @classmethod
    def table_columns(cls):
        return [
            'code', 'city', 'value_of_total_savings',
            'created_by', 'last_updated'
        ]

    @property
    def details_config(self):
        d = OrderedDict()
        d['City'] = self.city
        d['Value of Total Savings'] = self.value_of_total_savings

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
        return [ViewActionEnum.AdvancedImport, ViewActionEnum.Delete]

    @staticmethod
    def to_decimal(value, default):
        dec_ = value
        try:
            dec_ = float(dec_)
        except:
            return default
        return dec_

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)

        columns = [
            ImporterColumnConfig(column=0, column_name='City', property_name='city', ignore=False),
            ImporterColumnConfig(column=1, column_name='Value of Total Savings',
                                 property_name='value_of_total_savings', ignore=False),
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
            item_1 = cls.to_decimal(str(item['1']).strip(), None)

            city_ = Geography.objects.filter(level__name='Pourashava/City Corporation', name__iexact=city).first()

            if city_:
                new_ = TotalSaving(
                    city=city_,
                    organization=organization,
                    value_of_total_savings=item_1,
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
            TotalSaving.objects.bulk_create(create_list, batch_size=200)

        empties = TotalSaving.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            TotalSaving.objects.bulk_update(update_list, batch_size=200)

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
