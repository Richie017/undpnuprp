from collections import OrderedDict
from datetime import datetime

from blackwidow.core.models import ImageFileObject
from blackwidow.core.models import Location
from dynamic_survey.enums.dynamic_survey_question_type_enum import DynamicSurveyQuestionTypeEnum
from dynamic_survey.models import DynamicQuestionResponse


class DynamicSurveyResponseViewMixin(object):
    def prepare_survey_data(self, is_print_view=False):
        """
        Prepares context data for the template

        :return: list of context data the template is going to receive
        :rtype: python list
        """
        question_responses = DynamicQuestionResponse.objects.filter(
            section_response__survey_response_id=self.object.pk).order_by(
            'question__order', 'date_created').values(
            'question_id', 'question_text', 'answer_text', 'section_response_id', 'section_response__section__name',
            'question__question_code', 'question__parent_id', 'question__parent__text', 'question__question_type',
            'photo__name', 'photo__file', 'photo__description', 'index',
            'photo__location__latitude', 'photo__location__longitude','photo__generation_time'
        )

        section_dict = OrderedDict()
        for question_response in question_responses:
            question_id = question_response['question_id']
            question = question_response['question_text']
            parent_question_id = question_response['question__parent_id']
            parent_question_text = question_response['question__parent__text']
            index = question_response['index']
            answer = question_response['answer_text']
            photo_name = question_response['photo__name']
            photo_file = question_response['photo__file']
            photo_description = question_response['photo__description']
            photo_description = photo_description if photo_description else 'N/A'
            photo_location_latitude = question_response['photo__location__latitude'] if question_response[
                'photo__location__latitude'] else 0
            photo_location_longitude = question_response['photo__location__longitude'] if question_response[
                'photo__location__longitude'] else 0
            photo_location = str(Location(latitude=photo_location_latitude, longitude=photo_location_longitude))
            photo_generation_time = question_response['photo__generation_time']
            if photo_generation_time:
                format = "%d/%m/%Y - %I:%M %p"
                photo_generation_time = datetime.fromtimestamp(photo_generation_time // 1000).strftime(format)
            else:
                photo_generation_time = 'N/A'
            image = ""
            if photo_name:
                if not is_print_view:
                    image = str(ImageFileObject(name=photo_name, file=photo_file))
                else:
                    image = ImageFileObject(name=photo_name, file=photo_file).image_html()
            else:
                photo_name = ""
            code = question_response['question__question_code']
            section_id = question_response['section_response_id']
            question_type = question_response['question__question_type']
            if section_id in section_dict:
                existing_id = question_id
                if question_type == DynamicSurveyQuestionTypeEnum.GridRow.value:
                    existing_id = parent_question_id
                elif index > 0:
                    existing_id = str(parent_question_id) + "." + str(index)

                if existing_id in section_dict[section_id]['questions'].keys():
                    if question_type == DynamicSurveyQuestionTypeEnum.ImageInput.value:
                        answer = image
                        section_dict[section_id]['questions'][str(question_id) + photo_name] = {
                            'question': question, 'answer': answer, 'code': code, 'question_type': question_type,
                            'photo_description': photo_description,
                            # 'photo_location': photo_location,
                            # 'photo_generation_time': photo_generation_time
                        }
                    elif index > 0:
                        if not question_id in section_dict[section_id]['questions'][existing_id]['grid_questions']:
                            section_dict[section_id]['questions'][existing_id]['grid_questions'][question_id] = {
                                'question': question, 'answer': answer, 'code': code, 'question_type': question_type

                            }
                        else:
                            section_dict[section_id]['questions'][existing_id]['grid_questions'][question_id][
                                'answer'] += ', ' + answer

                    elif question_type == DynamicSurveyQuestionTypeEnum.GridRow.value:
                        section_dict[section_id]['questions'][parent_question_id]['grid_questions'].append(
                            {
                                'question': question, 'answer': answer, 'code': code, 'question_type': question_type

                            }
                        )
                    elif question_type != DynamicSurveyQuestionTypeEnum.MultipleSelectInput.value:
                        section_dict[section_id]['questions'][question_id]['answer'] = answer
                    else:
                        section_dict[section_id]['questions'][question_id]['answer'] += ', ' + answer
                else:
                    if question_type == DynamicSurveyQuestionTypeEnum.ImageInput.value:
                        answer = image
                        section_dict[section_id]['questions'][str(question_id) + photo_name] = {
                            'question': question, 'answer': answer, 'code': code, 'question_type': question_type,
                            'photo_description': photo_description, 'photo_location': photo_location,
                            'photo_generation_time': photo_generation_time
                        }
                    elif index > 0:
                        section_dict[section_id]['questions'][str(parent_question_id) + "." + str(index)] = {
                            'question': parent_question_text + "#" + str(index), 'code': code,
                            'question_type': DynamicSurveyQuestionTypeEnum.DynamicGrid.value,
                            'grid_questions': OrderedDict()
                        }
                        section_dict[section_id]['questions'][str(parent_question_id) + "." + str(index)][
                            'grid_questions'][question_id] = {
                            'question': question, 'answer': answer, 'code': code, 'question_type': question_type

                        }


                    elif question_type == DynamicSurveyQuestionTypeEnum.GridRow.value:
                        section_dict[section_id]['questions'][parent_question_id] = {
                            'question': parent_question_text, 'code': code, 'question_type': question_type,
                            'grid_questions': list()
                        }
                        section_dict[section_id]['questions'][parent_question_id]['grid_questions'].append(
                            {
                                'question': question, 'answer': answer, 'code': code, 'question_type': question_type

                            }
                        )

                    else:
                        section_dict[section_id]['questions'][question_id] = {
                            'question': question, 'answer': answer, 'code': code, 'question_type': question_type
                        }
            else:
                section_dict[section_id] = OrderedDict()
                section_dict[section_id][
                    'name'] = question_response['section_response__section__name']
                section_dict[section_id]['questions'] = OrderedDict()
                if question_type == DynamicSurveyQuestionTypeEnum.ImageInput.value:
                    answer = image
                    section_dict[section_id]['questions'][str(question_id) + photo_name] = {
                        'question': question, 'answer': answer, 'code': code, 'question_type': question_type,
                        'photo_description': photo_description, 'photo_location': photo_location,
                        'photo_generation_time': photo_generation_time
                    }
                elif index > 0:
                    section_dict[section_id]['questions'][str(parent_question_id) + "." + str(index)] = {
                        'question': parent_question_text + "#" + str(index), 'code': code,
                        'question_type': DynamicSurveyQuestionTypeEnum.DynamicGrid.value,
                        'grid_questions': OrderedDict()
                    }
                    section_dict[section_id]['questions'][str(parent_question_id) + "." + str(index)][
                        'grid_questions'][question_id] = {
                        'question': question, 'answer': answer, 'code': code, 'question_type': question_type

                    }


                elif question_type == DynamicSurveyQuestionTypeEnum.GridRow.value:
                    section_dict[section_id]['questions'][parent_question_id] = {
                        'question': parent_question_text, 'code': code, 'question_type': question_type,
                        'grid_questions': list()
                    }
                    section_dict[section_id]['questions'][parent_question_id]['grid_questions'].append(
                        {
                            'question': question, 'answer': answer, 'code': code, 'question_type': question_type

                        }
                    )

                else:
                    section_dict[section_id]['questions'][question_id] = {
                        'question': question, 'answer': answer, 'code': code, 'question_type': question_type
                    }

        return list(section_dict.values())
