import uuid
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models

from blackwidow.core.models import ImporterConfig, ImporterColumnConfig, Geography, ImageFileObject, Location
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock

__author__ = 'Ziaul Haque'

from blackwidow.engine.routers.database_router import BWDatabaseRouter

INTERVENTIONS = [
    'Footpath', 'Drain and/or Culvert', 'Solar Street Light', 'Non-Solar Street Light',
    'Deep Tubewell', 'Deep Tubewell with submersible pump', 'Bathroom', 'Twin Pit Latrine',
    'Single Pit Latrine', 'Septic Tank', 'Community Latrine', 'Multipurpose Use Center',
    'Road', 'Embankment cum Road'
]

REPORT_TYPES = [
    'SIF', 'CRMIF'
]


@decorate(is_object_context, enable_import, enable_export, route(
    route='sif-crmif-interventions', group='Interactive Mapping', module=ModuleEnum.Analysis,
    display_name='SIF & CRMIF Intervention', group_order=4, item_order=6), )
class SIFAndCRMIFIntervention(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', on_delete=models.CASCADE)
    image = models.ForeignKey('core.ImageFileObject', null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey('core.Location', on_delete=models.CASCADE)

    survey_time = models.DateField(null=True)
    type_of_report = models.CharField(max_length=256)
    type_of_intervention = models.CharField(max_length=256)
    footpath_length = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    drain_length = models.DecimalField(max_digits=16, decimal_places=2, null=True)
    number_of_benefited_households = models.IntegerField(null=True)

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
    def render_survey_time(self):
        return self.survey_time.strftime("%d/%m/%Y") if self.survey_time else 'N/A'

    @property
    def render_latitude(self):
        return self.location.latitude

    @property
    def render_longitude(self):
        return self.location.longitude

    @property
    def render_image_link(self):
        if self.image and self.image.relative_url:
            relative_url = self.image.relative_url
            if not settings.S3_STATIC_ENABLED:
                photo_href = settings.SITE_ROOT + relative_url[1:]
            else:
                photo_href = relative_url
            return photo_href
        else:
            return "N/A"

    @classmethod
    def table_columns(cls):
        return [
            'code', 'city', 'render_survey_time', 'type_of_report', 'type_of_intervention',
            'location', 'created_by', 'last_updated'
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
        d['City'] = self.city
        d['Survey Time'] = self.render_survey_time
        d['Type of Report'] = self.type_of_report
        d['Type of Intervention'] = self.type_of_intervention
        if self.type_of_intervention == "Footpath":
            d['Length of the footpath in meter'] = self.footpath_length if self.footpath_length else 'N/A'
        if self.type_of_intervention == "Drain and/or Culvert":
            d['Length of the drain in meter (average)'] = self.drain_length if self.drain_length else 'N/A'
        d['Total number of Households benefiting from this facility'] = self.number_of_benefited_households \
            if self.number_of_benefited_households else 'N/A'
        d['Location'] = self.location
        d['Image'] = self.image if self.image else "N/A"

        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by if self.last_updated_by else 'N/A'
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by if self.created_by else 'N/A'
        audit_info['created_on'] = self.render_timestamp(self.date_created)
        d["Audit Information"] = audit_info

        return d

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.AdvancedExport,
            ViewActionEnum.AdvancedImport, ViewActionEnum.Delete,
        ]

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.using(BWDatabaseRouter.get_write_database_name()).filter(
            model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.using(
            BWDatabaseRouter.get_write_database_name()).get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(using=BWDatabaseRouter.get_write_database_name(), **kwargs)

        columns = [
            ImporterColumnConfig(column=0, column_name='Type of Report', property_name='type_of_report', ignore=False),
            ImporterColumnConfig(column=1, column_name='Code', property_name='code', ignore=False),
            ImporterColumnConfig(column=2, column_name='City', property_name='city', ignore=False),
            ImporterColumnConfig(column=3, column_name='Survey Time', property_name='survey_time', ignore=False),
            ImporterColumnConfig(column=4, column_name='Latitude', property_name='render_latitude', ignore=False),
            ImporterColumnConfig(column=5, column_name='Longitude', property_name='render_longitude', ignore=False),
            ImporterColumnConfig(column=6, column_name='Type of Intervention', property_name='type_of_intervention',
                                 ignore=False),
            ImporterColumnConfig(column=7, column_name='Length of the footpath in meter',
                                 property_name='footpath_length', ignore=False),
            ImporterColumnConfig(column=8, column_name='Length of the drain in meter (average)',
                                 property_name='drain_length', ignore=False),
            ImporterColumnConfig(column=9, column_name='Total number of Households benefiting from this facility',
                                 property_name='number_of_benefited_households', ignore=False),
            ImporterColumnConfig(column=10, column_name='Image link', property_name='render_image_link', ignore=False),
        ]

        for c in columns:
            c.save(organization=organization, using=BWDatabaseRouter.get_write_database_name(), **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @staticmethod
    def to_int(value, default=None):
        if value is None:
            return None
        try:
            return int(str(value).strip())
        except Exception as exp:
            return default

    @staticmethod
    def to_decimal(value, default=None):
        if value is None:
            return None
        try:
            return Decimal(str(value).strip())
        except Exception as exp:
            return default

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        write_db = BWDatabaseRouter.get_write_database_name()
        current_timestamp = Clock.timestamp()
        create_list = []
        update_list = []

        # interventions with lower case
        interventions = [_intervention.lower() for _intervention in INTERVENTIONS]

        # report types with lower case
        report_types = [_report_type.lower() for _report_type in REPORT_TYPES]

        for index, item in enumerate(items):
            # Validating each row - Start
            report_type = str(item['0']).strip().lower() if item["0"] is not None else None
            if report_type == "":
                report_type = None

            code = str(item['1']).strip() if item["1"] is not None else None
            if code == "":
                code = None

            city = str(item['2']).strip() if item['2'] is not None else None
            if city == "":
                city = None

            survey_time = item["3"]

            latitude = str(item['4']).strip() if item["4"] is not None else None
            if latitude == "":
                latitude = None

            longitude = str(item['5']).strip() if item["5"] is not None else None
            if longitude == "":
                longitude = None

            intervention_type = str(item['6']).strip().lower() if item["6"] is not None else None
            if intervention_type == "":
                intervention_type = None

            footpath_length = cls.to_decimal(item['7']) if item["7"] is not None else None
            drain_length = cls.to_decimal(item['8']) if item["8"] is not None else None
            number_of_benefited_households = cls.to_int(item['9']) if item["9"] is not None else None
            image_link = str(item['10']).strip() if item["10"] is not None else None
            if image_link == "":
                image_link = None
            # Validating each row - End

            # Retrieving the Foreign Key data and validation - Start
            city_reference = Geography.objects.using(write_db).filter(
                name__iexact=city, level__name='Pourashava/City Corporation').first()

            if not city or not city_reference or not latitude or not longitude or not intervention_type or \
                    not report_type:
                continue

            if report_type not in report_types:
                continue
            report_type = REPORT_TYPES[report_types.index(report_type)]

            if intervention_type not in interventions:
                continue
            intervention_type = INTERVENTIONS[interventions.index(intervention_type)]

            survey_time_ = None
            if isinstance(survey_time, datetime):
                survey_time_ = survey_time.date()
            elif isinstance(survey_time, str):
                st = survey_time.strip()
                survey_time_ = datetime.strptime(st, "%d/%m/%Y").date() if st != "" else None

            try:
                image_reference = ImageFileObject.objects.using(write_db).filter(
                    name=image_link.split('static_media/uploads/')[1]).first() if image_link else None
            except Exception as exp:
                image_reference = None
            # Retrieving the Foreign Key data and validation - End

            # Preparing updatable bulk instances - Start
            if code:
                try:
                    intervention_instance = SIFAndCRMIFIntervention.objects.using(write_db).get(code=code)
                except (ObjectDoesNotExist, MultipleObjectsReturned) as exp:
                    continue
                Location.objects.using(write_db).filter(pk=intervention_instance.location.pk).update(
                    latitude=latitude, longitude=longitude)

                intervention_instance.type_of_report = report_type
                intervention_instance.city = city_reference
                intervention_instance.type_of_intervention = intervention_type
                intervention_instance.image = image_reference
                intervention_instance.survey_time = survey_time_
                intervention_instance.footpath_length = footpath_length
                intervention_instance.drain_length = drain_length
                intervention_instance.number_of_benefited_households = number_of_benefited_households
                intervention_instance.last_updated_by = user
                intervention_instance.last_updated = current_timestamp
                update_list.append(intervention_instance)
                continue
            # Preparing updatable bulk instances - End

            # Preparing creatable bulk instances - Start
            location_reference = Location.objects.using(write_db).create(latitude=latitude, longitude=longitude)
            intervention_instance = SIFAndCRMIFIntervention(
                organization=organization, city=city_reference, type_of_report=report_type,
                type_of_intervention=intervention_type, location=location_reference, date_created=current_timestamp,
                created_by=user, tsync_id=uuid.uuid4(), last_updated=current_timestamp, last_updated_by=user,
                type=cls.__name__, image=image_reference, survey_time=survey_time_, footpath_length=footpath_length,
                drain_length=drain_length, number_of_benefited_households=number_of_benefited_households)
            current_timestamp += 1
            create_list.append(intervention_instance)
            # Preparing creatable bulk instances - End

        # Creating creatable bulk instances - Start
        if create_list:
            SIFAndCRMIFIntervention.objects.using(write_db).bulk_create(objs=create_list, batch_size=500)
        # Creating creatable bulk instances - End

        # Updating updatable bulk instances - Start
        if update_list:
            SIFAndCRMIFIntervention.objects.bulk_update(objs=update_list, using=write_db, batch_size=500)
        # Updating updatable bulk instances - End

        # Preparing already created bulk instances `code` value - Start
        update_list = []
        for empty in SIFAndCRMIFIntervention.objects.using(write_db).filter(code=""):
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)
        # Preparing already created bulk instances `code` value - End

        # Updating updatable bulk instances due to `code` value - Start
        if update_list:
            SIFAndCRMIFIntervention.objects.bulk_update(objs=update_list, using=write_db, batch_size=500)
        # Updating updatable bulk instances due to `code` value - End

    @classmethod
    def export_file_columns(cls):
        return [
            "type_of_report", "code", 'city', 'render_survey_time', 'render_latitude', 'render_longitude',
            'type_of_intervention', 'footpath_length:Length of the footpath in meter',
            'drain_length:Length of the drain in meter (average)',
            'number_of_benefited_households:Total number of Households benefiting from this facility',
            'render_image_link'
        ]
