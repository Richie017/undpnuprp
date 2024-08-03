import functools
from collections import OrderedDict

from django.db.models import Prefetch
from django.utils.safestring import mark_safe

from blackwidow.core.generics.views.details_view import GenericDetailsView
from blackwidow.engine.decorators.utility import decorate
from blackwidow.engine.decorators.view_decorators import override_view
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models import PGPovertyIndex, Question, Answer
from undp_nuprp.survey.models.indicators.poverty_index_short_listed_grantee import PGPovertyIndexShortListedGrantee
from undp_nuprp.survey.models.response.question_response import QuestionResponse
from undp_nuprp.survey.models.response.survey_response import SurveyResponse

__author__ = 'Tareq'


class QuestionOperations:
    allowed_list = set()

    # skip_list = set()

    @staticmethod
    def get_sorted_questions_hash_map():
        questions = list(Question.objects.order_by('order').values_list('id', flat=True))
        hash_map = {q: i for i, q in enumerate(questions)}
        return hash_map

    def __init__(self):
        self.questions_hash = QuestionOperations.get_sorted_questions_hash_map()
        dependencies = {}
        qas = Question.objects.prefetch_related(Prefetch('answers', queryset=Answer.objects.only('id',
                                                                                                 'next_question_id'))
                                                ).all()
        for qa in qas:
            if qa.id not in dependencies:
                dependencies[qa.id] = {}
            for a in qa.answers.all():
                dependencies[qa.id][a.id] = a.next_question_id
        self.question_dependencies = dependencies
        self.allowed_list.add(Question.objects.order_by('order')[0].id)

    def _comparator(self, a, b):
        pos_a = self.questions_hash.get(a['question_id'], None)
        pos_b = self.questions_hash.get(b['question_id'], None)
        if pos_a and pos_b:
            return pos_a - pos_b
        return 0

    def sort_(self, obj):
        return sorted(obj, key=functools.cmp_to_key(self._comparator))

    def dependency_check(self, question):
        q = self.question_dependencies.get(question['question_id'], None)
        if q:
            next_ques = q.pop(question['answer_id'], None)
            ques_code = question['question__question_code']
            if ques_code == '6.2' and not (18 >= int(question['answer_text']) >= 5):
                self.allowed_list.add(Question.objects.filter(question_code='6.3').first().id)
            else:
                self.allowed_list.add(next_ques)
            # for k in q.keys():
            #     if q[k] not in self.allowed_list:
            #         self.skip_list.add(q[k])

    def not_allowed(self, question_id):
        return question_id not in self.allowed_list


@decorate(override_view(model=SurveyResponse, view=ViewActionEnum.Details))
class SurveyResponseDetailsView(GenericDetailsView):
    def get_context_data(self, **kwargs):
        context = super(SurveyResponseDetailsView, self).get_context_data(**kwargs)
        context['model_meta']['sections'] = self.prepare_survey_data()
        return context

    def get_template_names(self):
        return [
            "survey_response" + '/details.html'
        ]

    def prepare_mpi_indicators_data(self):
        mpi_indicators = PGPovertyIndex.objects.filter(
            primary_group_member_id=self.object.respondent_client_id).values(
            'index_no', 'index_name', 'index_description')
        indicators = list()
        indicators.append([mark_safe('<strong>Index No</strong>'), mark_safe('<strong>Index Detail</strong>'),
                           mark_safe('<strong>Score</strong>')])
        mpi_score = 0
        for i in mpi_indicators:
            if i['index_no'] < 5:
                _score = 16.7
            else:
                _score = 5.5
            mpi_score += _score
            indicators.append([i['index_no'], i['index_name'] + ' (' + i['index_description'] + ')', _score])
        indicators.append([mark_safe('<strong>Total</strong>'), '', round(mpi_score, 2)])
        return indicators

    def prepare_updated_mpi_indicators_data(self):
        mpi_indicators = PGPovertyIndexShortListedGrantee.objects.filter(
            survey_response_id=self.object.id).values(
            'index_no', 'index_name', 'index_description')
        indicators = list()
        indicators.append([mark_safe('<strong>Index No</strong>'), mark_safe('<strong>Index Detail</strong>'),
                           mark_safe('<strong>Score</strong>')])
        mpi_score = 0
        for i in mpi_indicators:
            if i['index_no'] < 5:
                _score = 16.7
            else:
                _score = 5.5
            mpi_score += _score
            indicators.append([i['index_no'], i['index_name'] + ' (' + i['index_description'] + ')', _score])
        indicators.append([mark_safe('<strong>Total</strong>'), '', round(mpi_score, 2)])
        return indicators

    def prepare_survey_data(self):
        question_responses = QuestionResponse.objects_include_versions.using(
            BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response_id=self.object.pk).order_by(
            'question__section__order', 'index', 'question__order', 'date_created').values(
            'question_id', 'question_text', 'answer_id', 'answer_text', 'index', 'section_response_id',
            'section_response__section__name', 'question__question_code', 'question__question_type', 'question__group')

        section_dict = OrderedDict()
        # # ordering the questions
        q_ops = QuestionOperations()
        question_responses = q_ops.sort_(question_responses)
        for question_response in question_responses:
            # check if question should be skipped
            q_ops.dependency_check(question_response)
            if q_ops.not_allowed(question_response['question_id']):
                continue

            question_id = question_response['question_id']
            question = question_response['question_text']
            answer = question_response['answer_text']
            code = question_response['question__question_code']
            section_id = question_response['section_response_id']
            question_type = question_response['question__question_type']
            index = question_response['index']
            if index:  # Need to group in section
                group_name = question_response['question__group'] + "#" + str(question_response['index'])
                if group_name in section_dict.keys():
                    if question_id in section_dict[group_name]['questions'].keys():
                        if question_type != QuestionTypeEnum.MultipleSelectInput.value:
                            section_dict[group_name]['questions'][question_id]['answer'] = answer
                        else:
                            section_dict[group_name]['questions'][question_id]['answer'] += ', ' + answer
                    else:
                        section_dict[group_name]['questions'][question_id] = {
                            'question': question, 'answer': answer, 'code': code
                        }
                else:
                    section_dict[group_name] = OrderedDict()
                    section_dict[group_name]['name'] = group_name
                    section_dict[group_name]['questions'] = OrderedDict()
                    section_dict[group_name]['questions'][question_id] = {
                        'question': question, 'answer': answer, 'code': code
                    }
            else:
                if section_id in section_dict:
                    if question_id in section_dict[section_id]['questions'].keys():
                        if question_type != QuestionTypeEnum.MultipleSelectInput.value:
                            section_dict[section_id]['questions'][question_id]['answer'] = answer
                        else:
                            section_dict[section_id]['questions'][question_id]['answer'] += ', ' + answer
                    else:
                        section_dict[section_id]['questions'][question_id] = {
                            'question': question, 'answer': answer, 'code': code
                        }
                else:
                    section_dict[section_id] = OrderedDict()
                    section_dict[section_id][
                        'name'] = question_response['section_response__section__name']
                    section_dict[section_id]['questions'] = OrderedDict()
                    section_dict[section_id]['questions'][question_id] = {
                        'question': question, 'answer': answer, 'code': code
                    }

        _oldest_response = SurveyResponse.objects_include_versions.filter(
            master_version_id=self.object.master_version_id).order_by('pk').first() if self.object.is_version else None

        _oldest_response_id = _oldest_response.pk if _oldest_response else 0

        # Initial MPI score segment
        if not self.object.is_version or _oldest_response_id == self.object.id:
            mpi_indicators = self.prepare_mpi_indicators_data()
            section_dict[998] = OrderedDict()
            section_dict[998]['name'] = 'MPI Indicator Score'
            section_dict[998]['questions'] = OrderedDict()
            k = 0
            for indicator in mpi_indicators:
                section_dict[998]['questions'][k] = {
                    'code': indicator[0], 'question': indicator[1], 'answer': indicator[2]
                }
                k += 1

        # Updated MPI score segment
        if not self.object.is_version and SurveyResponse.objects_include_versions.filter(
                master_version_id=self.object.id).count():
            updated_mpi_indicators = self.prepare_updated_mpi_indicators_data()
            section_dict[999] = OrderedDict()
            section_dict[998]['name'] = 'MPI Indicator Score(Initial)'
            section_dict[999]['name'] = 'MPI Indicator Score(Latest)'
            section_dict[999]['questions'] = OrderedDict()
            k = 0
            for indicator in updated_mpi_indicators:
                section_dict[999]['questions'][k] = {
                    'code': indicator[0], 'question': indicator[1], 'answer': indicator[2]
                }
                k += 1

        return list(section_dict.values())
