"""
Created by tareq on 10/3/17
"""
import uuid
from collections import OrderedDict
from datetime import datetime

from django import forms
from django.db import transaction
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField, \
    GenericMultipleChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models import PGSurveyUpdateLog
from blackwidow.core.models.clients.client_meta import ClientMeta
from blackwidow.core.models.common.membership_status import PrimaryGroupMemberStatus
from blackwidow.core.models.common.phonenumber import PhoneNumber
from blackwidow.core.models.organizations.organization import Organization
from blackwidow.engine.enums.pg_survey_update_enum import PGSurveyUpdateEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions.exceptions import BWException
from blackwidow.engine.extensions.async_task import perform_async
from undp_nuprp.approvals.models import EligibleBusinessGrantee, EligibleApprenticeshipGrantee, \
    EligibleEducationEarlyMarriageGrantee, EligibleEducationDropOutGrantee, SEFGrantDisbursement, SEFBusinessGrantee, \
    SEFApprenticeshipGrantee, SEFEducationDropoutGrantee, SEFEducationChildMarriageGrantee, SEFNutritionGrantee
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.reports.config.constants.pg_survey_constants import PHONE_QUESTION, NID_QUESTION, NAME_QUESTION_CODE, \
    NID_AVAILABILITY_QUESTION
from undp_nuprp.survey.models import Survey, Section, Question, SurveyResponse, QuestionResponse, Answer

__author__ = 'Tareq, Ziaul Haque'

status_choices = [("", "Select One")]
status_choices += PrimaryGroupMemberStatus.get_enum_list()


class PrimaryGroupMemberForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(PrimaryGroupMemberForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.ordered_fields = OrderedDict()

        self.ordered_fields['name'] = forms.CharField(initial=instance.name if instance else None)

        try:
            _assigned_city = instance.assigned_to.parent.address.geography.parent_id
        except:
            _assigned_city = None

        self.ordered_fields['assigned_cdc'] = GenericModelChoiceField(
            label='CDC',
            initial=instance.assigned_to.parent
            if instance and instance.assigned_to and instance.assigned_to.parent else None,
            queryset=CDC.objects.all(), widget=forms.Select(
                attrs={
                    'class': 'select2',
                    'width': '220'
                }
            ))

        self.ordered_fields['assigned_to'] = GenericModelChoiceField(
            label='Primary Group',
            initial=instance.assigned_to if instance else None,
            queryset=PrimaryGroup.objects.all(), widget=forms.TextInput(
                attrs={
                    'class': 'select2-input',
                    'width': '220',
                    'max-height': '20',
                    'height': '400',
                    'data-depends-on': 'assigned_cdc',
                    'data-depends-property': 'parent:id',
                    'data-url': reverse(PrimaryGroup.get_route_name(
                        action=ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                })
        )
        self.ordered_fields['pg_member_id'] = forms.IntegerField(
            label='PG member ID',
            initial=instance.assigned_code if instance else None
        )

        self.ordered_fields['national_id'] = forms.IntegerField(
            label='National ID',
            initial=instance.client_meta.national_id if instance and instance.client_meta else None,
            required=False
        )
        self.ordered_fields['mobile_no'] = forms.IntegerField(
            label='Mobile Number',
            initial=instance.phone_number.phone if instance and instance.phone_number else None
        )

        self.ordered_fields['status'] = forms.ChoiceField(
            choices=status_choices,
            required=False,
            widget=forms.Select(
                attrs={'class': 'select2', 'width': '220'}
            ), initial=""
        )

        # process survey questions - start
        survey_response = SurveyResponse.objects.filter(respondent_client=self.instance).first()
        question_response_dict = {}
        if survey_response:
            question_response_count = 0
            qr_queryset = QuestionResponse.objects.filter(
                section_response__survey_response=survey_response,
            ).exclude(
                section_response__section__name='Family Profile'
            ).values('pk', 'tsync_id', 'index', 'answer_text',
                     'answer_id', 'section_response__section_id', 'question_id')
            for item in qr_queryset:
                question_response_count += 1
                key = (item['section_response__section_id'], item['question_id'])
                if key not in question_response_dict.keys():
                    question_response_dict[key] = []
                question_response_dict[key].append(item)

            # handle family profile
            qr_queryset = QuestionResponse.objects.filter(
                section_response__survey_response=survey_response,
                section_response__section__name='Family Profile'
            ).values('pk', 'tsync_id', 'index', 'answer_text',
                     'answer_id', 'section_response__section_id', 'question_id')
            family_profile_max_index = 0
            for item in qr_queryset:
                question_response_count += 1
                if item['index'] > family_profile_max_index:
                    family_profile_max_index = item['index']
                key = (item['section_response__section_id'], item['question_id'], item['index'])
                if key not in question_response_dict.keys():
                    question_response_dict[key] = []
                question_response_dict[key].append(item)

            survey = Survey.objects.get(name='PG Member Survey Questionnaire')
            section_queryset = Section.objects.filter(
                survey=survey
            ).exclude(name='Family Profile').values('pk', 'name').order_by('order')
            question_count = 0
            questions = []
            question_ids = []

            answer_dict = {}
            option_dict = {}
            for item in Answer.objects.filter(question__section__survey=survey).values('pk', 'question',
                                                                                       'text').order_by('order'):
                answer_dict[item['question']] = item['pk']
                answer_dict[(item['question'], item['text'])] = item['pk']
                if item['question'] not in option_dict.keys():
                    option_dict[item['question']] = [("", "Select one"), ]
                option_dict[item['question']].append((item['text'], item['text']), )

            all_question_queryset = Question.objects.filter(
                section__survey=survey
            ).values('pk', 'section_id', 'question_type', 'question_code', 'text').order_by('order')
            section_wise_questions = {}
            for item in all_question_queryset:
                if item['section_id'] not in section_wise_questions.keys():
                    section_wise_questions[item['section_id']] = []
                section_wise_questions[item['section_id']].append(item)

            for section in section_queryset:
                question_queryset = section_wise_questions.get(section['pk'], [])
                _fields = []
                for question in question_queryset:
                    question_count += 1
                    _field_name = "question_{}{}".format(section['pk'], question['pk'])
                    _initial_value = question_response_dict.get((section['pk'], question['pk']), None)
                    question_ids.append(question['pk'])

                    if question['question_type'] == QuestionTypeEnum.SingleSelectInput.value:
                        choices = option_dict.get(question['pk'], [])
                        self.ordered_fields[_field_name] = forms.ChoiceField(
                            choices=choices, required=False,
                            label="{}: {}".format(question['question_code'], question['text']),
                            widget=forms.Select(
                                attrs={'class': 'select2', 'width': '220'}
                            ), initial=_initial_value[0]['answer_text'] if _initial_value else ""
                        )
                    elif question['question_type'] == QuestionTypeEnum.MultipleSelectInput.value:
                        choices = option_dict.get(question['pk'], [])
                        self.ordered_fields[_field_name] = GenericMultipleChoiceField(
                            choices=choices, required=False,
                            label="{}: {}".format(question['question_code'], question['text']),
                            widget=forms.SelectMultiple(
                                attrs={'class': 'select2', 'width': '220'}
                            ),
                            initial=",".join(
                                [_value['answer_text'] for _value in _initial_value]) if _initial_value else ""
                        )
                    elif question['question_type'] == QuestionTypeEnum.EditableSelectInput.value:
                        choices = option_dict.get(question['pk'], [])
                        self.ordered_fields[_field_name] = forms.ChoiceField(
                            choices=choices, required=False,
                            label="{}: {}".format(question['question_code'], question['text']),
                            widget=forms.Select(
                                attrs={'class': 'select2', 'width': '220'}
                            ), initial=_initial_value[0]['answer_text'] if _initial_value else ""
                        )
                    elif question['question_type'] == QuestionTypeEnum.NumberInput.value:
                        self.ordered_fields[_field_name] = forms.IntegerField(
                            label="{}: {}".format(question['question_code'], question['text']),
                            required=False,
                            initial=_initial_value[0]['answer_text'] if _initial_value else "",
                            widget=forms.NumberInput()
                        )
                    else:
                        self.ordered_fields[_field_name] = forms.CharField(
                            label="{}: {}".format(question['question_code'], question['text']),
                            required=False,
                            initial=_initial_value[0]['answer_text'] if _initial_value else ""
                        )

                    _question_dict = {
                        'question': question['pk'],
                        'question_text': question['text'],
                        'question_code': question['question_code'],
                        'section': section['pk'],
                        'field_name': _field_name,
                        'index': 0,
                        'is_family_profile': False,
                        'initial_question_responses': _initial_value,
                        'question_type': question['question_type']
                    }
                    questions.append(_question_dict)

                    _fields.append(_field_name)
                self.Meta.tabs[section['name']] = _fields

            # handle family profile
            section = Section.objects.filter(survey=survey, name='Family Profile').first()
            if section:
                for family_profile_index in range(family_profile_max_index):
                    family_profile_index = family_profile_index + 1
                    _fields = []
                    tab_name = "{}#{}".format(section.name, family_profile_index)

                    question_queryset = section_wise_questions.get(section.pk, [])
                    _fields = []
                    for question in question_queryset:
                        question_count += 1
                        question_ids.append(question['pk'])
                        _field_name = "question_{}{}{}".format(section.pk, question['pk'], family_profile_index)
                        _initial_value = question_response_dict.get((section.pk, question['pk'], family_profile_index),
                                                                    None)

                        if question['question_type'] == QuestionTypeEnum.SingleSelectInput.value:
                            choices = option_dict.get(question['pk'], [])
                            self.ordered_fields[_field_name] = forms.ChoiceField(
                                choices=choices, required=False,
                                label="{}: {}".format(question['question_code'], question['text']),
                                widget=forms.Select(
                                    attrs={'class': 'select2', 'width': '220'}
                                ), initial=_initial_value[0]['answer_text'] if _initial_value else ""
                            )
                        elif question['question_type'] == QuestionTypeEnum.MultipleSelectInput.value:
                            choices = option_dict.get(question['pk'], [])
                            self.ordered_fields[_field_name] = GenericMultipleChoiceField(
                                choices=choices, required=False,
                                label="{}: {}".format(question['question_code'], question['text']),
                                widget=forms.SelectMultiple(
                                    attrs={'class': 'select2', 'width': '220'}
                                ),
                                initial=",".join(
                                    [_value['answer_text'] for _value in _initial_value]) if _initial_value else ""
                            )
                        elif question['question_type'] == QuestionTypeEnum.EditableSelectInput.value:
                            choices = option_dict.get(question['pk'], [])
                            self.ordered_fields[_field_name] = forms.ChoiceField(
                                choices=choices, required=False,
                                label="{}: {}".format(question['question_code'], question['text']),
                                widget=forms.Select(
                                    attrs={'class': 'select2', 'width': '220'}
                                ), initial=_initial_value[0]['answer_text'] if _initial_value else ""
                            )
                        elif question['question_type'] == QuestionTypeEnum.NumberInput.value:
                            self.ordered_fields[_field_name] = forms.IntegerField(
                                label="{}: {}".format(question['question_code'], question['text']),
                                required=False,
                                initial=_initial_value[0]['answer_text'] if _initial_value else "",
                                widget=forms.NumberInput()
                            )
                        else:
                            self.ordered_fields[_field_name] = forms.CharField(
                                label="{}: {}".format(question['question_code'], question['text']),
                                required=False,
                                initial=_initial_value[0]['answer_text'] if _initial_value else ""
                            )

                        _question_dict = {
                            'question': question['pk'],
                            'question_text': question['text'],
                            'question_code': question['question_code'],
                            'section': section.pk,
                            'field_name': _field_name,
                            'index': family_profile_index,
                            'is_family_profile': True,
                            'initial_question_responses': _initial_value,
                            'question_type': question['question_type']
                        }
                        questions.append(_question_dict)

                        _fields.append(_field_name)
                    self.Meta.tabs[tab_name] = _fields

            setattr(self, 'answer_dict', answer_dict)
            setattr(self, 'questions', questions)
            print("Question Count: {}, Question Response Count: {}".format(question_count, question_response_count))

        setattr(self, 'survey_response', survey_response)
        # process survey questions - end

        self.fields = self.ordered_fields

    def clean(self):
        _given_pg_mem_id = self.data.get('pg_member_id', '')
        _assigned_to = self.data.get('assigned_to', None)

        if self.is_new_instance and self.cleaned_data['status'] == "":
            self.cleaned_data['status'] = 'Active'

        if len(_given_pg_mem_id) != 12:
            raise BWException('Please put valid PG member ID')

        if not _assigned_to:
            self.add_error('assigned_to', 'This field cannot be empty!')

        pg_code = PrimaryGroup.objects.get(pk=int(_assigned_to)).assigned_code

        if _given_pg_mem_id[:10] != pg_code:
            raise BWException('Please put valid PG member ID')

        if not self.is_new_instance and self.instance.assigned_code == _given_pg_mem_id:
            return self.cleaned_data

        if PrimaryGroupMember.objects.filter(assigned_code=_given_pg_mem_id).exists():
            raise BWException("This PG member ID No already exists")

        return self.cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            _given_pg_mem_id = self.data.get('pg_member_id', '')
            if self.is_new_instance:
                self.instance.assigned_code = _given_pg_mem_id

            instance = super(PrimaryGroupMemberForm, self).save(commit=commit)
            mobile_no = self.data.get('mobile_no', None)
            national_id = self.data.get('national_id', None)

            if 'name' in self.changed_data:
                if instance.assigned_code:
                    eligible_list = [
                        EligibleBusinessGrantee, EligibleApprenticeshipGrantee,
                        EligibleEducationDropOutGrantee, EligibleEducationEarlyMarriageGrantee
                    ]
                    for eligible in eligible_list:
                        member = eligible.objects.filter(pg_member__assigned_code=instance.assigned_code).first()
                        if member:
                            member.grantee_name = instance.name
                            member.save()

                    grantee_models = [
                        SEFGrantDisbursement, SEFBusinessGrantee,
                        SEFApprenticeshipGrantee, SEFEducationDropoutGrantee,
                        SEFEducationChildMarriageGrantee
                    ]
                    for klass in grantee_models:
                        member = klass.objects.filter(pg_member_assigned_code=instance.assigned_code).first()
                        if member:
                            member.pg_member_name = instance.name
                            member.name = instance.name
                            member.save()

            updated_nid = None
            updated_phone = None

            updated_instance = False

            if mobile_no:
                updated_phone = str(mobile_no)
                if not instance.phone_number:
                    phone_number = PhoneNumber()
                    phone_number.phone = str(mobile_no)
                    phone_number.save()
                    instance.phone_number = phone_number
                    updated_instance = True

                elif instance.phone_number.phone and instance.phone_number.phone != str(mobile_no):
                    instance.phone_number.phone = str(mobile_no)
                    instance.phone_number.save()

            if national_id:
                updated_nid = str(national_id)
                if not instance.client_meta:
                    client_meta = ClientMeta.objects.create(organization=Organization.get_organization_from_cache())
                    client_meta.national_id = str(national_id)
                    client_meta.save()
                    instance.client_meta = client_meta
                    updated_instance = True
                elif instance.client_meta and not instance.client_meta.national_id:
                    instance.client_meta.national_id = str(national_id)
                    instance.client_meta.save()
                elif instance.client_meta and instance.client_meta.national_id and instance.client_meta.national_id != str(
                        national_id):
                    instance.client_meta.national_id = str(national_id)
                    instance.client_meta.save()

            if _given_pg_mem_id and _given_pg_mem_id != instance.assigned_code:
                fix_grantee_and_grant_pg_member_id(
                    instance.assigned_code,
                    _given_pg_mem_id,
                    datetime.now().timestamp() * 1000
                )
                instance.assigned_code = _given_pg_mem_id
                updated_instance = True

            if updated_instance:
                instance.save()

            survey_response = getattr(self, 'survey_response')
            if survey_response:
                # process survey questions - start
                questions = getattr(self, 'questions')
                answer_dict = getattr(self, 'answer_dict')

                mandatory_question_mapping = {
                    NAME_QUESTION_CODE: instance.name,
                    PHONE_QUESTION: updated_phone,
                    NID_QUESTION: updated_nid,
                    NID_AVAILABILITY_QUESTION: "NID"
                }

                qr_dict_list = []
                for question_dict in questions:
                    _field_name = question_dict['field_name']
                    _question = question_dict['question']
                    _question_text = question_dict['question_text']
                    _question_code = question_dict['question_code']
                    _section = question_dict['section']
                    _question_type = question_dict['question_type']
                    _index = question_dict['index']
                    _is_family_profile = question_dict['is_family_profile']
                    _initial_question_responses = question_dict['initial_question_responses']

                    if _question_code in [PHONE_QUESTION, NID_QUESTION, NAME_QUESTION_CODE, NID_AVAILABILITY_QUESTION]:
                        answer_text = mandatory_question_mapping.get(_question_code, "")
                        if answer_text is not None and answer_text != "":
                            answer = answer_dict.get((_question, answer_text), None)
                            if not answer:
                                answer = answer_dict.get(_question, None)
                            if answer:
                                if _initial_question_responses:
                                    qr = _initial_question_responses[0]
                                    qr_dict_list.append(prepare_question_response_dict(
                                        _question, _question_text, qr['index'],
                                        qr['tsync_id'], answer_text, answer
                                    ))
                                else:
                                    qr_dict_list.append(prepare_question_response_dict(
                                        _question, _question_text, 0,
                                        uuid.uuid4().hex, answer_text, answer
                                    ))
                            else:
                                print(_question_type, _question_code, _question_text, answer_text)
                            continue

                    answer_text = self.cleaned_data[_field_name]
                    if answer_text is not None and answer_text != "":
                        if _question_type == QuestionTypeEnum.MultipleSelectInput.value:
                            for _answer_text in answer_text:
                                if _answer_text:
                                    _answer_text = str(_answer_text)
                                    answer = answer_dict.get((_question, _answer_text), None)
                                    if answer:
                                        _initial_response = [
                                            _initial_response for _initial_response in
                                            _initial_question_responses if
                                            _initial_response['answer_id'] == answer]
                                        if _initial_response:
                                            qr = _initial_response[0]
                                            qr_dict_list.append(prepare_question_response_dict(
                                                _question, _question_text, qr['index'],
                                                qr['tsync_id'], _answer_text, answer
                                            ))
                                        else:
                                            qr_dict_list.append(prepare_question_response_dict(
                                                _question, _question_text, _index,
                                                uuid.uuid4().hex, _answer_text, answer
                                            ))
                                    else:
                                        print(_question_type, _question_code, _question_text, answer_text)
                        else:
                            answer_text = str(answer_text)
                            answer = answer_dict.get((_question, answer_text), None)
                            if not answer:
                                answer = answer_dict.get(_question, None)

                            if answer:
                                if _initial_question_responses:
                                    qr = _initial_question_responses[0]
                                    qr_dict_list.append(prepare_question_response_dict(
                                        _question, _question_text, qr['index'],
                                        qr['tsync_id'], answer_text, answer
                                    ))
                                else:
                                    qr_dict_list.append(prepare_question_response_dict(
                                        _question, _question_text, _index,
                                        uuid.uuid4().hex, answer_text, answer
                                    ))
                            else:
                                print(_question_type, _question_code, _question_text, answer_text)
                    else:
                        print(_question_type, _question_code, _question_text, answer_text)
                # process survey questions - end

                # survey_response.update_survey_response_version_for_pg_member_update(
                #     name=instance.name,
                #     phone_number=updated_phone,
                #     national_id=updated_nid
                # )

                update_log = PGSurveyUpdateLog.objects.create(
                    survey_response=survey_response,
                    requested_time=int(datetime.now().timestamp() * 1000),
                    status=PGSurveyUpdateEnum.IN_PROGRESS.value,
                    created_by=instance.last_updated_by
                )
                perform_async(
                    method=survey_response.perform_pg_survey_update,
                    args=(survey_response, survey_response.id, qr_dict_list, update_log)
                )
            return instance

    class Meta(GenericFormMixin.Meta):
        model = PrimaryGroupMember
        fields = ['name', 'assigned_to', 'status', ]

        render_tab = True
        tabs = OrderedDict([
            ('Information about PG member',
             ['name', 'assigned_cdc', 'assigned_to', 'pg_member_id', 'national_id', 'mobile_no', 'status']),
        ])


def prepare_question_response_dict(question, question_text, index, tsync_id, answer_text, answer):
    _qr_dict = {
        'question': question,
        'question_text': question_text,
        'index': index,
        'tsync_id': tsync_id,
        'answer_text': answer_text,
        'answer': answer,
    }
    return _qr_dict


def fix_grantee_and_grant_pg_member_id(prev_code, new_code, current_time):
    SEFGrantDisbursement.objects.filter(
        pg_member_assigned_code=prev_code
    ).update(pg_member_assigned_code=new_code, last_updated=current_time)

    SEFBusinessGrantee.objects.filter(
        pg_member_assigned_code=prev_code
    ).update(pg_member_assigned_code=new_code, last_updated=current_time)

    SEFApprenticeshipGrantee.objects.filter(
        pg_member_assigned_code=prev_code
    ).update(pg_member_assigned_code=new_code, last_updated=current_time)

    SEFEducationDropoutGrantee.objects.filter(
        pg_member_assigned_code=prev_code
    ).update(pg_member_assigned_code=new_code, last_updated=current_time)

    SEFEducationChildMarriageGrantee.objects.filter(
        pg_member_assigned_code=prev_code
    ).update(pg_member_assigned_code=new_code, last_updated=current_time)

    SEFNutritionGrantee.objects.filter(
        pg_member_assigned_code=prev_code
    ).update(pg_member_assigned_code=new_code, last_updated=current_time)
