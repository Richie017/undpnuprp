import os
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models.query_utils import Q
from rest_framework import serializers

from blackwidow.core.generics.views.import_view import get_model
from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.file.exportfileobject import ExportFileObject
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.utility import decorate, save_audit_log
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_compress_name, bw_titleize
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.file_handlers.aws_file_writer import AWSFileWriter
from config.aws_s3_config import MEDIA_DIRECTORY
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_apprenticeship_grantee import \
    EligibleApprenticeshipGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_business_grantee import EligibleBusinessGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_drop_out_grantee import \
    EligibleEducationDropOutGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_education_early_marriage_grantee import \
    EligibleEducationEarlyMarriageGrantee
from undp_nuprp.approvals.models.grantees.eligible_grantees.eligible_grantee import EligibleGrantee
from undp_nuprp.reports.config.constants.values import BATCH_SIZE

EXPORT_FILE_ROOT = settings.EXPORT_FILE_ROOT
S3_STATIC_ENABLED = settings.S3_STATIC_ENABLED

__author__ = 'Shuvro'


@decorate(save_audit_log, expose_api('shortlisted-eligible-grantee'))
class ShortListedEligibleGrantee(EligibleGrantee):
    cdc = models.ForeignKey('nuprp_admin.CDC', null=True)
    assigned_city = models.CharField(max_length=128, blank=True, null=True)
    eligible_grantee_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    eligible_grantee_id = models.PositiveIntegerField(null=True)
    eligible_grantee = GenericForeignKey('eligible_grantee_content_type', 'eligible_grantee_id')

    class Meta:
        app_label = 'approvals'

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.AdvancedImport:
            return "Import"

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedImport, ViewActionEnum.AdvancedExport]

    @classmethod
    def distinct_fields(cls):
        return ['pg_member']

    @classmethod
    def prefetch_api_objects(cls):
        return ['pg_member', 'pg_member__assigned_to']

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.save(**kwargs)

        columns = [
            ImporterColumnConfig(column=0, column_name='Name of Beneficiary', property_name='grantee_name',
                                 ignore=False),
            ImporterColumnConfig(column=1, column_name='PG Member No', property_name='pg_member_number',
                                 ignore=False),
            ImporterColumnConfig(column=2, column_name='PG No', property_name='pg_number', ignore=False),
            ImporterColumnConfig(column=3, column_name='PG Name', property_name='pg_name', ignore=False),
            ImporterColumnConfig(column=4, column_name='PG Member Name', property_name='pg_member_name',
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
    def get_eligible_grantee(cls):
        '''

        :return: class related to short eligible grantee
        '''
        eligible_grantee_dict = {
            'ShortListedEligibleBusinessGrantee': EligibleBusinessGrantee,
            'ShortListedEligibleApprenticeshipGrantee': EligibleApprenticeshipGrantee,
            'ShortListedEligibleEducationDropOutGrantee': EligibleEducationDropOutGrantee,
            'ShortListedEligibleEducationEarlyMarriageGrantee': EligibleEducationEarlyMarriageGrantee
        }
        return eligible_grantee_dict[cls.__name__]

    @classmethod
    def get_eligible_grantee_field(cls):
        '''
            :return: class related to short eligible grantee
        '''
        grantee_field_dict = {
            'ShortListedEligibleBusinessGrantee': 'eligible_business_grantee',
            'ShortListedEligibleApprenticeshipGrantee': 'eligible_apprenticeship_grantee',
            'ShortListedEligibleEducationDropOutGrantee': 'eligible_education_dropout_grantee',
            'ShortListedEligibleEducationEarlyMarriageGrantee': 'eligible_education_early_marriage_grantee'
        }
        return grantee_field_dict[cls.__name__]

    @classmethod
    def get_short_listed_grantee(cls, eligible_grantee):
        '''

        :param eligible_grantee: an instance of eligible grantee
        (Business, Apprenticeship, Education Drop out or Early Marriage)
        :return: an instance of short listed grantee with basic fields(assigned here) of eligible grantee
        '''

        _short_listed_eligible_grantee = cls(
            survey_response=eligible_grantee.survey_response,
            pg_member=eligible_grantee.pg_member,
            cdc=eligible_grantee.pg_member.assigned_to.parent if eligible_grantee.render_cdc != '' else None,
            assigned_city=eligible_grantee.render_city,
            household_head_name=eligible_grantee.household_head_name,
            grantee_name=eligible_grantee.grantee_name,
            age=eligible_grantee.age, gender=eligible_grantee.gender,
            affiliation=eligible_grantee.affiliation,
            ethnicity=eligible_grantee.ethnicity,
            disability=eligible_grantee.disability,
            employment=eligible_grantee.employment,
            mpi_score=eligible_grantee.mpi_score,
            nuprp_grant_recipient=eligible_grantee.nuprp_grant_recipient,
            nuprp_grant_type_recipient=eligible_grantee.nuprp_grant_type_recipient,
            other_grant_recipient=eligible_grantee.other_grant_recipient,
            other_grant_type_recipient=eligible_grantee.other_grant_type_recipient,
            is_eligible=eligible_grantee.is_eligible,
            is_female_headed=eligible_grantee.is_female_headed,
            address=eligible_grantee.address,
            organization=eligible_grantee.organization,
            tsync_id=uuid.uuid4(),
            type=cls.__name__,
            eligible_grantee=eligible_grantee
        )
        return _short_listed_eligible_grantee

    @classmethod
    def _empty_field_value(cls, value):
        if value is None or value == '' or value.lower() == 'none':
            return True
        return False

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        creatable_eligible_grantees_dict = dict()
        time_now = Clock.timestamp()
        creatable_short_listed_grantees = []

        for index, item in enumerate(items):
            grantee_name = str(item['0'])
            pg_member_assigned_code = str(item['1'])
            pg_assigned_code = str(item['2'])
            pg_name = str(item['3'])
            pg_member_name = str(item['4'])

            if cls._empty_field_value(grantee_name):
                ErrorLog.log(
                    'Import file row: {0}, beneficiary name is empty!'.format(index + 1))
                continue

            if cls._empty_field_value(pg_member_assigned_code):
                ErrorLog.log(
                    'Import file row: {0}, PG member no is empty!'.format(index + 1))
                continue

            if cls._empty_field_value(pg_assigned_code):
                ErrorLog.log(
                    'Import file row: {0}, PG no is empty!'.format(index + 1))
                continue

            if cls._empty_field_value(pg_name):
                ErrorLog.log(
                    'Import file row: {0}, PG name is empty!'.format(index + 1))
                continue

            if cls._empty_field_value(pg_member_name):
                ErrorLog.log(
                    'Import file row: {0}, PG member name is empty!'.format(index + 1))
                continue

            _eligible_grantee_cls = cls.get_eligible_grantee()

            pg_member_assigned_code = pg_member_assigned_code.strip('\'')
            _eligible_grantee_queryset = _eligible_grantee_cls.objects.filter(
                pg_member__assigned_code=pg_member_assigned_code)
            _eligible_grantee_queryset = _eligible_grantee_cls.objects.filter(
                pg_member__assigned_code='0' + pg_member_assigned_code
            ) if not _eligible_grantee_queryset else _eligible_grantee_queryset

            if not _eligible_grantee_queryset:
                ErrorLog.log(
                    'Import file row: {}, PG member no: {} does not exist in the system.'.format(
                        index + 1, pg_member_assigned_code))
                continue

            pg_assigned_code = pg_assigned_code.strip('\'')
            tmp_queryset = _eligible_grantee_queryset

            tmp_queryset = tmp_queryset.filter(pg_member__assigned_to__assigned_code=pg_assigned_code)

            _eligible_grantee_queryset = tmp_queryset if tmp_queryset else _eligible_grantee_queryset.filter(
                pg_member__assigned_to__assigned_code='0' + pg_assigned_code
            )

            if not _eligible_grantee_queryset:
                ErrorLog.log(
                    'Import file row: {}, PG no: {} does not exist in the system.'.format(index + 1, pg_assigned_code))
                continue

            _eligible_grantee_queryset = _eligible_grantee_queryset.filter(pg_member__name=pg_member_name)

            if not _eligible_grantee_queryset:
                ErrorLog.log(
                    'Import file row: {}, PG member name: {} does not exist in the system.'.format(
                        index + 1, pg_member_name))
                continue

            _eligible_grantee_queryset = _eligible_grantee_queryset.filter(pg_member__assigned_to__name=pg_name)

            if not _eligible_grantee_queryset:
                ErrorLog.log(
                    'Import file row {}, PG name: {} does not exist in the system.'.format(index + 1, pg_name))
                continue

            _eligible_grantee = _eligible_grantee_queryset.filter(grantee_name=grantee_name).last()
            if not _eligible_grantee:
                ErrorLog.log(
                    'Import file row: {0}, beneficiary name: {1} does not exist in the system.'.format(
                        index + 1, grantee_name))
                continue

            creatable_eligible_grantees_dict[_eligible_grantee.id] = _eligible_grantee

        with transaction.atomic():
            try:
                existing_eligible_grantee_ids = cls.objects.filter(
                    Q(**{'eligible_grantee_id__in': creatable_eligible_grantees_dict.keys()})).values_list(
                    'eligible_grantee_id', flat=True)

                for creatable_eligible_grantee in creatable_eligible_grantees_dict.values():
                    if creatable_eligible_grantee.id not in existing_eligible_grantee_ids:
                        _short_listed_eligible_grantee = cls.get_short_listed_grantee(
                            eligible_grantee=creatable_eligible_grantee)
                        _short_listed_eligible_grantee.date_created = time_now
                        time_now += 1
                        _short_listed_eligible_grantee.last_updated = time_now
                        time_now += 1
                        _short_listed_eligible_grantee.created_by = user
                        _short_listed_eligible_grantee.last_updated_by = user
                        creatable_short_listed_grantees.append(_short_listed_eligible_grantee)
            except Exception as exp:
                ErrorLog.log(exp)

        if len(creatable_short_listed_grantees) > 0:
            cls.objects.bulk_create(creatable_short_listed_grantees)

    @classmethod
    def get_serializer(cls):
        ODESerializer = OrganizationDomainEntity.get_serializer()

        class ShortListedEligibleGranteeSerializer(ODESerializer):
            pg = serializers.SerializerMethodField(required=False)
            pg_member_assigned_code = serializers.SerializerMethodField(required=False)
            pg_member_name = serializers.SerializerMethodField(required=False)

            def get_pg_member_assigned_code(self, obj):
                return obj.pg_member.assigned_code if obj.pg_member else ''

            def get_pg_member_name(self, obj):
                return obj.pg_member.name if obj.pg_member else ''

            def get_pg(self, obj):
                return obj.pg_member.assigned_to_id if obj.pg_member else ''

            class Meta(ODESerializer.Meta):
                model = cls
                fields = (
                    'id', 'tsync_id', 'type', 'cdc', 'assigned_city', 'survey_response', 'pg', 'pg_member',
                    'pg_member_name', 'pg_member_assigned_code', 'household_head_name', 'grantee_name', 'age', 'gender',
                    'affiliation', 'ethnicity', 'disability', 'employment', 'mpi_score', 'nuprp_grant_recipient',
                    'nuprp_grant_type_recipient', 'other_grant_recipient', 'other_grant_type_recipient', 'is_eligible',
                    'is_female_headed', 'address', 'date_created', 'last_updated'
                )

        return ShortListedEligibleGranteeSerializer

    @property
    def render_other_grants(self):
        grantee_model_names = ['EligibleBusinessGrantee', 'EligibleApprenticeshipGrantee',
                               'EligibleEducationDropOutGrantee', 'EligibleEducationEarlyMarriageGrantee']
        grantee_model_names.remove(self.__class__.__name__.replace('ShortListed', ''))
        other_grants = ''
        for model_name in grantee_model_names:
            Model = get_model('approvals', model_name)
            if Model.objects.filter(pg_member_id=self.pg_member_id).exists():
                other_grants += bw_titleize(model_name) + ', '

        return other_grants.rstrip(', ')

    @classmethod
    def get_report_data(cls, queryset=None, columns=None):
        from undp_nuprp.survey.models.response.question_response import QuestionResponse

        organization = Organization.get_organization_from_cache()

        if columns is None:
            columns = cls.exporter_config(organization=organization).columns.all().order_by('date_created')

        report = list()
        headers = list()

        for column in columns:
            headers.append(column.column_name)

        report.append(headers)

        for _object in queryset:
            row = list()
            answers = QuestionResponse.objects.filter(
                section_response__survey_response_id=_object.survey_response_id).values(
                'answer_text', 'question__question_code')

            response_dict = dict()
            for answer in answers:
                if answer['question__question_code'] in response_dict.keys():
                    response_dict[answer['question__question_code']].append(answer['answer_text'])
                else:
                    response_dict[answer['question__question_code']] = [answer['answer_text']]

            for column in columns:
                _value = ''
                prop_name = column.property_name
                if hasattr(_object, prop_name):
                    _value = str(getattr(_object, prop_name))
                elif hasattr(_object.eligible_grantee, prop_name):
                    _value = str(getattr(_object.eligible_grantee, prop_name))
                elif prop_name.startswith('render_q_code_') and prop_name.endswith('_response'):
                    _value = cls.get_question_response(
                        question_code=prop_name[14:-9].replace('_', '.'), response_dict=response_dict)
                elif prop_name.startswith('render_resource_') and prop_name.endswith('_response'):
                    _value = cls.get_resource_response(
                        resource_name=column.column_name, response_dict=response_dict)
                row.append(_value)
            report.append(row)

        return report

    @classmethod
    def generate_short_listed_grantee_file(cls, start_year=2019, start_time=None, end_time=None):
        _cur_year = datetime.now().year

        while _cur_year >= start_year:
            if not start_time:
                start_time = datetime.now().replace(year=start_year, month=1, day=1, hour=0, minute=0,
                                                    second=0).timestamp() * 1000 if not start_time else start_time

            if not end_time:
                end_time = datetime.now().replace(year=start_year + 1, month=1, day=1, hour=0, minute=0,
                                                  second=0).timestamp() * 1000 - 1000 if not end_time else end_time

            available_cities = list(
                Geography.objects.filter(level__name='Pourashava/City Corporation').values_list('name',
                                                                                                flat=True))

            file_name = cls.get_export_file_name()

            for _city in [''] + available_cities:
                try:
                    path = os.path.join(EXPORT_FILE_ROOT)
                    if not os.path.exists(path):
                        os.makedirs(path)

                    gen_file_name = '_'.join([file_name, bw_compress_name(_city), str(start_year)]) \
                        if _city != '' else '_'.join([file_name, str(start_year)])

                    file_path = path + os.sep + gen_file_name + '.csv'

                    if os.path.exists(file_path):
                        os.remove(file_path)

                    csv_file = open(file_path, 'w', encoding='utf-8')

                    _updated_grant_queryset = cls.objects.filter(
                        survey_response__last_updated__gte=start_time, survey_response__last_updated__lte=end_time)

                    _created_grant_queryset = cls.objects.filter(
                        date_created__gte=start_time,
                        date_created__lte=end_time
                    )

                    _shortlisted_eligible_grantee_queryset = _updated_grant_queryset | _created_grant_queryset

                    if _city != '':
                        _shortlisted_eligible_grantee_queryset = _shortlisted_eligible_grantee_queryset.filter(
                            assigned_city=_city)

                    report_data = cls.get_report_data(queryset=_shortlisted_eligible_grantee_queryset)

                    for _row in report_data:
                        row_as_str = ','.join(['"{}"'.format(_val) for _val in _row]) + '\n'
                        csv_file.write(row_as_str)

                    csv_file.close()

                    # Uploading the exported file to AMAZON S3
                    if S3_STATIC_ENABLED:
                        from config.aws_s3_config import STATIC_EXPORT_MEDIA_DIRECTORY
                        try:
                            with open(file_path, 'rb') as content_file:
                                content = content_file.read()
                                s3_file_name = STATIC_EXPORT_MEDIA_DIRECTORY + "/" + str(gen_file_name) + '.csv'
                                file_path = s3_file_name.replace(MEDIA_DIRECTORY, '', 1)
                                AWSFileWriter.upload_file_with_content(file_name=s3_file_name, content=content)

                            # after successfully upload to AWS S3, remove local file
                            os.remove(file_path)
                        except Exception as exp:
                            ErrorLog.log(exp=exp)

                    export_file_object = ExportFileObject.objects.filter(
                        path=file_path, name=gen_file_name, file=file_path,
                        organization=Organization.get_organization_from_cache()
                    ).last()

                    if not export_file_object:
                        export_file_object = ExportFileObject()
                        export_file_object.path = file_path
                        export_file_object.name = gen_file_name
                        export_file_object.file = file_path
                        export_file_object.extension = '.csv'
                        export_file_object.organization = Organization.get_organization_from_cache()
                        export_file_object.save()

                except Exception as exp:
                    ErrorLog.log(exp)

            start_year += 1

    @classmethod
    def build_report(cls, columns=None, max_id=0, id_limit=0, batch_size=BATCH_SIZE, year=None, month=None,
                     city_id=None):
        from undp_nuprp.survey.models import QuestionResponse

        report = list()
        headers = list()

        organization = Organization.get_organization_from_cache()
        if columns is None:
            columns = cls.exporter_config(organization=organization).columns.all().order_by('date_created')

        for column in columns:
            headers.append(column.column_name)

        report.append(headers)

        initial_queryset = cls.objects.all()
        if city_id:
            initial_queryset = initial_queryset.filter(address__geography__parent_id=city_id)
        if year:
            if month:
                start_time = datetime.now().replace(year=year, month=month, day=1, hour=0, minute=0,
                                                    second=0).timestamp() * 1000
                if month == 12:
                    month = 0
                    year += 1
                end_time = datetime.now().replace(year=year, month=month + 1, day=1, hour=0, minute=0,
                                                  second=0).timestamp() * 1000 - 1000
            else:
                start_time = datetime.now().replace(year=year, month=1, day=1, hour=0, minute=0,
                                                    second=0).timestamp() * 1000
                end_time = datetime.now().replace(year=year + 1, month=1, day=1, hour=0, minute=0,
                                                  second=0).timestamp() * 1000 - 1000
            initial_queryset = initial_queryset.filter(date_created__gte=start_time, date_created__lte=end_time)

        eligible_grantee_queryset = initial_queryset.order_by('pk').filter(
            pk__gt=max_id, pk__lte=id_limit
        )[:batch_size]

        handled = 0
        for _object in eligible_grantee_queryset:
            max_id = _object.pk
            row = list()

            answers = QuestionResponse.objects.filter(
                section_response__survey_response_id=_object.survey_response_id).values(
                'answer_text', 'question__question_code')

            response_dict = dict()
            for answer in answers:
                if answer['question__question_code'] in response_dict.keys():
                    response_dict[answer['question__question_code']].append(answer['answer_text'])
                else:
                    response_dict[answer['question__question_code']] = [answer['answer_text']]

            for column in columns:
                _value = ''
                prop_name = column.property_name
                if hasattr(_object, prop_name):
                    _value = str(getattr(_object, prop_name))
                elif prop_name.startswith('render_q_code_') and prop_name.endswith('_response'):
                    _value = cls.get_question_response(
                        question_code=prop_name[14:-9].replace('_', '.'), response_dict=response_dict)
                elif prop_name.startswith('render_resource_') and prop_name.endswith('_response'):
                    _value = cls.get_resource_response(
                        resource_name=column.column_name, response_dict=response_dict)
                row.append(_value)
            report.append(row)
            handled += 1
        return handled, max_id, report
