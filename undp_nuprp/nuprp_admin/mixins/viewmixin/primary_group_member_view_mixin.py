from collections import OrderedDict

from blackwidow.engine.routers.database_router import BWDatabaseRouter
from undp_nuprp.nuprp_admin.utils.enums.question_type_enum import QuestionTypeEnum
from undp_nuprp.survey.models import QuestionResponse


class PrimaryGroupMemberViewMixin(object):
    def prepare_survey_data(self):
        question_responses = QuestionResponse.objects.using(BWDatabaseRouter.get_read_database_name()).filter(
            section_response__survey_response__respondent_client_id=self.object.pk).order_by(
            'question__section__order', 'index', 'question__order', 'date_created').values(
            'question_id', 'question_text', 'answer_text', 'index', 'section_response_id',
            'section_response__section__name', 'question__question_code', 'question__question_type', 'question__group')

        section_dict = OrderedDict()
        for question_response in question_responses:
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

        return list(section_dict.values())
