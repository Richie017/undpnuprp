from collections import OrderedDict

from django.db import models
from django.db.models.query_utils import Q

from blackwidow.core.models.config.importer_column_config import ImporterColumnConfig
from blackwidow.core.models.config.importer_config import ImporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.viewmodels.tabs_config import TabView
from blackwidow.engine.decorators.enable_import import enable_import
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, save_audit_log, is_object_context
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.tab_view_enum import ModelRelationType
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.utils.enums.answer_type_enum import AnswerTypeEnum
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.nuprp_admin.utils.enums.survey_status_enum import SurveyStatusEnum
from undp_nuprp.nuprp_admin.utils.import_helper.row_extractor import extract_row
from undp_nuprp.survey.models.entity.answer import Answer
from undp_nuprp.survey.models.entity.question import Question
from undp_nuprp.survey.models.entity.section import Section

__author__ = 'Tareq'


@decorate(save_audit_log, is_object_context, expose_api('survey'), enable_import,
          route(route='survey', group='Member Registration', module=ModuleEnum.Administration,
                display_name='Registration Questionnaire', group_order=1, item_order=1))
class Survey(OrganizationDomainEntity):
    name = models.CharField(max_length=512, blank=True)
    status = models.IntegerField(default=0)

    class Meta:
        app_label = 'survey'

    @property
    def render_status(self):
        return SurveyStatusEnum.get_status_name(self.status)

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedImport:
            return "Import Excel"

    @classmethod
    def table_columns(cls):
        return 'render_code', 'name', 'date_created', 'last_updated'

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.Delete, ViewActionEnum.AdvancedImport]

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details]

    @property
    def details_config(self):
        details = OrderedDict()
        details['code'] = self.code
        details['name'] = self.name
        details['status'] = self.render_status
        details['created_on'] = self.render_timestamp(self.date_created)
        details['updated_on'] = self.render_timestamp(self.last_updated)
        return details

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Export Excel / SPSS',
                action='advanced_export',
                icon='fbx-rightnav-edit',
                ajax='0',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Edit),
                classes='manage-action all-action',
                parent=None
            )
        ]

    @property
    def tabs_config(self):
        from undp_nuprp.survey.models.response.survey_response import SurveyResponse
        return [
            TabView(
                title='Response(s)',
                access_key='responses',
                route_name=self.__class__.get_route_name(ViewActionEnum.Tab),
                relation_type=ModelRelationType.INVERTED,
                related_model='survey.SurveyResponse',
                queryset=SurveyResponse.get_role_based_queryset(queryset=SurveyResponse.objects.filter()),
                queryset_filter=Q(**{'survey_id': self.pk})
            )
        ]

    def approval_level_1_action(self, action, *args, **kwargs):
        if action == "Approved":
            self.status = SurveyStatusEnum.Published.value
            self.save()

    @classmethod
    def get_serializer(cls):
        _ODESerializer = OrganizationDomainEntity.get_serializer()

        class SurveySerializer(_ODESerializer):
            class Meta:
                model = cls
                fields = 'id', 'code', 'name', 'status', 'last_updated'

        return SurveySerializer

    @classmethod
    def importer_config(cls, organization=None, **kwargs):
        ImporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        importer_config, result = ImporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        importer_config.starting_row = 1
        importer_config.starting_column = 0
        importer_config.save(**kwargs)

        columns = list()
        column = 0
        for level in ['Survey', 'Section_Bn', 'Section_En', 'Question_code', 'Question_Bn', 'Question_EN',
                      'Question_Type', 'Parent_question', 'Mendatory?', 'Answer_Code', 'Answer_Bn', 'Answer_EN',
                      'Answer_type', 'Next', 'Comment']:
            columns.append(ImporterColumnConfig(
                column=column, column_name=level, property_name=level.lower(), ignore=False))
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
        survey_name = section_bn = section_en = question_code = question_bn = question_en = \
            question_type = question_group = parent_question = question_required = answer_code = answer_bn = \
            answer_en = answer_type = next_question = comment = ''
        section_order = 1
        question_order = 1
        answer_order = 1
        survey = section = question = answer = None
        next_question_dict = dict()
        for item in items:
            survey_name, section_bn, section_en, question_code, question_bn, question_en, question_type, \
            question_group, parent_question, question_required, answer_code, answer_bn, answer_en, answer_type, \
            next_question, comment = extract_row(row=item, values=[
                survey_name, section_bn, section_en, question_code, question_bn, question_en, question_type,
                question_group, parent_question, question_required, answer_code, answer_bn, answer_en, answer_type,
                next_question, comment])

            if item['0'] is not None:  # item['0'] = Survey Name
                survey, created = Survey.objects.get_or_create(name=survey_name, organization=organization)
            if item['1'] is not None or item['2'] is not None:  # item['1'] = Section-Bn, item['2'] = Section-EN
                section, created = Section.objects.get_or_create(survey=survey, name_bd=section_bn, name=section_en,
                                                                 organization=organization)
                if section.order != section_order:
                    section.order = section_order
                    section.save()
                section_order += 1
            if item['3'] is not None:  # item['3'] = Question-code
                type_of_question = QuestionTypeEnum.get_question_type_from_raw(question_type)
                question, created = Question.objects.get_or_create(question_code=str(question_code), section=section,
                                                                   organization=organization)
                updated = False
                if question.text != question_en:
                    question.text = question_en
                    updated = True
                if question.text_bd != question_bn:
                    question.text_bd = question_bn
                    updated = True
                if question.type != type_of_question:
                    question.question_type = type_of_question
                    updated = True
                if question.order != question_order:
                    question.order = question_order
                    updated = True
                _required = True if question_required and 'yes' in question_required.lower() else False
                if question.is_required != _required:
                    question.is_required = _required
                    updated = True
                if not item['7']:
                    question_group = ''
                if question.group != question_group:
                    question.group = question_group
                    updated = True
                question.group = question.group if question.group else ''
                if updated:
                    question.save()
                question_order += 1

                if str(question_code) in next_question_dict.keys():
                    candidate_answers = next_question_dict[str(question_code)]
                    for ans in candidate_answers:
                        if ans.next_question_id != question.pk:
                            ans.next_question = question
                            ans.save()

            if item['8'] is not None:  # item['8'] = parent-question
                parent_question_obj = Question.objects.filter(question_code=parent_question).first()
                if parent_question_obj and question.parent_id != parent_question_obj.pk:
                    question.parent_id = parent_question_obj
                    question.save()

            if item['13'] is not None:
                answer_bn = item['11']
                answer_en = item['12']
                type_of_answer = AnswerTypeEnum.get_answer_type_from_raw(answer_type)
                answer, created = Answer.objects.get_or_create(organization=organization, question=question,
                                                               answer_code=str(answer_code))
                updated = False
                if answer.text != answer_en:
                    answer.text = answer_en
                    updated = True
                if answer.text_bd != answer_bn:
                    answer.text_bd = answer_bn
                    updated = True
                if answer.answer_type != type_of_answer:
                    answer.answer_type = type_of_answer
                    updated = True
                if answer.order != answer_order:
                    answer.order = answer_order
                    updated = True
                if updated:
                    answer.save()
                answer_order += 1

                if next_question is not None:
                    if str(next_question) not in next_question_dict.keys():
                        next_question_dict[str(next_question)] = list()
                    next_question_dict[str(next_question)].append(answer)
