import json
import uuid
from datetime import datetime
from threading import Thread

from django.db import transaction
from rest_framework import serializers

from blackwidow.core.models import ImageFileObject
from blackwidow.core.models.clients.client_meta import ClientMeta
from blackwidow.core.models.common.location import Location
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.log.error_log import ErrorLog
from blackwidow.core.models.log.pg_survey_update_log import PGSurveyUpdateLog
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.constants.cache_constants import SITE_NAME_AS_KEY, ONE_HOUR_TIMEOUT
from blackwidow.engine.enums.pg_survey_update_enum import PGSurveyUpdateEnum
from blackwidow.engine.extensions.async_task import perform_async
from blackwidow.engine.extensions.date_age_converter import calculate_age
from blackwidow.engine.managers.cachemanager import CacheManager
from undp_nuprp.nuprp_admin.models import PrimaryGroup
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup
from undp_nuprp.reports.config.constants.pg_survey_constants import AGE_QUESTION_CODE, GENDER_QUESTION_CODE, \
    PHONE_QUESTION, NID_QUESTION
from undp_nuprp.survey.models.entity.question import Question
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.section_response import SectionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse
from undp_nuprp.survey.serializers.survey_response_list_serializer import SurveyResponseListSerializer
from blackwidow.core.models.common.membership_status import PrimaryGroupMemberStatus

class SurveyResponseSerializer(OrganizationDomainEntity.get_serializer()):
    location = Location.get_serializer()(required=True)
    address = serializers.SerializerMethodField(required=False)
    questions = serializers.SerializerMethodField()
    photos = ImageFileObject.get_serializer()(many=True, required=False)

    def get_questions(self, obj):
        try:
            if hasattr(self, 'questions'):
                questions = getattr(self, 'questions')
                return questions
            else:
                return []
        except Exception as e:
            ErrorLog.log(exp=e)

    def get_address(self, obj):
        pg_id = obj.respondent_client.assigned_to_id
        pg_member_assigned_code = obj.respondent_client.assigned_code
        return {
            'poor_settlement': pg_id,
            'household': pg_member_assigned_code
        }

    def __init__(self, *args, fields=None, context=None, **kwargs):
        if bool(context):
            if context['request'].data:
                _data = context['request'].data
                if 'survey' in _data:
                    self.survey = _data['survey']
                if 'questions' in _data:
                    self.questions = _data['questions']
                if 'address' in _data:
                    self.address = _data['address']
        super().__init__(fields=fields, context=context, *args, **kwargs)

    def create(self, attrs):
        _question_code_id_map = {}  # a dict where key is question_code and value is question id
        pg_member = pg_member_name = None
        disabled_questions_count = 0
        _nid_answer = False
        phone_number = PhoneNumber()

        with transaction.atomic():
            tsync_id = attrs.get('tsync_id', uuid.uuid4())
            survey_response_obj = self.Meta.model.objects.filter(tsync_id=tsync_id)
            if survey_response_obj.exists():
                return survey_response_obj.first()

            instance = super().create(attrs=attrs)

            # Create/Update PG member and client meta instance
            if hasattr(self, 'address'):
                pg_id = self.address['poor_settlement']
                pg_member = PrimaryGroupMember(assigned_to_id=pg_id,
                                               status=PrimaryGroupMemberStatus.Active.value,
                                               assigned_code=self.address['household'])
                client_meta = ClientMeta.objects.create(organization=Organization.get_organization_from_cache())

            current_timestamp = datetime.now().timestamp() * 1000
            organization = Organization.get_organization_from_cache()
            if hasattr(self, 'questions'):
                question_ids = [q['question'] for q in self.questions]
                question_section_tuple = Question.objects.filter(section__survey_id=self.survey, pk__in=question_ids). \
                    values('pk', 'section_id', 'question_code')

                for _question in Question.objects.filter(section__survey=self.survey):
                    _question_code_id_map[_question.question_code] = _question.id

                section_response_dict = dict()  # Get section response by sention_id as key
                question_to_section_dict = dict()  # Get section by question_id as key
                for section in question_section_tuple:
                    question_to_section_dict[section['pk']] = section['section_id']
                    if section['section_id'] not in section_response_dict.keys():
                        section_response = SectionResponse(survey_response_id=instance.pk,
                                                           section_id=section['section_id'])
                        section_response.save()
                        section_response_dict[section['section_id']] = section_response

                _disable_question_ids = [_question_code_id_map['3.1'], _question_code_id_map['3.2'],
                                         _question_code_id_map['3.3'], _question_code_id_map['3.4'],
                                         _question_code_id_map['3.5'], _question_code_id_map['3.6']]

                creatable_question_list = list()
                for question in self.questions:
                    candidate_section_response = section_response_dict[
                        question_to_section_dict[question['question']]]
                    question_response = QuestionResponse(
                        tsync_id=uuid.uuid4(),
                        organization_id=organization.pk,
                        section_response_id=candidate_section_response.pk,
                        question_id=question['question'],
                        answer_id=question['answer'],
                        question_text=question['question_text'],
                        answer_text=question['answer_text'].strip(),
                        created_by_id=candidate_section_response.created_by_id,
                        last_updated_by_id=candidate_section_response.last_updated_by_id,
                        date_created=current_timestamp, last_updated=current_timestamp
                    )

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

                    current_timestamp += 1
                    if 'index' in question.keys() and question['index']:
                        question_response.index = question['index']
                    creatable_question_list.append(question_response)
                if len(creatable_question_list) > 0:
                    QuestionResponse.objects.bulk_create(creatable_question_list)

            # For PG member update it's client meta information
            if pg_member:
                if disabled_questions_count > 0:
                    client_meta.is_disabled = True

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
                pg_group = PrimaryGroup.objects.filter(pk=pg_member.assigned_to_id).last()
                if pg_group:
                    pg_group.save()

                # update primary group member count cache
                cache_key = SITE_NAME_AS_KEY + '_pg_member_count_dict'
                cached_member_dict = CacheManager.get_from_cache_by_key(key=cache_key)
                if cached_member_dict:
                    self.member_dict = json.loads(cached_member_dict)
                    if pg_id in self.member_dict.keys():
                        self.member_dict[pg_id]['member_count'] += 1
                        self.member_dict[pg_id]['last_pg_member_no'] = max(
                            pg_member.last_2_digits_of_assigned_code,
                            self.member_dict[pg_id]['last_pg_member_no'])
                        CacheManager.set_cache_element_by_key(
                            key=cache_key,
                            value=json.dumps(self.member_dict),
                            timeout=ONE_HOUR_TIMEOUT * 2
                        )

                if hasattr(self, 'address'):
                    pg_id = self.address['poor_settlement']
                    scg = SavingsAndCreditGroup.objects.filter(primary_group_id=pg_id).first()
                    if scg:
                        scg.members.add(pg_member)

            # cls.finalize_survey_response(survey_id=self.survey, instance=instance, serializer=self)

            # updating response cache count in thread
            Thread(target=instance.update_response_cache_count).start()

            return instance

    def update(self, instance, validated_data):
        try:
            update_log = PGSurveyUpdateLog.objects.create(
                survey_response=instance,
                requested_time=int(datetime.now().timestamp() * 1000),
                status=PGSurveyUpdateEnum.IN_PROGRESS.value,
                created_by=self._kwargs['context']['request'].c_user
            )
            perform_async(method=instance.perform_pg_survey_update,
                          args=(instance, instance.id, self.questions, update_log))
            return instance
        except Exception as exp:
            ErrorLog.log(exp)

    class Meta:
        model = SurveyResponse
        list_serializer_class = SurveyResponseListSerializer
        fields = ('id', 'survey', 'tsync_id', 'address', 'location', 'imei_number', 'survey_time', 'respondent_client',
                  'last_updated', 'questions', 'photos')
