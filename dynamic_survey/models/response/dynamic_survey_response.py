from collections import OrderedDict
from datetime import datetime, date

from django import forms
from django.db import models
from django.db.models.aggregates import Count
from django.forms.forms import Form

import settings
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.models import ExporterColumnConfig
from blackwidow.core.models import ExporterConfig
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.core.models.file.imagefileobject import ImageFileObject
from blackwidow.engine.constants.cache_constants import ONE_WEEK_TIMEOUT, MODEL_CACHE_PREFIX
from blackwidow.engine.decorators.expose_model import expose_api
from blackwidow.engine.decorators.route_partial_routes import route
from blackwidow.engine.decorators.utility import decorate, is_object_context, has_status_data, save_audit_log
from blackwidow.engine.enums.modules_enum import ModuleEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.clock import Clock
from blackwidow.engine.managers.cachemanager import CacheManager
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from dynamic_survey.enums.dynamic_survey_question_type_enum import DynamicSurveyQuestionTypeEnum
from dynamic_survey.enums.dynamic_survey_status_enum import DynamicSurveyStatusEnum
from dynamic_survey.models.entity.dynamic_question import DynamicQuestion
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum

__author__ = 'Razon'


@decorate(expose_api('dynamic-survey-response'), is_object_context, has_status_data, save_audit_log,
          route(route='dynamic-survey-response', group='Dynamic Survey', module=ModuleEnum.Administration,
                display_name='Survey Response'))
class DynamicSurveyResponse(OrganizationDomainEntity):
    survey = models.ForeignKey('dynamic_survey.DynamicSurvey', null=True, on_delete=models.SET_NULL)
    survey_time = models.BigIntegerField(default=0)
    on_spot_creation_time = models.BigIntegerField(default=0)
    respondent_client = models.ForeignKey('core.Client', null=True, on_delete=models.SET_NULL)
    respondent_unit = models.ForeignKey('core.InfrastructureUnit', null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey('core.Location', null=True)
    address = models.ForeignKey('core.ContactAddress', null=True)

    class Meta:
        app_label = 'dynamic_survey'

    @classmethod
    def get_cache_prefix(cls):
        """
        This method helps to store total survey by name in cache
        :return: String cache prefix
        """
        return MODEL_CACHE_PREFIX + cls.__name__ + '_'

    @property
    def details_view_title(self):
        title = self.survey.name if self.survey else ''
        return title

    @classmethod
    def get_button_title(cls, button=ViewActionEnum.Details):
        if button == ViewActionEnum.AdvancedExport:
            return "Export"
        elif button == ViewActionEnum.Import:
            return "Import"

    @classmethod
    def get_export_file_name(cls):
        return 'DynamicSurveyResponses'

    def update_response_cache_count(self):
        cache_key = self.get_cache_prefix() + str(self.created_by_id)
        response_cache = CacheManager.get_from_cache_by_key(key=cache_key)
        if response_cache is None:
            response_cache = dict()
            survey_response_queryset = DynamicSurveyResponse.objects.filter(
                created_by_id=self.created_by_id).values('survey_id', 'survey__name').annotate(count=Count('pk'))

            for _sr in survey_response_queryset:
                response_cache[_sr['survey_id']] = {
                    'survey_name': _sr['survey__name'],
                    'count': _sr['count']
                }
        elif self.survey_id not in response_cache.keys():
            response_cache[self.survey_id] = {
                'survey_name': self.survey.name,
                'count': DynamicSurveyResponse.objects.filter(survey_id=self.survey_id,
                                                              created_by_id=self.created_by_id).aggregate(
                    count=Count('pk'))['count']
            }
        else:
            response_cache[self.survey_id]['count'] += 1
        CacheManager.set_cache_element_by_key(key=cache_key, value=response_cache, timeout=ONE_WEEK_TIMEOUT)

    def save(self, *args, organization=None, **kwargs):
        result = super(DynamicSurveyResponse, self).save(*args, organization=organization, **kwargs)
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
            'completed_dynamic_survey': list(response_cache.values())
        }

    @classmethod
    def get_manage_buttons(cls):
        return [ViewActionEnum.AdvancedExport, ViewActionEnum.Delete]

    @property
    def render_on_spot_creation_time(self):
        return self.render_timestamp(self.on_spot_creation_time)

    @property
    def render_sync_time(self):
        return self.render_timestamp(self.date_created)

    @property
    def render_created_by(self):
        return self.created_by if self.created_by else 'N/A'

    @classmethod
    def get_datetime_fields(cls):
        return ['date_created', 'last_updated', 'on_spot_creation_time']

    @property
    def details_config(self):
        details = OrderedDict()
        details['survey'] = self.survey if self.survey else 'N/A'
        details['client'] = self.respondent_client if self.respondent_client else 'N/A'
        details['location'] = self.location if self.location else 'N/A'
        details['on_spot_creation_time'] = self.render_on_spot_creation_time
        details['sync_time'] = self.render_sync_time
        details['created_by'] = self.render_created_by
        return details

    @classmethod
    def order_by_on_spot_creation_time(cls):
        return ['on_spot_creation_time']

    @classmethod
    def get_object_inline_buttons(cls):
        return [ViewActionEnum.Details, ViewActionEnum.Delete]

    def details_link_config(self, **kwargs):
        return [
            dict(
                name='Print Survey Response',
                action='print_dynamic_survey_response',
                icon='fbx-rightnav-print',
                ajax='0',
                classes='manage-action popup',
                url_name=self.__class__.get_route_name(action=ViewActionEnum.Print)
            ),

        ]

    @classmethod
    def table_columns(cls, *args, **kwargs):
        return [
            'render_code', 'survey', 'respondent_client', 'created_by',
            'render_on_spot_creation_time', 'last_updated'
        ]

    @classmethod
    def get_serializer(cls):
        from dynamic_survey.serializers.response.v_1.dynamic_survey_response_serializer import \
            DynamicSurveyResponseSerializer
        return DynamicSurveyResponseSerializer

    @classmethod
    def exporter_config(cls, organization=None, **kwargs):
        ExporterConfig.objects.filter(model=cls.__name__, organization=organization).delete()
        exporter_config, created = ExporterConfig.objects.get_or_create(model=cls.__name__, organization=organization)
        columns = [
            ExporterColumnConfig(column=0, column_name='Code',
                                 property_name='render_code', ignore=False),

        ]
        for c in columns:
            c.save(organization=organization, **kwargs)
            exporter_config.columns.add(c)
        return exporter_config

    def export_item(self, workbook=None, columns=None, row_number=None, **kwargs):
        return self.pk, row_number + 1

    @classmethod
    def finalize_export(cls, workbook=None, row_number=None, query_set=None, **kwargs):
        return workbook

    @classmethod
    def get_export_dependant_fields(cls):
        class AdvancedExportDependentForm(Form):
            def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
                super(AdvancedExportDependentForm, self).__init__(data=data, files=files, prefix=prefix, **kwargs)
                from dynamic_survey.models.design.dynamic_survey import DynamicSurvey
                today = date.today().replace(day=1)
                year_choices = tuple()
                month_choices = tuple(
                    [(today.replace(month=i).strftime('%B'), today.replace(month=i).strftime('%B'))
                     for i in range(1, 13)])
                for y in range(2000, 2100):
                    year_choices += ((y, str(y)),)

                self.fields['survey'] = \
                    GenericModelChoiceField(
                        label='Survey Name', empty_label=None, required=True,
                        queryset=DynamicSurvey.objects.using(
                            BWDatabaseRouter.get_export_database_name()
                        ).filter(
                            status__in=[
                                DynamicSurveyStatusEnum.Disabled.value,
                                DynamicSurveyStatusEnum.Published.value
                            ]
                        ).order_by("name", "-version"),
                        widget=forms.Select(attrs={'class': 'select2'})
                    )

                self.fields['year'] = forms.ChoiceField(
                    choices=year_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.year
                )

                self.fields['month'] = forms.ChoiceField(
                    choices=month_choices,
                    widget=forms.Select(
                        attrs={'class': 'select2', 'width': '220'}
                    ), initial=today.strftime('%B')
                )

        return AdvancedExportDependentForm

    @classmethod
    def get_photo_response(cls, query_set=None, **kwargs):
        """
        :param query_set:
        :param kwargs:
        :return: A dictionary of following structure

                {
                    'survey_client_name1_survey_date_time1': [photo11, photo12, ...],
                    'survey_client_name2_survey_date_time2': [photo21, photo22, ...]
                }
        """
        photo_dict = {}
        from dynamic_survey.models import DynamicQuestionResponse
        query_params = kwargs.get('query_params')
        if query_params:
            survey_id = query_params.get("survey")
            time_from = query_params.get("on_spot_creation_time_from")
            time_to = query_params.get("on_spot_creation_time_to")
            try:
                survey_id = int(survey_id)
            except Exception:
                survey_id = -1

            if survey_id <= 0:
                return photo_dict

            question_responses = DynamicQuestionResponse.objects.filter(
                section_response__survey_response__survey_id=survey_id)

            try:
                time_from = datetime.strptime(time_from, "%d/%m/%Y") \
                                .replace(hour=0, minute=0, second=0).timestamp() * 1000
            except Exception:
                time_from = None
            try:
                time_to = datetime.strptime(time_to, "%d/%m/%Y") \
                              .replace(hour=23, minute=59, second=59).timestamp() * 1000
            except Exception:
                time_to = None

            if time_from:
                question_responses = question_responses.filter(
                    section_response__survey_response__on_spot_creation_time__gte=time_from)

            if time_to:
                question_responses = question_responses.filter(
                    section_response__survey_response__on_spot_creation_time__lte=time_to)

            for question_response in question_responses:
                client_name = question_response.section_response.survey_response.respondent_client.name
                on_spot_creation_time = question_response.section_response.survey_response.on_spot_creation_time
                survey_date = datetime.fromtimestamp(on_spot_creation_time / 1000).strftime('%d-%m-%Y_%H-%M-%S')
                photo_list = photo_dict.get(client_name + "_" + survey_date, None)
                if photo_list is None:
                    photo_list = []
                    photo_dict[client_name + "_" + survey_date] = photo_list
                photo_list.append(question_response.photo)

            return photo_dict

    @classmethod
    def initialize_export(cls, workbook=None, columns=None, row_number=None, query_set=None, **kwargs):

        from dynamic_survey.models import DynamicQuestionResponse
        query_params = kwargs.get('query_params')
        if query_params:
            survey_id = query_params.get("survey")
            time_from = query_params.get("on_spot_creation_time_from")
            time_to = query_params.get("on_spot_creation_time_to")
            try:
                survey_id = int(survey_id)
            except Exception:
                survey_id = -1

            if survey_id <= 0:
                return workbook, row_number

            question_responses = DynamicQuestionResponse.objects.using(
                BWDatabaseRouter.get_export_database_name()
            ).exclude(
                section_response__survey_response__is_deleted=True
            ).filter(section_response__survey_response__survey_id=survey_id)

            try:
                time_from = datetime.strptime(time_from, "%d/%m/%Y") \
                                .replace(hour=0, minute=0, second=0).timestamp() * 1000
            except Exception:
                time_from = None
            try:
                time_to = datetime.strptime(time_to, "%d/%m/%Y") \
                              .replace(hour=23, minute=59, second=59).timestamp() * 1000
            except Exception:
                time_to = None

            # As survey time is replaced with on spot creation time, time filtering is changed thereby
            if time_from:
                question_responses = question_responses.filter(
                    section_response__survey_response__on_spot_creation_time__gte=time_from)

            if time_to:
                question_responses = question_responses.filter(
                    section_response__survey_response__on_spot_creation_time__lte=time_to)

            survey_response_dict = {}

            survey_basic_information = question_responses.order_by('section_response__survey_response_id').distinct(
                'section_response__survey_response_id').values(
                'section_response__survey_response_id', 'section_response__survey_response__on_spot_creation_time',
                'section_response__survey_response__respondent_client__name',
                'section_response__survey_response__respondent_unit__name',
                'section_response__survey_response__location__latitude',
                'section_response__survey_response__location__longitude', 'created_by__phones__phone',
                'section_response__survey_response__code', 'created_by__name')

            for survey_response in survey_basic_information:
                survey_response_id = survey_response['section_response__survey_response_id']
                survey_time = survey_response['section_response__survey_response__on_spot_creation_time']
                respondent_client = survey_response['section_response__survey_response__respondent_client__name']
                respondent_unit = survey_response['section_response__survey_response__respondent_unit__name']
                latitude = survey_response['section_response__survey_response__location__latitude']
                longitude = survey_response['section_response__survey_response__location__longitude']
                phone = survey_response['created_by__phones__phone']
                survey_response_code = survey_response['section_response__survey_response__code']
                user_name = survey_response['created_by__name']

                survey_response_dict[survey_response_id] = OrderedDict()
                survey_response_dict[survey_response_id]['Survey Time'] = \
                    Clock.get_user_local_time(survey_time).strftime("%d/%m/%Y") if survey_time else None
                survey_response_dict[survey_response_id]['Respondent Client'] = respondent_client
                survey_response_dict[survey_response_id]['respondent_unit'] = respondent_unit
                survey_response_dict[survey_response_id]['Latitude'] = latitude
                survey_response_dict[survey_response_id]['Longitude'] = longitude
                survey_response_dict[survey_response_id]['User Contact Number'] = phone
                survey_response_dict[survey_response_id]['Survey Response Code'] = survey_response_code
                survey_response_dict[survey_response_id]['User Name'] = user_name

            survey_questions = DynamicQuestion.objects.using(
                BWDatabaseRouter.get_export_database_name()
            ).filter(section__survey_id=survey_id).values(
                'id', 'question_type', 'parent_id', 'parent__question_code', 'parent__text', 'question_code', 'text',
                'parent__question_type', 'section_id', 'section__name').order_by('section__order', 'order')

            """
                   Information about the dictionary data used in following code:

                   #1: _question_id_info_dict:

                    :key question ID
                    :value a dictionary contains this keys: text, parent_id, parent_question_code, section_id, section_name,
                    question_type, parent_question_type
                    example:
                    _question_id_info_dict[question_id] = {
                        'question_code': '',
                        'parent_id': '',
                        'parent_question_code': '',
                        'section_id': '',
                        'section_name': '',
                        'question_type': '',
                        'parent_question_type': ''
                    }

                    #2: _section_id_name_dict:
                    :key section ID
                    :value is section name and list of question exist in that section maintaining the order of the
                    questions
                    example:
                    _section_id_name_dict[section_id] = {
                        'name': Name of the section,
                        'questions': [id of the questions for following section]
                    }

                    #3: _child_grid_ques_dict
                    key: question ID which type is grid question
                    value: child question ID's of the following question
                    example:
                    _child_grid_ques_dict[question_id] = [
                        List child question's ID
                    ]

                    #4: _grid_qid_by_index_dict
                    key: question ID which type is grid question
                    value: A list indexes that found from question responses queryset
                    example:
                    _grid_qid_by_index_dict[question_id] = [
                        List of index found in question resposne queryset i.e, 1,2,3...
                    ]

                    #5: _sr_ques_index_ans_dict
                    key: survey response ID
                    value: A dictionary contains the answer of the question by index. index > 0 means grid question
                    example:
                    _sr_ques_index_ans_dict[survey_response_id] = {
                        'question_id': {
                            'index': 'answer_of_the_question'
                        }
                    }
            """

            _question_id_info_dict = OrderedDict()
            _section_id_name_dict = OrderedDict()
            _child_grid_ques_dict = OrderedDict()
            _grid_qid_by_index_dict = {}
            _sr_ques_index_ans_dict = {}
            _default_headers = ['Survey Time', 'Survey Response Code', 'User Name', 'User Contact Number', 'Latitude',
                                'Longitude']
            nested_headers = False

            for survey_question in survey_questions:
                parent_question_id = survey_question['parent_id']
                section_id = survey_question['section_id']
                section_name = survey_question['section__name']
                question_id = survey_question['id']
                question_code = survey_question['question_code']
                question_text = survey_question['text']
                parent_ques_code = survey_question['parent__question_code']
                parent_ques_text = survey_question['parent__text']
                question_type = survey_question['question_type']
                parent_question_type = survey_question['parent__question_type']

                if section_id not in _section_id_name_dict:
                    _section_id_name_dict[section_id] = {
                        'name': section_name,
                        'questions': []
                    }
                if parent_question_id:
                    nested_headers = True

                if parent_question_type == QuestionTypeEnum.DynamicGrid.value:
                    if parent_question_id not in _child_grid_ques_dict:
                        _child_grid_ques_dict[parent_question_id] = []
                        _grid_qid_by_index_dict[parent_question_id] = []
                    _child_grid_ques_dict[parent_question_id].append(question_id)
                else:
                    _section_id_name_dict[section_id]['questions'].append(question_id)

                _question_id_info_dict[question_id] = {
                    'question_code': question_code + ' ' + question_text,
                    'parent_id': parent_question_id,
                    'parent_question_code': (parent_ques_code + ' ' + parent_ques_text)
                    if parent_ques_code and parent_ques_text else '',
                    'section_id': section_id,
                    'section_name': section_name,
                    'question_type': question_type,
                    'parent_question_type': parent_question_type
                }

            question_responses = question_responses.values(
                'photo_id', 'photo__name', 'question_id', 'answer_text',
                'question__question_type', 'section_response__survey_response_id', 'index', 'question__parent_id',
                'question__parent__text').order_by('section_response__survey_response_id', 'question__order', 'index',
                                                   'answer_text')

            for question_response in question_responses:
                question_id = question_response['question_id']
                parent_question_id = question_response['question__parent_id']
                question_type = question_response['question__question_type']

                answer = settings.SITE_ROOT + ImageFileObject.objects.using(
                    BWDatabaseRouter.get_export_database_name()
                ).get(pk=question_response['photo_id']).relative_url[1:] \
                    if question_type == 'image' and question_response['photo_id'] else question_response['answer_text']

                answer = '=HYPERLINK("{}", "{}")'.format(answer, question_response['photo__name']) \
                    if question_type == 'image' and question_response['photo_id'] else answer
                survey_response_id = question_response['section_response__survey_response_id']
                index = question_response['index']

                if parent_question_id in _grid_qid_by_index_dict:
                    if index not in _grid_qid_by_index_dict[parent_question_id]:
                        _grid_qid_by_index_dict[parent_question_id].append(index)

                if survey_response_id not in _sr_ques_index_ans_dict:
                    _sr_ques_index_ans_dict[survey_response_id] = {}

                if question_id not in _sr_ques_index_ans_dict[survey_response_id]:
                    _sr_ques_index_ans_dict[survey_response_id][question_id] = {}

                if index not in _sr_ques_index_ans_dict[survey_response_id][question_id]:
                    _sr_ques_index_ans_dict[survey_response_id][question_id][index] = answer
                else:
                    sep = ', '
                    _sr_ques_index_ans_dict[survey_response_id][question_id][index] += sep + answer
                    _sr_ques_index_ans_dict[survey_response_id][question_id][index] = ', '. \
                        join(set(ques_answer.strip() for ques_answer in
                                 _sr_ques_index_ans_dict[survey_response_id][question_id][index].split(',')))

            column_number = 1

            for h in _default_headers:
                workbook.cell(row=row_number, column=column_number).value = h
                if nested_headers:
                    workbook.merge_cells(
                        start_row=row_number, end_row=row_number + 1, start_column=column_number,
                        end_column=column_number)
                column_number += 1

            for _sec_info in _section_id_name_dict.values():
                _questions = _sec_info['questions']
                for q_id in _questions:
                    _ques_info = _question_id_info_dict[q_id]
                    if _ques_info['question_type'] == DynamicSurveyQuestionTypeEnum.DynamicGrid.value:
                        _grid_ques_ids = _child_grid_ques_dict[q_id]
                        _tot_grid_ques = len(_grid_ques_ids)
                        _grid_ques_inds = _grid_qid_by_index_dict[q_id]
                        if len(_grid_ques_inds):
                            for _indx in sorted(_grid_ques_inds):
                                workbook.cell(row=row_number, column=column_number).value = \
                                    _ques_info['question_code'] + '#{}'.format(_indx)
                                workbook.merge_cells(start_row=row_number, end_row=row_number,
                                                     start_column=column_number,
                                                     end_column=column_number + _tot_grid_ques - 1)
                                for _qid in _grid_ques_ids:
                                    workbook.cell(row=row_number + 1, column=column_number).value = \
                                        _question_id_info_dict[_qid]['question_code']
                                    column_number += 1
                        else:
                            workbook.cell(row=row_number, column=column_number).value = _ques_info['question_code']
                            workbook.merge_cells(start_row=row_number, end_row=row_number,
                                                 start_column=column_number,
                                                 end_column=column_number + _tot_grid_ques - 1)
                            for _qid in _grid_ques_ids:
                                workbook.cell(row=row_number + 1, column=column_number).value = \
                                    _question_id_info_dict[_qid]['question_code']
                                column_number += 1
                    else:
                        if _ques_info['parent_question_code']:
                            workbook.cell(row=row_number, column=column_number).value = _ques_info[
                                'parent_question_code']
                            workbook.cell(row=row_number + 1, column=column_number).value = _ques_info['question_code']
                        else:
                            workbook.cell(row=row_number, column=column_number).value = _ques_info['question_code']
                        column_number += 1

            if nested_headers:
                row_number += 2
            else:
                row_number += 1

            for _sr_id, sr_info in _sr_ques_index_ans_dict.items():
                column_number = 1

                for h in _default_headers:
                    workbook.cell(row=row_number, column=column_number).value = survey_response_dict[_sr_id][h] \
                        if _sr_id in survey_response_dict and h in survey_response_dict[_sr_id] else ''
                    column_number += 1

                for _sec_info in _section_id_name_dict.values():
                    _questions = _sec_info['questions']
                    for q_id in _questions:
                        _ques_info = _question_id_info_dict[q_id]
                        if _ques_info['question_type'] == DynamicSurveyQuestionTypeEnum.DynamicGrid.value:
                            _grid_ques_ids = _child_grid_ques_dict[q_id]
                            _grid_ques_inds = _grid_qid_by_index_dict[q_id]
                            if len(_grid_ques_inds):
                                for ind in sorted(_grid_ques_inds):
                                    for _qid in _grid_ques_ids:
                                        workbook.cell(row=row_number, column=column_number).value = str(
                                            sr_info[_qid][ind]) \
                                            if _qid in sr_info and ind in sr_info[_qid] else ''
                                        column_number += 1
                            else:
                                for _qid in _grid_ques_ids:
                                    workbook.cell(row=row_number + 1, column=column_number).value = ''
                                    column_number += 1
                        else:
                            workbook.cell(row=row_number, column=column_number).value = sr_info[q_id][
                                -1] if q_id in sr_info else ''
                            column_number += 1
                row_number += 1
        return workbook, row_number

    @classmethod
    def prefetch_objects(cls):
        return ["location", "respondent_client"]

    @classmethod
    def prefetch_api_objects(cls):
        return ["location", "respondent_client", "created_by"]
