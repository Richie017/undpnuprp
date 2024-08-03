""" This module consists of several functions that are used to save a survey draft to the database with the
    existing format of models.
 """
import os

from blackwidow.core.models.common.choice_options import ApprovalStatus
from blackwidow.core.models import ErrorLog, ApprovalAction
from crequest.middleware import CrequestMiddleware
from django.conf import settings
from django.contrib import messages
from django.db import transaction

from dynamic_survey.enums.dynamic_survey_question_type_enum import DynamicSurveyQuestionTypeEnum
from dynamic_survey.models.entity.dynamic_answer import DynamicAnswer
from dynamic_survey.models.entity.dynamic_question import DynamicQuestion
from dynamic_survey.models.entity.dynamic_section import DynamicSection
from dynamic_survey.utils.dynamic_survey.survey_parser import ParseSurvey


def save_full_parsed_survey(survey, survey_draft):
    """
    This function takes in the survey as `ParseSurvey` object. From that survey, the sections, questions
    and answers are saved to corresponding models.

    :param survey: the parsed survey object from ParseSurvey class
    :type survey: ParseSurvey object
    :param survey_draft: survey_draft model object
    :type survey_draft: DynamicSurvey object
    :return: True or False based on the success of saving all items in corresponding mdoels
    :rtype: bool
    """
    # Dividing the survey into list of sections

    saved_survey = survey_draft

    # From the ParseSurvey object getting the `group_wise_survey` attribute
    sections = survey.group_wise_survey

    saved_section = None
    question_order = 1
    answer_order = 1
    for order, section in enumerate(sections):
        saved_section = save_parsed_sections(section, saved_section, order + 1, saved_survey)
        question_list = section.question_list
        for question in question_list:
            saved_question = save_parsed_questions(question, saved_survey, saved_section, question_order)
            question_order += 1
    return True


def save_parsed_sections(section, parent_section, section_order, saved_survey):
    """
    This function saves the section according to the given parameters.

    :param section: section we want to save in the model
    :type section: Section object
    :param parent_section: parent section of the current section
    :type parent_section: Section object
    :param section_order: order of the section
    :type section_order: integer
    :param saved_survey: the survey object that the section belongs to
    :type saved_survey: DynamicSurvey object
    :return: Either None or saved_section
    :rtype: None or Section
    """
    section_params = dict(
        survey=saved_survey, name=section.label,
        name_bn=getattr(section, settings.SECONDARY_LANGUAGE),
        order=section_order
    )
    if parent_section:
        section_params['parent'] = parent_section
    # Ignoring the None values because they create objects with null value in database
    # if they are ignored database will save the default value in that column
    section_params = {k: v for k, v in section_params.items() if v is not None}
    saved_section = DynamicSection.objects.create(**section_params)
    return saved_section


def save_parsed_questions(question, saved_survey, saved_section, question_order, parent_question=None):
    """
    This function saves the questions according to the given parameters

    :param question: question object that is needed to be saved
    :type question: Question object
    :param saved_section: the section that the question belongs to
    :type saved_section: Section object
    :param question_order: order of the question
    :type question_order: integer
    :param parent_question: parent question object
    :type parent_question: question object
    :return: None or the saved_question
    :rtype: None or Question object
    """
    question_params = dict(
        section=saved_section, text=question.label,
        text_bn=getattr(question, settings.SECONDARY_LANGUAGE), order=question_order,
        question_type=DynamicSurveyQuestionTypeEnum.get_question_type_from_raw(question.type),
        question_code=str(question.question_code) \
            if hasattr(question, 'question_code') and question.question_code else '',
        is_required=True if str(question.required) == 'true' else False,
        assigned_code=question.assigned_code
    )
    if parent_question:
        question_params['parent'] = parent_question

    elif question.parent_list:
        # TODO Here We are assuming a question's parent can only be one question
        # TODO and the dependent question lies within the section it must be changed
        parent_question = DynamicQuestion.objects.filter(assigned_code=question.parent_list[0].assigned_code,
                                                         text=question.parent_list[0].label,
                                                         section__survey=saved_survey)
        if not parent_question.exists():
            raise Exception('Cant find parent question in database')
        if parent_question.count() > 1:
            raise Exception('Question with same code and label already exists in the current survey')
        parent_question = parent_question.first()
        # Taking codes of all the parent questions
        parent_codes = [(parent.assigned_code, parent.label) for parent in question.parent_list]
        # Finding out those questions from database
        parent_questions = []
        for parent_code in parent_codes:
            _current_parent = DynamicQuestion.objects.filter(assigned_code=parent_code[0], text=parent_code[1],
                                                             section__survey=saved_survey)
            if not _current_parent.exists():
                raise Exception('Cant find parent question in database')
            if _current_parent.count() > 1:
                raise Exception('Question with same code and label already exists in the current survey')
            _current_parent = _current_parent.first()
            parent_questions.append(_current_parent)

        # finding out there primary keys
        parent_ids = [parent.pk for parent in parent_questions]
        # dependency structure is getting replaced by primary key in the place of question code
        question.dependency_string = replace_dependency_structure_with_id(question, parent_ids)
        question_params['parent'] = parent_question

    try:
        repeat_time = int(question.repeat_time)
    except:
        repeat_time = -1
    # This is the new parameter list for each question
    new_params = dict(constraint=question.constraint, constraint_message=question.constraint_message,
                      default=question.default, hint=question.hint, dependency_string=question.dependency_string,
                      count_as_a_parent=question.count_as_a_parent,
                      repeat_time=repeat_time,
                      minimum_image_number=question.minimum_image_number
                      if hasattr(question, 'minimum_image_number') and question.minimum_image_number else 0,
                      instruction=question.instruction
                      if hasattr(question, 'instruction') and question.instruction else "",
                      translated_instruction=question.translated_instruction
                      if hasattr(question, 'translated_instruction') and question.translated_instruction else "",

                      )

    # Changing the dependency structure with id instead of code
    final_params = {}
    final_params.update(question_params)
    final_params.update(new_params)
    # Ignoring the None values because they create objects with null value in database
    # if they are ignored database will save the default value in that column
    final_params = {k: v for k, v in final_params.items() if v is not None}
    saved_question = DynamicQuestion.objects.create(**final_params)
    # TODO manual handling of option list needs to be fixed
    option_list = question.option_list
    if option_list is None:
        option_list = [("", ""), ]
    else:
        option_list = option_list.values()
    answer_order = 1
    for option, answer_code, answer_type in zip(option_list, question.answer_code_list,
                                                question.answer_type_list):
        option_english = option[0]
        option_secondary_lang = option[1] if option[1] else ""
        saved_answer = save_parsed_answers(answer_code, answer_type, answer_order, option_english,
                                           option_secondary_lang, saved_question)

        answer_order += 1

    # If the saved question is a grid question then recursively save the child questions
    if saved_question and saved_question.question_type == DynamicSurveyQuestionTypeEnum.GridInput.value or DynamicSurveyQuestionTypeEnum.DynamicGrid.value:
        if question.grid_questions:
            for index, child_question in enumerate(question.grid_questions):
                save_parsed_questions(child_question, saved_survey, saved_section, index + 1,
                                      parent_question=saved_question)

    return saved_question


def save_parsed_answers(answer_code, answer_type, order, text, text_bn, saved_question):
    """
    This function saves the answers according to the given parameters

    :param answer_code: code of the current answer
    :type answer_code: str
    :param answer_type: type of the current answer
    :type answer_type: str
    :param order: order of the answer
    :type order: integer
    :param text: text of the answer (empty string for which there is no answer choice)
    :type text: str
    :param text_bn: text of the answer (empty string for which there is no answer choice)
    :type text: str
    :param saved_question: the question object that the answer belongs to
    :type saved_question: Question object
    :return: None or the saved_answer object
    :rtype: None or Answer object
    """
    # https://redmine.field.buzz/issues/9734
    if str(text_bn).lower() == 'empty':
        text_bn = ""
    saved_answer = DynamicAnswer.objects.create(question=saved_question,
                                                answer_code=answer_code,
                                                answer_type=answer_type,
                                                order=order, text=text, text_bn=text_bn)
    return saved_answer


def replace_dependency_structure_with_id(question, parent_ids):
    """
    This function creates the dependency string with the ids of the parent question

    :param question: the question object
    :type question: Question object
    :param parent_ids: primary keys of parent questions of the current question
    :type parent_ids: list of integer
    :return: dependency string
    :rtype: str
    """
    string = ""
    for id_, relation in zip(parent_ids, question.parent_relation_list):
        string += str(id_) + " "
        string += relation.symbol + " "
        string += relation.value + " "
        if relation.log_op:
            string += relation.log_op + " "
    return string.strip()


def parse_survey(survey_draft):
    """
    This function takes the survey draft id as it's parameter.
    1. Takes survey_draft object as parameter
    2. Converts it into an internal xls representation.
    3. Create an in memory excel file with xls contents
    4. Parse the excel with the help of ParseSurvey class
    5. Save the parsed survey draft to database
    6. Finally remove the in memory excel file
    :param survey_draft: The specific survey_draft object obtained from database that we want to parse
    :return a dictionary containing 'bool' as key which is either True or False which indicates if the survey is
    parsed without any error or not. Another key of the dictionary is `error_message` which contains the error message
    """

    contents = survey_draft.to_xls()
    temporary_location = "testout.xls"
    with open(temporary_location, 'wb') as out:
        out.write(contents.read())
    try:
        survey = ParseSurvey(temporary_location)
    except Exception as e:
        ErrorLog.log(exp=e)
        error_message = str(e) + ". " + "The Survey Cannot be parsed, Please Check the designed survey again."
        os.remove(temporary_location)
        ApprovalAction.objects.filter(object_id=survey_draft.id, status=ApprovalStatus.Approved.value,
                                      model_name=survey_draft.__class__.__name__).order_by(
            'date_created').last().delete()
        current_request = CrequestMiddleware.get_request()
        if current_request:
            messages.error(current_request, error_message)
        return False
    if not survey.is_valid_survey[0]:
        os.remove(temporary_location)
        error_message = "The questions are not divided into groups properly. Question code '{}' with label '{}' does not belong to any group.".format(
            survey.is_valid_survey[1]['question_code'], survey.is_valid_survey[1]['label'])
        ApprovalAction.objects.filter(object_id=survey_draft.id, status=ApprovalStatus.Approved.value,
                                      model_name=survey_draft.__class__.__name__).order_by(
            'date_created').last().delete()
        current_request = CrequestMiddleware.get_request()
        if current_request:
            messages.error(current_request, error_message)

        return False

    os.remove(temporary_location)
    try:
        with transaction.atomic():
            save_full_parsed_survey(survey, survey_draft)
    except Exception as e:
        ErrorLog.log(e)
        error_message = str(e) + '. ' + 'The Survey Cannot be Saved in Database Properly'
        ApprovalAction.objects.filter(object_id=survey_draft.id, status=ApprovalStatus.Approved.value,
                                      model_name=survey_draft.__class__.__name__).order_by(
            'date_created').last().delete()

        current_request = CrequestMiddleware.get_request()
        if current_request:
            messages.error(current_request, error_message)
        return False
    return True
