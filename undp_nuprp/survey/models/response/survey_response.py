import uuid
from collections import OrderedDict
from datetime import datetime

from django.db import models, transaction
from django.db.models.aggregates import Count
from django.utils.safestring import mark_safe

from blackwidow.core.models import PhoneNumber, ImageFileObject
from blackwidow.core.models.clients.client_meta import ClientMeta
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.common.location import Location
from blackwidow.core.models.config.exporter_column_config import ExporterColumnConfig
from blackwidow.core.models.config.exporter_config import ExporterConfig
from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.constants.cache_constants import MODEL_CACHE_PREFIX, ONE_WEEK_TIMEOUT
from blackwidow.engine.decorators.enable_export import enable_export
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, has_status_data, enable_versioning, \
    save_audit_log
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.pg_survey_update_enum import PGSurveyUpdateEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.extensions.date_age_converter import calculate_age
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from blackwidow.scheduler.celery import app as celery_app
from undp_nuprp.nuprp_admin.models.infrastructure_units.household import Household
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
from undp_nuprp.nuprp_admin.models.users.enumerator import Enumerator
from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.reports.config.constants.pg_survey_constants import GENDER_QUESTION_CODE, AGE_QUESTION_CODE, \
    HH_QUESTION_CODE, PHONE_QUESTION, PG_MEMBER_SURVEY_NAME, NID_QUESTION, NAME_QUESTION_CODE, \
    NID_AVAILABILITY_QUESTION, \
    NID_ANSWER_CODE, NID_AVAILABILITY_QUESTION_TEXT, NID_QUESTION_TEXT
from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question
from undp_nuprp.survey.models.entity.survey import Survey
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.section_response import SectionResponse

__author__ = 'Tareq'

HH_QUESTIONS = {
    '1.1': '4.2.1', '1.3': '4.2.2', '1.4': '4.2.4', '1.5': '4.2.3', '2.2': '4.2.5', '2.3': '4.2.6',
    '2.4': '4.2.7', '2.6': '4.2.8', '2.11': '4.2.9', '3.1': '4.3.1', '3.2': '4.3.2', '3.3': '4.3.3',
    '3.4': '4.3.4', '3.5': '4.3.5', '3.6': '4.3.6'
}


@decorate(save_audit_log, expose_api('survey-response'), is_object_context, enable_versioning(),
          enable_export, enable_import, has_status_data,
          route(route='survey-response', group='Member Registration', module=ModuleEnum.Administration, group_order=1,
                display_name='Registration Responses', item_order=2))
class SurveyResponse(OrganizationDomainEntity):
    survey = models.ForeignKey('survey.Survey', null=True, on_delete=models.SET_NULL)
    survey_time = models.BigIntegerField(default=0)
    respondent_client = models.ForeignKey('core.Client', null=True, on_delete=models.SET_NULL)
    respondent_unit = models.ForeignKey('core.InfrastructureUnit', null=True, on_delete=models.SET_NULL)
    photos = models.ManyToManyField('core.ImageFileObject')
    location = models.ForeignKey('core.Location', null=True)
    address = models.ForeignKey('core.ContactAddress', null=True)
    imei_number = models.CharField(max_length=55, null=True, blank=True)

    class Meta:
        app_label = 'survey'

    def soft_delete(self, *args, force_delete=False, user=None, skip_log=False, **kwargs):
        # Delete survey response for soft deleting client
        from undp_nuprp.survey.models.response.section_response import SectionResponse
        from undp_nuprp.survey.models.response.question_response import QuestionResponse
        question_responses = QuestionResponse.objects.filter(section_response__survey_response_id=self.pk)
        section_responses = SectionResponse.objects.filter(survey_response_id=self.pk)

        # Handle PG member delete
        if not kwargs.get('client_deleted', False):
            if self.respondent_client is not None:
                self.respondent_client.soft_delete(*args, force_delete=force_delete, user=user, skip_log=skip_log,
                                                   **kwargs)

        for sr in section_responses:
            sr.soft_delete(*args, force_delete=force_delete, user=user, skip_log=skip_log, **kwargs)
        for qr in question_responses:
            qr.soft_delete(*args, force_delete=force_delete, user=user, skip_log=skip_log, **kwargs)
        return super(SurveyResponse, self).soft_delete(
            *args, force_delete=force_delete, user=user, skip_log=skip_log, **kwargs)

    @classmethod
    def version_enabled_related_fields(cls):
        return ['sectionresponse']

    @classmethod
    def get_cache_prefix(cls):
        """
        This method helps to store total survey by name in cache
        :return: String cache prefix
        """
        return MODEL_CACHE_PREFIX + cls.__name__ + '_'

    def delete_pg_score_of_updated_response(self):
        from undp_nuprp.survey.models.indicators.poverty_index_short_listed_grantee import \
            PGPovertyIndexShortListedGrantee
        PGPovertyIndexShortListedGrantee.objects.filter(survey_response_id=self.id).delete()

    def update_response_cache_count(self):
        cache_key = self.get_cache_prefix() + str(self.created_by_id)
        response_cache = CacheManager.get_from_cache_by_key(key=cache_key)
        if response_cache is None:
            response_cache = dict()
            survey_response_queryset = SurveyResponse.objects.filter(
                created_by_id=self.created_by_id).values('survey_id', 'survey__name').annotate(count=Count('pk'))

            for _sr in survey_response_queryset:
                response_cache[_sr['survey_id']] = {
                    'survey_name': _sr['survey__name'],
                    'count': _sr['count']
                }
        elif self.survey_id not in response_cache.keys():
            response_cache[self.survey_id] = {
                'survey_name': self.survey.name,
                'count':
                    SurveyResponse.objects.filter(survey_id=self.survey_id, created_by_id=self.created_by_id).aggregate(
                        count=Count('pk'))['count']
            }
        else:
            response_cache[self.survey_id]['count'] += 1
        CacheManager.set_cache_element_by_key(key=cache_key, value=response_cache, timeout=ONE_WEEK_TIMEOUT)

    def save(self, *args, organization=None, **kwargs):
        result = super(SurveyResponse, self).save(*args, organization=organization, **kwargs)
        return result

    @classmethod
    def get_status_data(cls, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return: Key value pair for status API response
        """
        cache_key = cls.get_cache_prefix() + str(request.c_user.pk)
        response_cache = CacheManager.get_from_cache_by_key(key=cache_key)
        if response_cache is None:
            survey_response_queryset = cls.objects.filter(
                created_by_id=request.c_user.pk).values('survey_id', 'survey__name').annotate(count=Count('pk'))
            response_cache = dict()
            for _sr in survey_response_queryset:
                response_cache[_sr['survey_id']] = {
                    'survey_name': _sr['survey__name'],
                    'count': _sr['count']
                }
            CacheManager.set_cache_element_by_key(key=cache_key, value=response_cache, timeout=ONE_WEEK_TIMEOUT)

        return {
            'completed_survey': list(response_cache.values())
        }

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Edit]

    @property
    def render_detail_title(self):
        return mark_safe(str(self.display_name()))

    @property
    def render_household(self):
        return self.respondent_unit

    @property
    def render_household_id(self):
        return self.respondent_unit.assigned_code

    @property
    def render_household_address(self):
        return self.address

    @property
    def render_survey_time(self):
        return self.render_timestamp(self.survey_time)

    @property
    def render_PG_member(self):
        if self.respondent_client:
            return self.respondent_client
        else:
            return 'N/A'

    @property
    def render_city(self):
        if self.respondent_client:
            return self.respondent_client.assigned_to.parent.address.geography.parent.name
        else:
            return 'N/A'

    @classmethod
    def search_city(cls, queryset, value):
        return queryset.filter(
            respondent_client__assigned_to__parent__address__geography__parent__name__icontains=value)

    @classmethod
    def order_by_city(cls):
        return ['respondent_client__assigned_to__parent__address__geography__parent__name']

    @classmethod
    def order_by_survey_time(cls):
        return ['survey_time']

    @property
    def render_IMEI_number(self):
        return self.imei_number if self.imei_number else "N/A"

    @classmethod
    def table_columns(cls):
        return (
            'render_code', 'survey', 'imei_number:IMEI Number', 'render_PG_member', 'created_by:Enumerator',
            'render_city', 'render_survey_time', 'last_updated', 'location')

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Edit',
                action='edit',
                icon='fbx-rightnav-edit',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit)
            )
        ]

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return 'Export Excel / SPSS'
        if button == ViewActionEnum.AdvancedImport:
            return 'Import Excel'

    @property
    def details_config(self):
        address = self.address
        if address is None:
            client = self.respondent_client
            if client and client.assigned_to and client.assigned_to.parent:
                address = client.assigned_to.parent.address
        details = OrderedDict()
        details['detail_title'] = self.render_detail_title
        if self.respondent_unit:
            details['household'] = self.respondent_unit
            details['household_ID'] = self.respondent_unit.assigned_code
        elif self.respondent_client:
            details['primary_group_member'] = self.respondent_client
            details['primary_group_member_ID'] = self.respondent_client.assigned_code
        details['enumerator'] = self.created_by
        details['address'] = address
        details['survey_time'] = self.render_timestamp(self.survey_time)
        details['sync_time'] = self.render_timestamp(self.date_created)
        details['location'] = self.location
        details['IMEI Number'] = self.imei_number if self.imei_number else "N/A"
        return details

    @property
    def tabs_config(self):
        return [
            TabView(
                title='Photos(s)',
                access_key='photos',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.NORMAL,
                property=self.photos,
                related_model=ImageFileObject,
                queryset=self.photos.all(),
            ),
        ]

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)

        columns = list()
        column = 0
        for level in ['Location', 'Date', 'Latitude', 'Alt', 'Longitude', 'Survey_id', 'Trip_id', 'Speed', 'Username',
                      'Division', 'City Corporation', 'Ward', 'Mahalla_no', 'Settlement_no', 'Mahalla',
                      'Poor Settlement', 'Household ID']:
            columns.append(ImporterColumnConfig(
                column=column, column_name=level, property_name=level.lower().replace(' ', '_'), ignore=False))
            column += 1

        for question in Question.objects.all().order_by('order'):  # TODO Future, filter by survey
            columns.append(ImporterColumnConfig(
                column=column, column_name=question.question_code, property_name=question.question_code, ignore=False))
            column += 1
        for level in ['Enumerator Name', 'Enumerator Mobile No', 'Comment']:
            columns.append(ImporterColumnConfig(
                column=column, column_name=level, property_name=level.lower().replace(' ', '_'), ignore=False))
            column += 1

        for c in columns:
            c.save(organization=organization, **kwargs)
            importer_config.columns.add(c)
        return importer_config

    @classmethod
    def import_item(cls, config, sorted_columns, data, user=None, **kwargs):
        return data

    @classmethod
    def post_processing_import_completed(cls, items=[], user=None, organization=None, **kwargs):
        question_answers = Answer.objects.values('id', 'text', 'answer_type', 'question_id', 'question__text',
                                                 'question__question_type').order_by('order')
        question_dict = dict()
        for qa in question_answers:
            if qa['question_id'] not in question_dict.keys():
                question_dict[qa['question_id']] = {
                    'question_text': qa['question__text'],
                    'question_type': qa['question__question_type'],
                    'answers': list()
                }
            question_dict[qa['question_id']]['answers'].append({
                'answer_id': qa['id'],
                'answer_text': qa['text'],
                'answer_type': qa['answer_type']
            })
        questions = Question.objects.values('id', 'section_id').order_by('order')
        survey = Survey.objects.first()  # TODO in future filter this for multiple survey
        respondent_question = questions[0]
        organization = Organization.objects.first()
        background_enumerator = Enumerator.objects.filter(name='Background Enumerator').first()

        for item in items:
            try:
                date = item['1']
                latitude = item['2']
                longitude = item['4']
                division_name = item['9']
                city_name = item['10']
                ward_name = str(int(item['11']))
                mahalla_name = item['14']
                settlement_name = item['15']
                household_id = str(int(item['16']))

                column_id = 17
                answers = dict()
                for question in questions:
                    _ans = item[str(column_id)]
                    column_id += 1
                    answers[question['id']] = _ans

                survey_time = date
                if date:
                    try:
                        survey_time = datetime.strptime(date, '%m/%d/%Y %H:%M')
                    except:
                        try:
                            survey_time = datetime.strptime(date, '%m/%d/%Y')
                        except:
                            pass
                survey_time = survey_time.timestamp() * 1000
                survey_location = None
                survey_address = None
                if latitude and longitude:
                    survey_location = Location.objects.create(latitude=latitude, longitude=longitude)

                settlement = Geography.objects.filter(
                    level__name='Poor Settlement', name__iexact=settlement_name, parent__name__iexact=mahalla_name,
                    parent__parent__name__iexact=ward_name
                ).first()
                if settlement:
                    survey_address = ContactAddress.objects.create(geography_id=settlement.pk,
                                                                   location_id=survey_location.pk)
                else:
                    continue
                household = Household.objects.create(address=survey_address, assigned_code=household_id,
                                                     name=answers[respondent_question['id']],
                                                     organization_id=organization.pk)

                with transaction.atomic():
                    survey_response = SurveyResponse.objects.create(
                        survey_id=survey.pk, respondent_unit_id=household.pk, location_id=survey_location.pk,
                        address_id=survey_address.pk, survey_time=survey_time, organization_id=organization.pk,
                        created_by=background_enumerator
                    )

                    section_responses = dict()
                    for question in questions:
                        candidate_answer = answers[question['id']]
                        if not candidate_answer or candidate_answer == '98':
                            continue
                        if question['section_id'] not in section_responses:
                            section_responses[question['section_id']] = SectionResponse.objects.create(
                                survey_response_id=survey_response.pk, section_id=question['section_id'],
                                organization_id=organization.pk)
                        question_obj = question_dict[question['id']]

                        question_id = question['id']
                        question_text = question_obj['question_text']

                        candidate_answer = answers[question['id']]
                        if candidate_answer and question_obj[
                            'question_type'] == QuestionTypeEnum.MultipleSelectInput.value:
                            candidate_answers = candidate_answer.split(',')
                        else:
                            candidate_answers = [candidate_answer]

                        for candidate_answer in candidate_answers:
                            answer_id = None
                            answer_text = ''
                            for answer_obj in question_obj['answers']:
                                if answer_obj['answer_type'] == AnswerTypeEnum.TextInput.value or answer_obj[
                                    'answer_type'] == AnswerTypeEnum.NumberInput.value or answer_obj[
                                    'answer_type'] == AnswerTypeEnum.PhoneNumberInput.value or answer_obj[
                                    'answer_type'] == AnswerTypeEnum.EmailAddressInput.value or answer_obj[
                                    'answer_type'] == AnswerTypeEnum.OtherOption.value:
                                    answer_id = answer_obj['answer_id']
                                    answer_text = candidate_answer
                                elif answer_obj['answer_text'].lower().strip() == candidate_answer.lower().strip():
                                    answer_id = answer_obj['answer_id']
                                    answer_text = answer_obj['answer_text']
                            if answer_id:
                                question_response = QuestionResponse.objects.create(
                                    section_response_id=section_responses[question['section_id']].pk,
                                    question_id=question_id,
                                    answer_id=answer_id,
                                    question_text=question_text,
                                    answer_text=answer_text,
                                    organization_id=organization.pk
                                )
            except Exception as exp:
                ErrorLog.log(exp=exp)

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)

        all_questions = Question.objects.using(BWDatabaseRouter.get_export_database_name()).order_by(
            'order')  # filter by survey should be added if system has multiple survey

        columns = [
            ExporterColumnConfig(column=0, column_name='Division', property_name='division', ignore=False),
            ExporterColumnConfig(column=1, column_name='Pourashava/City Corporation', property_name='city',
                                 ignore=False),
            ExporterColumnConfig(column=2, column_name='Ward Number', property_name='ward', ignore=False),
            ExporterColumnConfig(column=3, column_name='Mahalla number', property_name='mahalla', ignore=False),
            ExporterColumnConfig(column=4, column_name='Poor Settlement number', property_name='poor_settlement',
                                 ignore=False),
            ExporterColumnConfig(column=5, column_name='Household ID Number', property_name='household', ignore=False),
        ]
        column_index = len(columns)

        for question in all_questions:
            columns.append(ExporterColumnConfig(column=column_index, column_name=question.question_code,
                                                property_name=question.question_code, ignore=False))
            column_index += 1

        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)

        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        # workbook.protection.sheet = True
        return self.pk, row_number + 1

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, query_set=None, **kwargs):
        row = 1
        workbook.merge_cells(start_row=1, start_column=1, end_row=1, end_column=6)
        workbook.cell(row=row, column=1).value = 'Household Survey Resonses'
        row += 1

        all_questions = Question.objects.using(BWDatabaseRouter.get_export_database_name()).order_by(
            'order')  # filter by survey should be added if system has multiple survey

        workbook.cell(row=row, column=1).value = "Division"
        workbook.cell(row=row, column=2).value = "Pourashava/City Corporation"
        workbook.cell(row=row, column=3).value = "Ward Number"
        workbook.cell(row=row, column=4).value = "Mahalla number"
        workbook.cell(row=row, column=5).value = "Poor Settlement number"
        workbook.cell(row=row, column=6).value = "Household ID Number"

        column = 7
        for question in all_questions:
            workbook.cell(row=row, column=column).value = question.question_code
            column += 1
        row += 1

        all_responses = SurveyResponse.objects.using(BWDatabaseRouter.get_export_database_name()).all()  # filter by survey should be added if system has multiple survey
        question_responses = QuestionResponse.objects.using(BWDatabaseRouter.get_export_database_name()).all()
        question_response_dict = dict()
        for question_response in question_responses:
            survey_response = question_response.section_response.survey_response_id
            if survey_response not in question_response_dict.keys():
                question_response_dict[survey_response] = dict()
            question_id = question_response.question_id
            if question_id not in question_response_dict[survey_response].keys():
                question_response_dict[survey_response][question_id] = list()
            question_response_dict[survey_response][question_id].append(question_response)
        for response in all_responses:
            try:
                respondent = response.respondent_client
                household = respondent.assigned_to if respondent else None
                workbook.cell(row=row, column=6).value = household.assigned_code if household else ''
                poor_settlement = household.address.geography
                workbook.cell(row=row, column=5).value = poor_settlement.name if poor_settlement else ''
                mahalla = poor_settlement.parent
                workbook.cell(row=row, column=4).value = mahalla.name if mahalla else ''
                ward = mahalla.parent
                workbook.cell(row=row, column=3).value = ward.name if ward else ''
                city = ward.parent
                workbook.cell(row=row, column=2).value = city.name if city else ''
                division = city.parent
                workbook.cell(row=row, column=1).value = division.name if division else ''
            except:
                pass

            column = 7
            for question in all_questions:
                if response.pk in question_response_dict.keys() and \
                        question.pk in question_response_dict[response.pk].keys():
                    _val = '\n'.join([question_response.answer_text for question_response in
                                      question_response_dict[response.pk][question.pk]])
                else:
                    _val = ''
                workbook.cell(row=row, column=column).value = _val
                column += 1
            row += 1
        return workbook, row

    @classmethod
    def finalize_export(cls, workbook=None, row_count=None, **kwargs):
        file_name = '%s_%s' % (cls.__name__, Clock.timestamp())
        return workbook, file_name

    @classmethod
    def finalize_survey_response(cls, survey_id=None, instance=None, serializer=None):
        survey_obj = Survey.objects.get(id=survey_id)

        if survey_obj.name == 'Household Survey Questionnaire':
            household = None
            if hasattr(serializer, 'address'):
                household_address = ContactAddress(geography_id=serializer.address['poor_settlement'])
                household_address.save()
                household = Household(address=household_address, assigned_code=serializer.address['household'])
                household.save()
                instance.address = household_address
                instance.respondent_unit = household
                instance.save()
            respondent_question = Question.objects.filter(section__survey_id=instance.survey_id).order_by(
                'order').first()
            respondent_response = QuestionResponse.objects.filter(
                question_id=respondent_question.pk, section_response__survey_response_id=instance.pk).first()
            if respondent_response is not None:
                household.name = respondent_response.answer_text
                household.save()

        elif survey_obj.name == 'PG Member Survey Questionnaire':
            pg_member = None
            if hasattr(serializer, 'address'):
                pg_id = serializer.address['poor_settlement']
                pg_member = PrimaryGroupMember(assigned_to_id=pg_id, assigned_code=serializer.address['household'])
                client_meta = ClientMeta.objects.create(organization=Organization.get_organization_from_cache())
                phone_number = PhoneNumber()
                gender_question = QuestionResponse.objects.filter(question__question_code=GENDER_QUESTION_CODE,
                                                                  section_response__survey_response_id=instance.pk).first()
                age_question = QuestionResponse.objects.filter(question__question_code=AGE_QUESTION_CODE,
                                                               section_response__survey_response_id=instance.pk).first()
                hh_question = QuestionResponse.objects.filter(question__question_code=HH_QUESTION_CODE,
                                                              answer_text='Yes',
                                                              section_response__survey_response_id=instance.pk).first()
                phone_question = QuestionResponse.objects.filter(question__question_code=PHONE_QUESTION,
                                                                 section_response__survey_response_id=instance.pk).first()
                nid_question = QuestionResponse.objects.filter(question__question_code=NID_QUESTION,
                                                               section_response__survey_response_id=instance.pk).first()

                if nid_question:
                    client_meta.national_id = nid_question.answer_text
                else:
                    client_meta.national_id = 'N/A'
                client_meta.save()

                if phone_question:
                    phone_number.phone = phone_question.answer_text
                else:
                    phone_number.phone = 'N/A'
                phone_number.save()

                if hh_question:
                    hh_question_responses = QuestionResponse.objects.filter(
                        question__question_code__in=list(HH_QUESTIONS.keys()),
                        section_response__survey_response_id=instance.pk)
                    for hh_question_response in hh_question_responses:
                        hh_question_code = HH_QUESTIONS[hh_question_response.question.question_code]
                        hh_original_question = Question.objects.filter(section__survey__name=PG_MEMBER_SURVEY_NAME,
                                                                       question_code=hh_question_code).first()
                        hh_question_id = hh_original_question.pk
                        if hh_question_code == '4.2.3':
                            try:
                                birth_date = datetime.strptime(hh_question_response.answer_text, "%d-%b-%Y")
                            except:
                                birth_date = datetime(year=int(hh_question_response.answer_text.split('-')[-1]),
                                                      month=1, day=1)
                            hh_age = calculate_age(birth_date)
                            copied_hh_response = QuestionResponse(
                                organization_id=hh_question.organization_id,
                                question_id=hh_question_id,
                                question_text=hh_original_question.text,
                                answer_id=hh_question_response.answer_id,
                                answer_text=hh_age,
                                section_response_id=hh_question.section_response_id)
                        else:
                            copied_hh_response = QuestionResponse(
                                organization_id=hh_question.organization_id,
                                question_id=hh_question_id,
                                question_text=hh_original_question.text,
                                answer_id=hh_question_response.answer_id,
                                answer_text=hh_question_response.answer_text,
                                section_response_id=hh_question.section_response_id)
                        copied_hh_response.save()

                if age_question:
                    try:
                        try:
                            birth_date = datetime.strptime(age_question.answer_text, "%d-%b-%Y")
                        except:
                            birth_date = datetime(year=int(age_question.answer_text.split('-')[-1]), month=1, day=1)
                        client_meta.age = calculate_age(birth_date)
                    except:
                        client_meta.age = 0
                    client_meta.save()

                if gender_question:
                    if gender_question.answer_text.lower() == 'male':
                        client_meta.gender = 'M'
                    elif gender_question.answer_text.lower() == 'female':
                        client_meta.gender = 'F'
                    elif gender_question.answer_text.lower() == 'hijra':
                        client_meta.gender = 'H'
                    client_meta.save()

                disabled_questions_count = QuestionResponse.objects.filter(
                    section_response__survey_response_id=instance.pk,
                    question__question_code__in=['3.1', '3.2', '3.3', '3.4', '3.5', '3.6'],
                    answer_text__in=['Cannot do at all', 'A lot of difficulty']
                ).count()
                if disabled_questions_count > 0:
                    client_meta.is_disabled = True
                    client_meta.save()
                pg_member.client_meta = client_meta
                pg_member.phone_number = phone_number
                pg_member.save()
                instance.respondent_client = pg_member
                instance.save()
            respondent_question = Question.objects.filter(section__survey_id=instance.survey_id).order_by(
                'order').first()
            respondent_response = QuestionResponse.objects.filter(
                question_id=respondent_question.pk, section_response__survey_response_id=instance.pk).first()
            if respondent_response is not None:
                pg_member.name = respondent_response.answer_text
                pg_member.save()
                if hasattr(serializer, 'address'):
                    pg_id = serializer.address['poor_settlement']
                    scg = SavingsAndCreditGroup.objects.filter(primary_group_id=pg_id).first()
                    if scg:
                        scg.members.add(pg_member)

    @classmethod
    def get_model_api_queryset(cls, queryset=None, **kwargs):
        queryset = queryset.filter(shortlistedeligiblegrantee__isnull=False)
        queryset = queryset.order_by('id').distinct('id')
        return queryset

    @classmethod
    def get_serializer(cls):
        from undp_nuprp.survey.serializers.survey_response_serializer import SurveyResponseSerializer
        return SurveyResponseSerializer

    @celery_app.task
    def perform_pg_survey_update(self, sr_id, qr_dict_list, update_log):
        print('calling - perform_pg_survey_update')
        try:
            # a dict where key is question_code and value is question id
            _question_code_id_map = {}

            # a dict which contains a dictionary tsync_id as a key and QR(question response as a value
            question_response_dict = {}

            disabled_questions_count = 0
            pg_member_name = None
            _nid_answer = False
            phone_number = PhoneNumber()
            creatable_question_list = list()
            modified_question_list = list()

            with transaction.atomic():
                instance = self.__class__.objects.filter(id=sr_id).last()
                instance.handle_version_creation()
                pg_member = instance.respondent_client
                client_meta = pg_member.client_meta

                current_timestamp = datetime.now().timestamp() * 1000
                organization = Organization.get_organization_from_cache()
                if qr_dict_list:
                    question_ids = [q['question'] for q in qr_dict_list]
                    question_section_tuple = Question.objects.filter(
                        section__survey_id=instance.survey_id, pk__in=question_ids). \
                        values('pk', 'section_id', 'question_code')

                    question_to_section_dict = dict()  # Get section by question_id as key
                    section_response_dict = dict()  # Get section response by section_id as key

                    for _question in Question.objects.filter(section__survey_id=instance.survey_id):
                        _question_code_id_map[_question.question_code] = _question.id

                    _existing_srs = SectionResponse.objects.filter(survey_response_id=sr_id)
                    for _existing_sr in _existing_srs:
                        section_response_dict[_existing_sr.section_id] = _existing_sr

                    for section in question_section_tuple:
                        question_to_section_dict[section['pk']] = section['section_id']
                        if section['section_id'] not in section_response_dict.keys():
                            section_response = SectionResponse.objects.create(
                                survey_response_id=sr_id, section_id=section['section_id'])
                            section_response_dict[section['section_id']] = section_response

                    _disable_question_ids = [_question_code_id_map['3.1'], _question_code_id_map['3.2'],
                                             _question_code_id_map['3.3'], _question_code_id_map['3.4'],
                                             _question_code_id_map['3.5'], _question_code_id_map['3.6']]

                    question_response_queryset = QuestionResponse.objects.filter(
                        section_response__survey_response_id=sr_id)

                    for qr in question_response_queryset:
                        question_response_dict[qr.tsync_id] = qr

                    for question in qr_dict_list:
                        candidate_section_response = section_response_dict[
                            question_to_section_dict[question['question']]]

                        _answer_text = question['answer_text'].strip()

                        if question['question'] == _question_code_id_map['1.1']:
                            pg_member_name = _answer_text

                        if question['question'] == _question_code_id_map['4.2.3']:
                            try:
                                birth_date = datetime.strptime(_answer_text, "%d-%b-%Y")
                            except:
                                birth_date = datetime(year=int(_answer_text.split('-')[-1]), month=1, day=1)
                            _answer_text = calculate_age(birth_date)

                        if question['question'] == _question_code_id_map[GENDER_QUESTION_CODE]:
                            if _answer_text.lower() == 'male':
                                client_meta.gender = 'M'
                            elif _answer_text.lower() == 'female':
                                client_meta.gender = 'F'
                            elif _answer_text.lower() == 'hijra':
                                client_meta.gender = 'H'

                        if question['question'] == _question_code_id_map[AGE_QUESTION_CODE]:
                            try:
                                try:
                                    birth_date = datetime.strptime(_answer_text, "%d-%b-%Y")
                                except:
                                    birth_date = datetime(year=int(_answer_text.split('-')[-1]),
                                                          month=1, day=1)
                                client_meta.age = calculate_age(birth_date)
                            except:
                                client_meta.age = 0

                        if question['question'] == _question_code_id_map[PHONE_QUESTION]:
                            phone_number.phone = _answer_text
                            phone_number.save()

                        if question['question'] == _question_code_id_map[NID_QUESTION]:
                            client_meta.national_id = _answer_text
                            _nid_answer = True

                        if question['question'] in _disable_question_ids:
                            if _answer_text in ['Cannot do at all', 'A lot of difficulty']:
                                disabled_questions_count += 1

                        qr_obj = question_response_dict.get(question['tsync_id']) if 'tsync_id' in question else None
                        if not qr_obj:
                            question_response = QuestionResponse(
                                tsync_id=question['tsync_id'] if 'tsync_id' in question and question[
                                    'tsync_id'] else uuid.uuid4(),
                                organization_id=organization.pk,
                                index=question['index'],
                                question_id=question['question'],
                                answer_id=question['answer'],
                                question_text=question['question_text'],
                                answer_text=_answer_text,
                                section_response_id=candidate_section_response.pk,
                                created_by_id=candidate_section_response.created_by_id,
                                last_updated_by_id=candidate_section_response.last_updated_by_id,
                                date_created=current_timestamp, last_updated=current_timestamp
                            )
                            creatable_question_list.append(question_response)
                        else:
                            qr_obj.answer_id = question['answer']
                            qr_obj.answer_text = _answer_text
                            qr_obj.created_by_id = candidate_section_response.created_by_id
                            qr_obj.last_updated_by_id = candidate_section_response.last_updated_by_id
                            qr_obj.last_updated = current_timestamp
                            modified_question_list.append(qr_obj)
                            del question_response_dict[qr_obj.tsync_id]

                        current_timestamp += 1

                    if len(creatable_question_list) > 0:
                        QuestionResponse.objects.bulk_create(creatable_question_list)

                    if len(modified_question_list) > 0:
                        QuestionResponse.objects.bulk_update(modified_question_list)

                # For PG member update it's client meta information
                if pg_member:
                    if disabled_questions_count > 0:
                        client_meta.is_disabled = True
                    else:
                        client_meta.is_disabled = False

                    if phone_number.phone is None or phone_number.phone == '':
                        phone_number.phone = 'N/A'
                        phone_number.save()

                    if not _nid_answer:
                        client_meta.national_id = 'N/A'

                    if pg_member_name:
                        pg_member.name = pg_member_name

                    client_meta.save()
                    pg_member.client_meta = client_meta
                    pg_member.phone_number = phone_number
                    pg_member.save()
                    instance.respondent_client = pg_member
                    instance.save()

            deletable_qr_ids = [qr.id for qr in question_response_dict.values()]

            if deletable_qr_ids:
                QuestionResponse.update_master_version(deletable_qr_ids=deletable_qr_ids)

            # Update MPI Indicators
            from undp_nuprp.survey.models.indicators.pg_mpi_indicator.mpi_indicator import PGMPIIndicator
            from undp_nuprp.approvals.managers.eligible_grantee_manager import EligibleGranteeManager

            mpi_indicator, indices = PGMPIIndicator.get_mpi_indicator_object_for_survey_response(
                response=self, organization_id=self.organization_id, poverty_indices=[])
            mpi_indicator.save()

            # Update Eligible Grantees
            EligibleGranteeManager.handle_eligible_grantee_selection_for_survey_response(
                survey_response=self, indvidually_edited=True)

            instance.delete_pg_score_of_updated_response()
            update_log.status = PGSurveyUpdateEnum.SUCCESS.value
            update_log.completion_time = int(datetime.now().timestamp() * 1000)

        except Exception as exp:
            update_log.status = PGSurveyUpdateEnum.ERROR.value
            update_log.message = exp
            ErrorLog.log(exp)
        print('execution completed - perform_pg_survey_update')
        update_log.save()

    def update_survey_response_version_for_pg_member_update(self, name, phone_number, national_id):
        from undp_nuprp.approvals.managers.eligible_grantee_manager import EligibleGranteeManager

        with transaction.atomic():
            self.handle_version_creation()

            if name:
                pgm_name_qr = QuestionResponse.objects.filter(
                    section_response__survey_response=self,
                    question__question_code=NAME_QUESTION_CODE
                ).first()

                if not pgm_name_qr:
                    name_question = Question.objects.filter(question_code=NAME_QUESTION_CODE).first()
                    section = name_question.section
                    section_response = SectionResponse.objects.filter(
                        survey_response=self,
                        section=section
                    ).first()

                    if not section_response:
                        section_response = SectionResponse(
                            organization=self.organization,
                            survey_response=self,
                            section=section
                        )
                        section_response.save()

                    # Create question response for pg member name
                    QuestionResponse.objects.create(
                        organization=self.organization,
                        section_response=section_response,
                        question=name_question,
                        answer=Answer.objects.filter(
                            question__question_code=NAME_QUESTION_CODE,
                        ).first(),
                        question_text=name_question.text,
                        answer_text=name
                    )
                else:
                    pgm_name_qr.answer_text = name
                    pgm_name_qr.save()

            if phone_number:
                pgm_phone_qr = QuestionResponse.objects.filter(
                    section_response__survey_response=self,
                    question__question_code=PHONE_QUESTION
                ).first()

                if not pgm_phone_qr:
                    phone_question = Question.objects.filter(question_code=PHONE_QUESTION).first()
                    section = phone_question.section
                    section_response = SectionResponse.objects.filter(
                        survey_response=self,
                        section=section
                    ).first()

                    if not section_response:
                        section_response = SectionResponse(
                            organization=self.organization,
                            survey_response=self,
                            section=section
                        )
                        section_response.save()

                    # Create question response for phone number
                    QuestionResponse.objects.create(
                        organization=self.organization,
                        section_response=section_response,
                        question=phone_question,
                        answer=Answer.objects.filter(
                            question__question_code=PHONE_QUESTION,
                        ).first(),
                        question_text=phone_question.text,
                        answer_text=phone_number
                    )
                else:
                    pgm_phone_qr.answer_text = phone_number
                    pgm_phone_qr.save()

            if national_id:
                pgm_nid_qr = QuestionResponse.objects.filter(
                    section_response__survey_response=self,
                    question__question_code=NID_QUESTION
                ).first()

                if not pgm_nid_qr:
                    # Update NID availability question response
                    pgm_nid_avail_qr = QuestionResponse.objects.filter(
                        section_response__survey_response=self,
                        question__question_code=NID_AVAILABILITY_QUESTION
                    ).first()
                    nid_answer = Answer.objects.filter(
                        question__question_code=NID_AVAILABILITY_QUESTION,
                        question__text=NID_AVAILABILITY_QUESTION_TEXT,
                        answer_code=NID_ANSWER_CODE
                    ).first()
                    pgm_nid_avail_qr.answer = nid_answer
                    pgm_nid_avail_qr.answer_text = nid_answer.text
                    pgm_nid_avail_qr.save()
                    nid_ques = Question.objects.filter(question_code=NID_QUESTION).first()

                    # Create question response for NID
                    QuestionResponse.objects.create(
                        organization=pgm_nid_avail_qr.organization,
                        section_response=pgm_nid_avail_qr.section_response,
                        question=nid_ques,
                        answer=Answer.objects.filter(
                            question__question_code=NID_QUESTION,
                            question__text=NID_QUESTION_TEXT
                        ).first(),
                        question_text=nid_ques.text,
                        answer_text=national_id
                    )
                else:
                    pgm_nid_qr.answer_text = national_id
                    pgm_nid_qr.save()

            current_timestamp = datetime.now().timestamp() * 1000
            QuestionResponse.objects.filter(section_response__survey_response=self).update(
                last_updated=current_timestamp)

            # Update Eligible Grantees
            EligibleGranteeManager.handle_eligible_grantee_selection_for_survey_response(
                survey_response=self, indvidually_edited=True)
