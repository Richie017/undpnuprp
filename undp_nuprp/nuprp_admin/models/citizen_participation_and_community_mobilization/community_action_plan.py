import uuid
from datetime import date
from django.db import models
from django.forms import Form
from django import forms
from django.utils.safestring import mark_safe

from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.models import Geography, ImporterConfig, ImporterColumnConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from blackwidow.engine.routers.database_router import BWDatabaseRouter


@decorate(is_object_context, enable_import,
          route(route='community-action-plan', group='Social Mobilization and Community Capacity Building',
                module=ModuleEnum.Analysis, display_name='Community Action Plan (CAP)', group_order=2,
                item_order=3)
          )
class CommunityActionPlan(OrganizationDomainEntity):
    city = models.ForeignKey('core.Geography', null=True, blank=True)
    year = models.CharField(max_length=4, null=True, blank=True)
    ward_no = models.CharField(max_length=20, null=True, blank=True)
    cap_developed = models.IntegerField(null=True, blank=True)
    approved_proposals = models.TextField(blank=True)
    how_many_of_approved_infrastructure_proposals = models.IntegerField(null=True, blank=True)
    how_many_of_approved_social_development_proposals = models.IntegerField(null=True, blank=True)
    how_many_of_approved_business_and_employment_proposals = models.IntegerField(null=True, blank=True)
    cap_integrated_in_ward_planning = models.CharField(max_length=3, null=True, blank=True)

    @property
    def detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_city(self):
        return self.city.name if self.city else 'N/A'

    @classmethod
    def details_view_fields(cls):
        return [
            'detail_title', 'year', 'render_city', 'ward_no', 'cap_developed:How many CAP developed?',
            'approved_proposals',
            'how_many_of_approved_infrastructure_proposals', 'how_many_of_approved_social_development_proposals',
            'how_many_of_approved_business_and_employment_proposals',
            'cap_integrated_in_ward_planning:CAP integrated in ward planning?',
            'created_by', 'date_created', 'last_updated:Last Updated On'
        ]

    @classmethod
    def table_columns(cls):
        return [
            'code', 'year', 'render_city', 'ward_no', 'cap_developed:How many CAP developed?', 'approved_proposals',
            'cap_integrated_in_ward_planning:CAP integrated in ward planning?',
            'created_by', 'date_created', 'last_updated:Last Updated On'
        ]

    @classmethod
    def export_file_columns(cls):
        return ['code'] + list(cls.details_view_fields())

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit,
            ViewActionEnum.AdvancedExport, ViewActionEnum.Delete,
            ViewActionEnum.AdvancedImport
        ]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        if button == ViewActionEnum.AdvancedImport:
            return 'Import'
        return button

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, created = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        columns = [
            ImporterColumnConfig(column=0, column_name='Year', property_name='year', ignore=False),
            ImporterColumnConfig(column=1, column_name='City', property_name='city', ignore=False),
            ImporterColumnConfig(column=2, column_name='Ward no', property_name='ward_no', ignore=False),
            ImporterColumnConfig(column=3, column_name='How many CAP developed?', property_name='cap_developed',
                                 ignore=False),
            ImporterColumnConfig(column=4, column_name='Select approved proposals', property_name='approved_proposals',
                                 ignore=False),
            ImporterColumnConfig(column=5, column_name='How many of approved infrastructure proposals',
                                 property_name='how_many_of_approved_infrastructure_proposals', ignore=False),
            ImporterColumnConfig(column=6, column_name='How many of approved social development proposals',
                                 property_name='how_many_of_approved_social_development_proposals', ignore=False),
            ImporterColumnConfig(column=7, column_name='How many of approved business and employment proposals',
                                 property_name='how_many_of_approved_business_and_employment_proposals', ignore=False),
            ImporterColumnConfig(column=8, column_name='CAP integrated in ward planning?',
                                 property_name='cap_integrated_in_ward_planning', ignore=False),
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
            infrastructure_proposals = None
            social_development_proposals = None
            business_and_employment_proposals = None
            year = str(item['0']).strip() if item['0'] else None
            city = str(item['1']).strip() if item['1'] else None
            ward_no = str(item['2']).strip() if item['2'] else ''
            if len(ward_no) == 1:
                ward_no = "0" + str(ward_no)
            cap_developed = int(str(item['3']).strip()) if item['3'] else None
            approved_proposals = str(item['4']).strip() if item['4'] else ''
            if approved_proposals:
                _approved_proposals = approved_proposals.split(',')
                for _item in _approved_proposals:
                    _item = _item.strip()
                    if _item == 'Infrastructure':
                        infrastructure_proposals = int(str(item['5']).strip()) if item['5'] else None
                    elif _item == 'Social Development':
                        social_development_proposals = int(str(item['6']).strip()) if item['6'] else None
                    elif _item == 'Business and Employment':
                        business_and_employment_proposals = int(str(item['7']).strip()) if item['7'] else None

            cap_integration = str(item['8']).strip() if item['8'] else ''

            city_ = Geography.objects.filter(level__name='Pourashava/City Corporation', name__iexact=city)

            new_ = CommunityActionPlan(
                organization=organization,
                year=year,
                city=city_.first() if city_ else None,
                ward_no=ward_no,
                cap_developed=cap_developed,
                approved_proposals=approved_proposals,
                how_many_of_approved_infrastructure_proposals=infrastructure_proposals,
                how_many_of_approved_social_development_proposals=social_development_proposals,
                how_many_of_approved_business_and_employment_proposals=business_and_employment_proposals,
                cap_integrated_in_ward_planning=cap_integration,
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
            CommunityActionPlan.objects.bulk_create(create_list, batch_size=200)

        empties = CommunityActionPlan.objects.filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            CommunityActionPlan.objects.bulk_update(update_list, batch_size=200)

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

