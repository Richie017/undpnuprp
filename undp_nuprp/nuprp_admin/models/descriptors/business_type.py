import uuid
from collections import OrderedDict

from unidecode import unidecode

from blackwidow.core.models import Organization, MaxSequence
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from undp_nuprp.nuprp_admin.models.descriptors.sub_sector import SubSector

__author__ = 'Ziaul Haque'


@decorate(is_object_context, enable_import,
          route(route='business-sub-sector', group='Descriptors',
                module=ModuleEnum.Settings, display_name="Business Sub Sector", item_order=2))
class BusinessType(SubSector):
    class Meta:
        proxy = True
        app_label = 'nuprp_admin'

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import"

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.Delete, ViewActionEnum.AdvancedImport]

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
        from blackwidow.core.models.config.importer_config import ImporterConfig

        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        if result or importer_config.columns.count() == 0:
            importer_config.save(**kwargs)
        else:
            importer_config.columns.all().delete()

        columns = [
            ImporterColumnConfig(column=0, column_name='Sector', property_name='parent_name', ignore=False),
            ImporterColumnConfig(column=1, column_name='Sub Sector', property_name='name', ignore=False),
        ]
        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def run_post_processing_import(cls, items=[], user=None, organization=None, **kwargs):
        from undp_nuprp.nuprp_admin.models import BusinessSector

        organization = organization if organization else Organization.get_organization_from_cache()

        sector_dict = OrderedDict()
        sectors_update = list()
        sectors_create = list()
        creatable_sector_names = list()
        updatable_sector_names = list()
        sector_max_seqs, created = MaxSequence.objects.get_or_create(context=BusinessSector.__name__)
        sector_seqs_value = sector_max_seqs.value
        for sector in BusinessSector.objects.all():
            _sector_name = unidecode(sector.name).lower()
            sector_dict[_sector_name] = sector
        time_now = Clock.timestamp()
        _error_count = 0
        for index, item in enumerate(items):
            try:
                sector_name = item['0']
                if sector_name:
                    _sector_name = unidecode(sector_name).lower()
                    if _sector_name in sector_dict.keys():
                        sector = sector_dict[_sector_name]
                        sector.name = sector_name
                        if sector.code is None or sector.code == '':
                            sector.code = sector.code_prefix + \
                                            sector.code_separator + \
                                            str(sector_seqs_value).zfill(5)
                            sector_seqs_value += 1
                        sector.tsync_id = uuid.uuid4() \
                            if sector.tsync_id is None else sector.tsync_id
                        sector.last_updated = time_now
                        time_now += 1
                        if _sector_name not in updatable_sector_names:
                            sectors_update.append(sector)
                            updatable_sector_names.append(_sector_name)

                    elif _sector_name not in creatable_sector_names:
                        sector = BusinessSector(
                            name=sector_name,
                            organization_id=organization.pk
                        )
                        sector.date_created = time_now
                        time_now += 1
                        sector.type = BusinessSector.__name__
                        sector.tsync_id = uuid.uuid4() \
                            if sector.tsync_id is None else sector.tsync_id
                        sector.last_updated = time_now
                        time_now += 1
                        sector.code = sector.code_prefix + \
                                        sector.code_separator + \
                                        str(sector_seqs_value).zfill(5)
                        sector_seqs_value += 1
                        sectors_create.append(sector)
                        creatable_sector_names.append(_sector_name)
            except:
                _error_count += 1
                
        sector_max_seqs.value = sector_seqs_value
        sector_max_seqs.save()
        if len(sectors_create) > 0:
            BusinessSector.objects.bulk_create(sectors_create)
        if len(sectors_update) > 0:
            BusinessSector.objects.bulk_update(sectors_update)
        sector_dict = OrderedDict()
        for sector in BusinessSector.objects.all():
            _sector_name = unidecode(sector.name).lower()
            sector_dict[_sector_name] = sector

        sub_sector_dict = OrderedDict()
        sub_sector_update = list()
        sub_sector_create = list()
        creatable_sub_sector_names = list()
        updatable_sub_sector_names = list()
        sub_sector_max_seqs, created = MaxSequence.objects.get_or_create(context=BusinessType.__name__)
        sub_sector_seqs_value = sub_sector_max_seqs.value
        for sub_sector in BusinessType.objects.all():
            _sub_sector_name = unidecode(sub_sector.name).lower()
            _sector_name = unidecode(sub_sector.parent.name).lower() if sub_sector.parent else ''
            _sub_sector_key = (_sector_name, _sub_sector_name)
            sub_sector_dict[_sub_sector_key] = sub_sector
        time_now = Clock.timestamp()
        for index, item in enumerate(items):
            try:
                sector_name = item['0']
                if sector_name:
                    sector = None
                    _sector_name = unidecode(sector_name).lower()
                    if _sector_name in sector_dict.keys():
                        sector = sector_dict[_sector_name]
                    sub_sector_name = item['1']
                    if sub_sector_name:
                        _sub_sector_name = unidecode(sub_sector_name).lower()
                        _sub_sector_key = (_sector_name, _sub_sector_name)
                        if _sub_sector_key in sub_sector_dict.keys():
                            sub_sector = sub_sector_dict[_sub_sector_key]
                            sub_sector.name = sub_sector_name
                            sub_sector.parent_id = sector.pk if sector else None
                            if sub_sector.code is None or sub_sector.code == '':
                                sub_sector.code = sub_sector.code_prefix + \
                                             sub_sector.code_separator + \
                                             str(sub_sector_seqs_value).zfill(5)
                                sub_sector_seqs_value += 1
                            sub_sector.tsync_id = uuid.uuid4() \
                                if sub_sector.tsync_id is None else sub_sector.tsync_id
                            sub_sector.last_updated = time_now
                            time_now += 1
                            if _sub_sector_key not in updatable_sub_sector_names:
                                sub_sector_update.append(sub_sector)
                                updatable_sub_sector_names.append(_sub_sector_key)
                        elif _sub_sector_key not in creatable_sub_sector_names:
                            sub_sector = BusinessType(
                                name=sub_sector_name,
                                organization_id=organization.pk
                            )
                            sub_sector.date_created = time_now
                            time_now += 1
                            sub_sector.parent_id = sector.pk if sector else None
                            sub_sector.type = BusinessType.__name__
                            sub_sector.tsync_id = uuid.uuid4() \
                                if sub_sector.tsync_id is None else sub_sector.tsync_id
                            sub_sector.last_updated = time_now
                            time_now += 1
                            sub_sector.code = sub_sector.code_prefix + sub_sector.code_separator + \
                                         str(sub_sector_seqs_value).zfill(5)
                            sub_sector_seqs_value += 1
                            sub_sector_create.append(sub_sector)
                            creatable_sub_sector_names.append(_sub_sector_key)
            except:
                pass
        sub_sector_max_seqs.value = sub_sector_seqs_value
        sub_sector_max_seqs.save()
        if len(sub_sector_create) > 0:
            BusinessType.objects.bulk_create(sub_sector_create)
        if len(sub_sector_update) > 0:
            BusinessType.objects.bulk_update(sub_sector_update)

        print('error %d' % _error_count)
        print('creatable sector %d' % len(sectors_create))
        print('updateable sector %d' % len(sectors_update))
        print('creatable sub_sector %d' % len(sub_sector_create))
        print('updateable sub_sector %d' % len(sub_sector_update))
