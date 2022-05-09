import uuid
from collections import OrderedDict
from datetime import datetime

from django.db import models

from blackwidow.core.models import ImporterConfig, ImporterColumnConfig, ErrorLog
from blackwidow.engine.decorators import enable_import
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import Clock
from undp_nuprp.approvals.models import SEFGrantee
from undp_nuprp.nuprp_admin.models import PrimaryGroupMember
from undp_nuprp.approvals.models.interactive_maps.output_one.word_prioritization_indicator import WordPrioritizationIndicator


__author__ = 'Ziaul Haque'


@decorate(is_object_context, enable_import, enable_export,
          route(route='sef-nutrition-grantee', group='Local Economy Livelihood and Financial Inclusion',
                module=ModuleEnum.Analysis,
                display_name='Nutrition Grantees', group_order=3, item_order=13))
class SEFNutritionGrantee(SEFGrantee):
    is_still_pregnant_or_lactating = models.CharField(max_length=128, blank=True, null=True)
    ward_poverty_index = models.CharField(max_length=128, blank=True, null=True)
    mpi = models.CharField(max_length=128, blank=True, null=True)
    grant_received_year = models.CharField(max_length=128, blank=True, null=True)
    grant_received_month = models.CharField(max_length=128, blank=True, null=True)
    number_of_pregnancy_month = models.IntegerField(blank=True, null=True)
    age_of_child_in_month = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = 'approvals'

    @staticmethod
    def to_int(value, default):
        int_ = value
        try:
            int_ = int(int_)
        except:
            return default
        return int_

    @classmethod
    def table_columns(cls):
        return (
            "code", "render_PG_member_ID", "render_pg_member_name", "age", "name:Beneficiary Name",
            "grant_received_year:Grant Received-Year", "grant_received_month:Grant Received-Month",
            "render_contact_number",
            "render_CDC", "render_city_corporation", "ward",
            "date_created:Created On", "last_updated:Last Updated On"
        )

    @property
    def details_config(self):
        details = OrderedDict()

        # basic information
        basic_info = OrderedDict()
        basic_info['pg_member_ID'] = self.render_PG_member_ID
        basic_info['pg_member_name'] = self.render_pg_member_name
        basic_info['age'] = self.age
        basic_info["Beneficiary's Name"] = self.name
        basic_info['Grant Received-Year'] = self.grant_received_year if self.grant_received_year else "N/A"
        basic_info['Grant Received-Month'] = self.grant_received_month if self.grant_received_month else "N/A"
        basic_info['contact_number'] = self.render_contact_number

        basic_info['CDC'] = self.render_CDC
        basic_info['city_corporation'] = self.render_city_corporation
        basic_info['ward'] = self.ward
        basic_info['Relationship of grantee to PG member'] = self.relation_with_pg_member
        basic_info['Is the grantee still pregnant or lactating?'] = self.is_still_pregnant_or_lactating
        basic_info['Ward Poverty Index'] = self.ward_poverty_index
        basic_info['mpi'] = self.mpi
        basic_info[
            'Number of Months (Pregnancy)'] = self.number_of_pregnancy_month if self.number_of_pregnancy_month else "N/A"
        basic_info[
            'Age of Child in Month (if Lactating)'] = self.age_of_child_in_month if self.age_of_child_in_month else "N/A"
        basic_info['remarks'] = self.remarks

        # disability status information
        disability_status_info = OrderedDict()
        disability_status_info['Has disability'] = self.has_disability
        disability_status_info['Difficulty seeing, even if wearing glasses'] = self.difficulty_in_seeing
        disability_status_info['Difficulty hearing, even if using a hearing aid'] = self.difficulty_in_hearing
        disability_status_info['Difficulty walking or climbing steps'] = self.difficulty_in_walking
        disability_status_info['Difficulty remembering or concentrating'] = self.difficulty_in_remembering
        disability_status_info['Difficulty with self-care such as washing all over or dressing'] = \
            self.difficulty_in_self_care
        disability_status_info['Difficulty communicating, for example understanding or being understood'] = \
            self.difficulty_in_communicating

        # audit information
        audit_info = OrderedDict()
        audit_info['last_updated_by'] = self.last_updated_by
        audit_info['last_updated_on'] = self.render_timestamp(self.last_updated)
        audit_info['created_by'] = self.created_by
        audit_info['created_on'] = self.render_timestamp(self.date_created)

        details["Grantee's Basic Information"] = basic_info
        details["Grantee's Disability Status"] = disability_status_info
        details["Audit Information"] = audit_info
        return details

    @classmethod
    def get_manage_buttons(cls):
        return [
            ViewActionEnum.Create, ViewActionEnum.Edit, ViewActionEnum.AdvancedImport,
            ViewActionEnum.AdvancedExport, ViewActionEnum.Delete
        ]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import"

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)

        columns = [
            ImporterColumnConfig(column=0, column_name='PG member ID', property_name='pg_member_assigned_code',
                                 ignore=False),
            ImporterColumnConfig(column=1, column_name='Pg member name', property_name='pg_member_name', ignore=False),
            ImporterColumnConfig(column=2, column_name='Age', property_name='age', ignore=False),

            ImporterColumnConfig(column=3, column_name='Beneficiary Name', property_name='name', ignore=False),
            ImporterColumnConfig(column=4, column_name='Grant Received-Year', property_name='grant_received_year',
                                 ignore=False),
            ImporterColumnConfig(column=5, column_name='Grant Received-Month', property_name='grant_received_month',
                                 ignore=False),
            ImporterColumnConfig(column=6, column_name='Contact number',
                                 property_name='contact_number', ignore=False),

            ImporterColumnConfig(column=7, column_name='Relationship of grantee to PG member',
                                 property_name='relation_with_pg_member', ignore=False),
            ImporterColumnConfig(column=8, column_name='Is the grantee still pregnant or lactating?',
                                 property_name='is_still_pregnant_or_lactating', ignore=False),
            ImporterColumnConfig(column=9, column_name='Number of Months (Pregnancy)',
                                 property_name='number_of_pregnancy_month', ignore=False),
            ImporterColumnConfig(column=10, column_name='Age of Child in Month (if Lactating)',
                                 property_name='age_of_child_in_month', ignore=False),

            ImporterColumnConfig(column=11, column_name='Has disability',
                                 property_name='has_disability', ignore=False),
            ImporterColumnConfig(column=12, column_name='Difficulty in seeing',
                                 property_name='difficulty_in_seeing', ignore=False),
            ImporterColumnConfig(column=13, column_name='Difficulty in hearing',
                                 property_name='difficulty_in_hearing', ignore=False),
            ImporterColumnConfig(column=14, column_name='Difficulty in walking',
                                 property_name='difficulty_in_walking', ignore=False),
            ImporterColumnConfig(column=15, column_name='Difficulty in remembering',
                                 property_name='difficulty_in_remembering', ignore=False),
            ImporterColumnConfig(column=16, column_name='Difficulty in self care',
                                 property_name='difficulty_in_self_care', ignore=False),
            ImporterColumnConfig(column=17, column_name='Difficulty in communicating',
                                 property_name='difficulty_in_communicating', ignore=False),
            ImporterColumnConfig(column=18, column_name='Remarks',
                                 property_name='remarks', ignore=False),
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

        available_difficulties = {
            'no difficulty': 'No difficulty',
            'some difficulty': 'Some difficulty',
            'a lot of difficulty': 'A lot of difficulty',
            'cannot do at all': 'Cannot do at all',
        }

        yes_no_dict = {
            "yes": "Yes",
            "no": "No"
        }

        month_dict = {
            'january': 'January',
            'february': 'February',
            'march': 'March',
            'april': 'April',
            'may': 'May',
            'june': 'June',
            'july': 'July',
            'august': 'August',
            'september': 'September',
            'october': 'October',
            'november': 'November',
            'december': 'December',
        }

        pregnant_or_lactating_dict = {
            'pregnant': 'Pregnant',
            'lactating': 'Lactating'
        }

        for index, item in enumerate(items):
            pg_member_assigned_code = str(item['0']).strip()
            pg_member_name = str(item['1']).strip()
            print(pg_member_name)
            age = cls.to_int(str(item['2']).strip(), None)
            name = str(item['3']).strip()
            grant_received_year = str(item['4']).strip()
            grant_received_month = str(item['5']).strip()
            if grant_received_month in month_dict.keys():
                grant_received_month = month_dict[grant_received_month]
            contact_number = str(item['6']).strip()
            try:
                pg_member_id = PrimaryGroupMember.objects.filter(assigned_code=pg_member_assigned_code).first().id
                ward_id = PrimaryGroupMember.objects.filter(assigned_code=pg_member_assigned_code).first().ward_id
                poverty_score_index = WordPrioritizationIndicator.objects.filter(Ward_id=ward_id).first().poverty_index_score
                from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
                query = PGMPIIndicator.objects.filter(primary_group_member_id=pg_member_id).values('mpi_score')

                totalMpi = 0
                if query.count()>0:
                    for j in query:
                        totalMpi += j['mpi_score']
                # poverty_score_index = 0
                # totalMpi = 0
                ward = pg_member_assigned_code[3:5] if len(pg_member_assigned_code) > 4 else ""
                if len(ward) == 1:
                    ward = "0" + str(ward)
            except Exception as exp:
                ErrorLog.log(exp=exp)
                continue

            relation_with_pg_member = str(item['7']).strip()
            is_still_pregnant_or_lactating = str(item['8']).strip().lower()
            if is_still_pregnant_or_lactating in pregnant_or_lactating_dict.keys():
                is_still_pregnant_or_lactating = pregnant_or_lactating_dict[is_still_pregnant_or_lactating]

            ward_poverty_index = poverty_score_index    
            mpi = totalMpi    

            number_of_pregnancy_month = cls.to_int(str(item['9']).strip(), None)
            age_of_child_in_month = cls.to_int(str(item['10']).strip(), None)

            has_disability = str(item['11']).strip().lower()
            if has_disability in yes_no_dict.keys():
                has_disability = yes_no_dict[has_disability]
            else:
                has_disability = ''

            difficulty_in_seeing = str(item['12']).strip().lower()
            if difficulty_in_seeing in available_difficulties.keys():
                difficulty_in_seeing = available_difficulties[difficulty_in_seeing]
            else:
                difficulty_in_seeing = ''

            difficulty_in_hearing = str(item['13']).strip().lower()
            if difficulty_in_hearing in available_difficulties.keys():
                difficulty_in_hearing = available_difficulties[difficulty_in_hearing]
            else:
                difficulty_in_hearing = ''

            difficulty_in_walking = str(item['14']).strip().lower()
            if difficulty_in_walking in available_difficulties.keys():
                difficulty_in_walking = available_difficulties[difficulty_in_walking]
            else:
                difficulty_in_walking = ''

            difficulty_in_remembering = str(item['15']).strip().lower()
            if difficulty_in_remembering in available_difficulties.keys():
                difficulty_in_remembering = available_difficulties[difficulty_in_remembering]
            else:
                difficulty_in_remembering = ''

            difficulty_in_self_care = str(item['16']).strip().lower()
            if difficulty_in_self_care in available_difficulties.keys():
                difficulty_in_self_care = available_difficulties[difficulty_in_self_care]
            else:
                difficulty_in_self_care = ''

            difficulty_in_communicating = str(item['17']).strip().lower()
            if difficulty_in_communicating in available_difficulties.keys():
                difficulty_in_communicating = available_difficulties[difficulty_in_communicating]
            else:
                difficulty_in_communicating = ''

            remarks = str(item['18']).strip()

            new_ = SEFNutritionGrantee(
                organization=organization,
                pg_member_assigned_code=pg_member_assigned_code,
                pg_member_id=pg_member_id,
                pg_member_name=pg_member_name,
                age=age,
                name=name,
                grant_received_year=grant_received_year,
                grant_received_month=grant_received_month,
                contact_number=contact_number,
                ward=ward,
                relation_with_pg_member=relation_with_pg_member,
                is_still_pregnant_or_lactating=is_still_pregnant_or_lactating,
                ward_poverty_index=ward_poverty_index,
                mpi=mpi,
                number_of_pregnancy_month=number_of_pregnancy_month,
                age_of_child_in_month=age_of_child_in_month,
                has_disability=has_disability,
                difficulty_in_seeing=difficulty_in_seeing,
                difficulty_in_hearing=difficulty_in_hearing,
                difficulty_in_walking=difficulty_in_walking,
                difficulty_in_remembering=difficulty_in_remembering,
                difficulty_in_self_care=difficulty_in_self_care,
                difficulty_in_communicating=difficulty_in_communicating,
                remarks=remarks,

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
            SEFNutritionGrantee.objects.bulk_create(create_list, batch_size=500)

        empties = SEFNutritionGrantee.objects.using('default').filter(code='')
        update_list = []

        for empty in empties:
            empty.code = empty.code_prefix + empty.code_separator + str(empty.id).zfill(5)
            update_list.append(empty)

        if update_list:
            SEFNutritionGrantee.objects.bulk_update(update_list, batch_size=200, )

    @classmethod
    def export_file_columns(cls):
        """
        this method is used to get the list of columns to be exported
        :return: a list of column properties
        """

        _table_columns = [
            "code", "render_PG_member_ID", "render_pg_member_name", 'age', "name:Beneficiary Name",
            "grant_received_year:Grant Received-Year", "grant_received_month:Grant Received-Month",
            "render_contact_number",
            "render_CDC_name", "render_CDC_ID", "render_city_corporation", "ward",
            "relation_with_pg_member:Relationship of grantee to PG member",
            "date_created:Created On", "last_updated:Last Updated On"
        ]

        return _table_columns + list(cls.details_view_fields())

    @classmethod
    def details_view_fields(cls):
        """
        this method is used to get the list of fields used in the details view
        :return: list of strings (names of fields in details view)
        """
        return [
            'is_still_pregnant_or_lactating','ward_poverty_index','mpi', 'number_of_pregnancy_month:Number of Months (Pregnancy)',
            'age_of_child_in_month:Age of Child in Month (if Lactating)', 'difficulty_in_seeing',
            'difficulty_in_hearing', 'difficulty_in_walking', 'difficulty_in_remembering', 'has_disability',
            'difficulty_in_self_care', 'difficulty_in_communicating', 'render_total_installment', 'remarks',
        ]

    @classmethod
    def apply_search_filter(cls, search_params=None, queryset=None, **kwargs):
        queryset = super(SEFGrantee, cls).apply_search_filter(search_params=search_params, queryset=queryset, **kwargs)

        if search_params.get('city', None):
            city_param = search_params.get('city')
            city_ids = [int(x) for x in city_param.split(',')]
            queryset = queryset.filter(
                pg_member__assigned_to__parent__address__geography__parent__id__in=city_ids
            )

        if search_params.get('year', None):
            target_year = int(search_params.get('year'))
            _from_datetime = datetime(year=target_year, month=1, day=1).timestamp() * 1000
            _to_datetime = datetime(year=target_year + 1, month=1, day=1).timestamp() * 1000 - 1
            queryset = queryset.filter(date_created__gte=_from_datetime, date_created__lte=_to_datetime)

        return queryset
