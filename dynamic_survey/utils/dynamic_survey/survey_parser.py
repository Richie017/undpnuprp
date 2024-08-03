"""
This module combined with following classes parses the Survey Draft which is designed by the survey designer.
"""
import re
import uuid
from collections import OrderedDict

import xlrd
from django.conf import settings

from dynamic_survey.enums.dynamic_survey_answer_type_enum import DynamicSurveyAnswerTypeEnum
from dynamic_survey.enums.xlform_question_type_enum import XLFormQuestionTypeEnum


class DealWithXlsSurvey:
    """
    This class mainly extracts the settings and answer choices information from the xls representation of the
    survey draft.

    """

    def __init__(self, file_name):
        """
        Firstly the xls file (survey draft) is opened as a workbook using xlrd module and saved as an attribute of the object.
        Then different page names of the excel file is saved as another attribute of the object.


        :param file_name: the filename of the ``DynamicSurvey`` object that is represented as a xls file
        :type file_name: xls file object
        """
        self.workbook = xlrd.open_workbook(file_name)
        self.sheet_names = self.workbook.sheet_names()

    def get_choice_dict(self):
        """
        If there is a choices sheet in the xls file then it's opened and a dictionary is created.
        The keys of the dictionary are the distinct group codes.
        For each key an empty dictionary is associated as the value.
        The empty inner dictionary is populated with {choice_name:choice_label} pairs having same group code.
        If there is no choices sheet in the xls ``None`` is returned.
        All the dictionaries are ``OrderedDict`` objects.


        :return: returns an ``OrderedDict`` object. Each key of the dictionary is a distinct group code and as the value
        of each key another ``OrderedDict`` object is saved. The inner saved dictionary holds choice_names as keys and
        choice_labels as values.
        :rtype: ``OrderedDict``  object containg ``OrderedDict`` objects
        """
        if "choices" in self.sheet_names:
            choices_sheet = self.workbook.sheet_by_name("choices")
            choice_dict = self.get_distinct_choice_codes(choices_sheet)
            column_names = [str(i.value).strip() for i in choices_sheet.row(0)]
            # TODO where is the try catch
            label_index = column_names.index("label")
            name_index = column_names.index("name")
            list_name_index = column_names.index("list name")
            secondary_lang_index = column_names.index(settings.SECONDARY_LANGUAGE) \
                if settings.SECONDARY_LANGUAGE in column_names else -1
            # order_index = column_names.index("order")
            for row in range(1, choices_sheet.nrows):
                choice_label = str(choices_sheet.cell(row, label_index).value).strip()
                choice_name = str(choices_sheet.cell(row, name_index).value).strip()
                choice_list_name = str(choices_sheet.cell(row, list_name_index).value).strip()
                choice_secondary_lang = ""
                if secondary_lang_index is not None and secondary_lang_index >= 0:
                    choice_secondary_lang = str(choices_sheet.cell(row, secondary_lang_index).value).strip()
                choice_dict[choice_list_name][choice_name] = choice_label, choice_secondary_lang
            return choice_dict
        else:
            return None

    def get_settings_dict(self):
        """
        It opens the settings sheet of the xls file and populates an ``OrderedDict`` object
        with meta information:
        1.form_title  (must have to be in the xls file)
        2.form_id   (must have to be in the xls file)
        3.style (optional, set to ``None`` if there isn't any)
        4.version (optional, set to ``None`` if there isn't any)

        :return: returns an ``OrderedDict`` object containing meta information
        :rtype: ``OrderedDict`` object
        """
        if "settings" in self.sheet_names:
            settings_sheet = self.workbook.sheet_by_name("settings")
            settings_dict = OrderedDict()
            column_names = [str(i.value).strip() for i in settings_sheet.row(0)]
            form_title_index = column_names.index("form_title")
            form_id_index = column_names.index("form_id")
            settings_dict['form_title'] = str(settings_sheet.cell(1, form_title_index).value).strip()
            settings_dict['form_id'] = str(settings_sheet.cell(1, form_id_index).value).strip()
            if "style" in column_names:
                style_index = column_names.index("style")
                settings_dict['style'] = str(settings_sheet.cell(1, style_index).value).strip()
            else:
                settings_dict['style'] = None

            if "version" in column_names:
                version_index = column_names.index("version")
                settings_dict['version'] = str(settings_sheet.cell(1, version_index).value).strip()
            else:
                settings_dict['version'] = None

            return settings_dict
        else:
            return None

    @staticmethod
    def get_distinct_choice_codes(sheet):
        """
        This method is better understood from the params and return descriptions.

        :param sheet: receives a sheet of the xls file which is opened as a workbook of xlrd module
        :type sheet: sheet type object got from workbook.sheet_by_name(sheet_name) of xlrd module
        :return: returns an ``OrderedDict`` object. Each key of the dictionary is a distinct group code and as the value
        of each key an empty ``OrderedDict`` object is saved.
        :rtype: ``OrderedDict``  object containg empty ``OrderedDict`` objects
        """
        choice_dict = OrderedDict()

        column_names = [str(i.value).strip() for i in sheet.row(0)]
        list_name_index = column_names.index("list name")

        code_list = [str(i.value).strip() for i in sheet.col(list_name_index)[1:]]
        distinct_code_list = sorted(set(code_list), key=code_list.index)
        for key in distinct_code_list:
            choice_dict[key] = OrderedDict()
        return choice_dict


class SurveyRow:
    """
    This class represents each row of the generated excel file from
     designed survey. each column of a row can be accessed through the name
     of the column name.
     It also tracks the list of options if it's a choice question
     It counts the number of depenedent parent questions
    """

    def __init__(self, file_name, **kwargs):
        """
        It gets the keyword arguments from the row of the xls file and updates correspnding instance attributes
        first.
        Then it updates the other attributes to None if they don't exist in the xls file.
        Then it does some initialization.
        If it's a choice question then the option_list is set accordingly otherwise option_list is set to None.

        :param file_name: the filename of the ``DynamicSurvey`` object that is represented as a xls file
        :type file_name: xls file object
        :param kwargs: variable number of attributes each row is going to have
        :type kwargs: variable number of keyword arguments
        """
        self.file_name = file_name
        self.repeat_time = -1
        self.code = None
        self.assigned_code = uuid.uuid4().hex
        self.update_none_type_attributes()
        self.grid_questions = list()
        self.parent_counter = 0  # This attribute is only for assigning code to the children questions
        self.count_as_a_parent = 0  # This attribute defines how many times this question has come as a dependency
        self.parent_list = []
        # self.child_list = []
        self.parent_relation_list = []
        # self.child_realtion_list = []
        self.__dict__.update(kwargs)
        dealer = DealWithXlsSurvey(file_name)
        # TODO fix the options according to order if there is any
        if str(self.type).startswith("select_") or str(self.type).startswith("free_") or str(self.type).startswith(
                "rank_"):
            index = str(self.type).index(" ") + 1
            code = str(self.type)[index:]
            self.option_list = dealer.get_choice_dict()[code]
        elif str(self.type).startswith(XLFormQuestionTypeEnum.GridInput.value):
            code = self.__dict__.get(XLFormQuestionTypeEnum.GridCode.value)
            self.option_list = dealer.get_choice_dict().get(code)
        elif str(self.type).startswith(XLFormQuestionTypeEnum.DynamicGrid.value):
            self.option_list = None
            grid_option_separator = "#|"
            grid_options = self.grid_options if hasattr(self, 'grid_options') and self.grid_options else None
            grid_translated_options = self.grid_translated_options \
                if hasattr(self, 'grid_translated_options') and self.grid_translated_options else None

            if grid_options:
                grid_option_list = str(grid_options).split(grid_option_separator)
                grid_translation_list = str(grid_translated_options).split(grid_option_separator)
                choice_dict = OrderedDict()
                for option in grid_option_list:
                    option = option.strip()
                    choice_dict[option] = option, ""
                for option, option_translated in zip(grid_option_list, grid_translation_list):
                    option = option.strip()
                    option_translated = option_translated.strip()
                    choice_dict[option] = option, option_translated
                self.option_list = choice_dict
        else:
            self.option_list = None
        self.answer_code_list = []
        self.answer_type_list = []
        self.dependency_string = None

    def update_none_type_attributes(self):
        """
        If some attributes that are in the model for questions but is not generated in xls file then
        they are set to None here. If these attributes are created in the xls file they get populated.
        Otherwise they are set to None here.

        :return: None
        :rtype: None
        """
        if not hasattr(self, 'hint'):
            self.hint = None
        if not hasattr(self, 'default'):
            self.default = None

        if not hasattr(self, 'constraint'):
            self.constraint = None

        if not hasattr(self, 'constraint_message'):
            self.constraint_message = None

        if not hasattr(self, 'dependency_string'):
            self.dependency_string = None

        if not hasattr(self, 'relevant'):
            self.relevant = None

        if not hasattr(self, settings.SECONDARY_LANGUAGE):
            setattr(self, settings.SECONDARY_LANGUAGE, None)

        if not hasattr(self, 'question_code'):
            self.question_code = None

    def create_answer_code(self):
        """
        There are two scenarios.
        Scenario 1: This is not a choice question. So the answer gets saved as ``question_code.1``
        Scenario 2: This is a choice question. So answer codes get incremented by 1 for each option
        it has in it's ``option_list`` attribute.

        Then the answer type is created by calling ``create_answer_type`` method.
        And also ``create_dependency_structure`` method is called to prepare the string representation of
        the question's dependency.

        :return: None
        :rtype: None
        """
        if hasattr(self, "question_code") and self.question_code:
            question_prefix_code = self.question_code
        else:
            question_prefix_code = self.code
        if self.option_list == None:
            self.answer_code_list.append(question_prefix_code + "." + "1")
        else:
            for index in range(len(self.option_list)):
                self.answer_code_list.append(question_prefix_code + "." + str(index + 1))
        self.create_answer_type()
        self.create_dependency_structure()

    def create_dependency_structure(self):
        """
        This method creates a string representation of the dependency structure with question code
        and sets the dependency string as an instance attribute(dependency_string) of the object.
        If there is no dependency ``self.dependency_string`` is set to ``None``.
        Otherwise from the list of parent questions and list of relation with those parents
        a simple string representation is formed. Example: ``1.1 > 18 or 1.1.1 > 20000``

        :return: None
        :rtype: None
        """
        if not self.parent_list:
            self.dependency_string = None
        else:
            string = ""
            for question, relation in zip(self.parent_list, self.parent_relation_list):
                relation_label = None
                dealer = DealWithXlsSurvey(self.file_name)
                if str(question.type).startswith("select_") or str(question.type).startswith("free_") or str(
                        question.type).startswith("rank_"):
                    index = str(question.type).index(" ") + 1
                    code = str(question.type)[index:]
                    option_list = dealer.get_choice_dict().get(code, None)
                    option_list_labels = {k: v[0] for k, v in option_list.items()}
                    if option_list is not None:
                        matched_patterns = re.findall(r"'(?P<dummy>.*)'", relation.value)
                        if matched_patterns:
                            relation_label = option_list_labels.get(matched_patterns[0], None)
                string += question.code + " "
                string += relation.symbol + " "
                if relation_label is not None:
                    relation.value = "'" + relation_label + "'"
                    string += "'" + relation_label + "'" + " "
                else:
                    string += relation.value + " "
                if relation.log_op:
                    string += relation.log_op + " "
            self.dependency_string = string.strip()

    def create_answer_type(self):
        """
        This class is more like an enumerator for existing API. The type attribute which is got
        from the xls file itself is converted to ``answer_types`` as mobile version recognises the types.

        N.B: Currently this are the data types that are supported by the survey module. If any upgrade is needed
        here the changes should be reflected.
        :return: None
        :rtype: None
        """
        if str(self.type).startswith(XLFormQuestionTypeEnum.TextInput.value):
            self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.TextInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.NumberInput.value):
            self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.NumberInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.PhoneNumberInput.value):
            self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.PhoneNumberInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.ImageInput.value):
            self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.ImageInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.DateInput.value):
            self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.DateInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.SingleSelectInput.value):
            for i in self.answer_code_list:
                self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.SingleSelectInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.MultipleSelectInput.value):
            for i in self.answer_code_list:
                self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.MultipleSelectInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.EditableSelectInput.value):
            for i in range(len(self.answer_code_list) - 1):
                self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.SingleSelectInput.value)
            self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.OtherOption.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.GridInput.value):
            for i in self.answer_code_list:
                self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.GridInput.value)

        elif str(self.type).startswith(XLFormQuestionTypeEnum.DynamicGrid.value):
            if self.option_list is None:
                self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.DynamicGrid.value)
            else:
                for i in self.answer_code_list:
                    self.answer_type_list.append(DynamicSurveyAnswerTypeEnum.DynamicGrid.value)

        else:
            # TODO Exception case needs to be handled
            raise Exception()

    def __str__(self):
        """
        Custom string representation of the class.

        :return: returns the string representation
        :rtype: string
        """

        string = "Question Code: {}\n".format(self.code)
        string += "Question Label: {}\n".format(self.label)
        string += "Question Hint: {}\n".format(self.hint)
        string += "Question Constraint: {}\n".format(self.constraint)
        string += "Question Default: {}\n".format(self.default)
        string += "Question Relevant: {}\n".format(self.relevant)
        string += "Dependency String: {}\n".format(self.dependency_string)

        string += "Parent List: {}\n".format(self.parent_list)
        string += "Relation of Parent: {}\n".format(str([str(i) for i in self.parent_relation_list]))

        #
        string += "Parent Counter: {}\n".format(self.parent_counter)
        string += "Option List: {}\n".format(self.option_list)
        string += "Answer Code List: {}\n".format(self.answer_code_list)
        string += "Answer Type List: {}\n".format(self.answer_type_list)

        # return "Question: {}, Code: {}, Option List: {}".format(self.label, self.code, self.option_list)
        # return str(self.__dict__)
        return string

    def __repr__(self):
        """
        Custom repr representation of the class.

        :return: returns the string representation
        :rtype: string
        """

        return self.__str__()


class Relation:
    """
    This class holds the dependency among the questions. The 3 attributes are:
      1. symbol --> the comparison operator (e.g. >,<,=,e.t.c)
      2. value --> the actual value
      3. log_op --> the logical operator (e.g. and,ot)
    """

    def __init__(self, symbol, value):
        """
        Basic initialization method. ``log_op`` is set dynamically.

        :param symbol: the comparison operator (e.g. >,<,=,e.t.c)
        :type symbol: string
        :param value: the actual value
        :type value: string
        """
        self.symbol = symbol
        self.value = value
        self.log_op = None

    def __str__(self):
        """
        Custom string representation of the class.

        :return: returns the string representation
        :rtype: string
        """

        return "Symbol: {}, Value: {}, Logical Operator: {}".format(self.symbol, self.value, self.log_op)

    def __repr__(self):
        """
        Custom repr representation of the class.

        :return: returns the string representation
        :rtype: string
        """

        return self.__str__()


class SurveyGroup:
    """
    This class basically keeps a list of questions with a specific group.
    """

    def __init__(self):
        """
        Initially all instance attributes are set on None or empty. Eventually they get populated when
        the survey is divided into groups in ``ParseSurvey`` class ``__init__`` method
        (specifically divide_into_groups method).
        """
        self.id = None
        self.code = None
        self.label = None
        setattr(self, settings.SECONDARY_LANGUAGE, None)
        self.question_list = []

    def __str__(self):
        """
        Custom string representation of the class.

        :return: returns the string representation
        :rtype: string
        """
        string = "Group ID: {} ,Group label: {}, Group Code: {}\n\n".format(self.id, self.label, self.code)
        for row in self.question_list:
            string += str(row) + "\n" * 2
        string += "##" * 50 + "\n" * 5
        return string


class ParseSurvey:
    """
    This class is the main class that parses the xls file. The detailed procedure of this class's workflow
    can be easily understood from the following method's docstrings.
    """

    def __init__(self, file_name):
        """
         This init method takes and saves the xls filename, opens and saves it as a workbook.
         From the workbook it opens and saves the main survey sheet.
         From the survey sheet it saves the column names of the xls file in ``survey_params`` attribute.
         Then the validity of the survey is checked.
         if it's valid then the full survey is saved in ``full_survey`` attribute.
         From the full survey, group wise survey is saved in ``group_wise_survey`` attribute.
         Also meta information of the survey is saved in ``settings_dict`` attribute with the help of
         ``DealWithXlsSurvey`` class.


        :param file_name: the filename of the ``DynamicSurvey`` object that is represented as a xls file
        :type file_name: xls file object
        """
        self.file_name = file_name
        self.survey_metadata = []
        self.workbook = xlrd.open_workbook(self.file_name)
        self.survey_sheet = self.workbook.sheet_by_name("survey")
        self.survey_params = [str(i.value).strip() for i in self.survey_sheet.row(0)]
        self.is_valid_survey = self.check_validity()
        if self.is_valid_survey:
            self.full_survey = self.get_full_survey()
            self.group_wise_survey = self.divide_into_groups()
            dealer = DealWithXlsSurvey(file_name)
            self.settings_dict = dealer.get_settings_dict()

    def check_validity(self):
        """
        This method only checks if all the survey questions are well formed in groups.


        :return: returns a tuple containing either true or false as the first element based on the validity of
        the survey and second element of the tuple is the error message
        :rtype: tuple
        """
        survey_sheet_metadata_types = (
            'start', 'end', 'today', 'username', 'simserial', 'subscriberid', 'deviceid', 'phonenumber')
        survey_dict = OrderedDict()
        valid_flag = 0
        question_number = 0
        group_number = 0
        for i in range(1, self.survey_sheet.nrows):
            current_row = [str(i.value).strip() for i in self.survey_sheet.row(i)]
            for index, value in enumerate(current_row):
                survey_dict[self.survey_params[index]] = value
            if survey_dict['type'] in survey_sheet_metadata_types:
                continue
            else:
                if survey_dict['type'] == "begin group":
                    valid_flag = 1
                    group_number += 1
                elif survey_dict['type'] == "end group":
                    valid_flag = 0
                else:
                    question_number += 1
                    if valid_flag == 0:
                        content_dict = {'label': survey_dict['label'], 'question_number': question_number,
                                        'group_number': group_number,
                                        'question_code': survey_dict.get('question_code', "")}
                        return False, content_dict
        return True, {}

    def get_full_survey(self):
        """
        Each row except the first one of the main survey sheet of the xls file saved as a SurveyRow and the whole
        list is returned. But only the rows having ``type`` containing in ``survey_sheet_metadata_types`` are saved in
        ``self.survey_metadata``.

        :return: returns a list of ``SurveyRow`` objects
        :rtype: python list of ``SurveyRow`` objects
        """
        survey_sheet_metadata_types = (
            'start', 'end', 'today', 'username', 'simserial', 'subscriberid', 'deviceid', 'phonenumber')

        survey_row_list = []
        survey_dict = OrderedDict()
        dynamic_grid_stack = list()
        # This variable keeps track of how much deep we are inside groups
        group_counter = 0
        for i in range(1, self.survey_sheet.nrows):
            current_row = [str(i.value).strip() for i in self.survey_sheet.row(i)]
            for index, value in enumerate(current_row):
                value = str(value).strip()
                value = value.replace("\\n", "")
                if self.survey_params[index] == "relevant":
                    pattern1 = re.compile(r"(?P<dummy>not\(selected\()(?P<id>\$\{\w+\}),\s*(?P<value>'\w+')\)\)")
                    pattern2 = re.compile(r"(?P<dummy>selected\()(?P<id>\$\{\w+\}),\s*(?P<value>'\w+')\)")

                    searched_pattern_1 = pattern1.search(value)
                    if searched_pattern_1:
                        value = pattern1.sub(r'\g<id> != \g<value>', value)

                    searched_pattern_2 = pattern2.search(value)
                    if searched_pattern_2:
                        value = pattern2.sub(r'\g<id> = \g<value>', value)
                survey_dict[self.survey_params[index]] = value
            # TODO This should be consulted and changed accordingly
            if survey_dict['type'] in survey_sheet_metadata_types:
                # TODO currently only the type is saved but full row is not saved. NB current implementation of dkobo survey doesn't populate any other column except 'type' column
                self.survey_metadata.append(survey_dict['type'])
                continue

            # If this is the start of dynamic grid question push this to a stack
            if survey_dict['type'] == XLFormQuestionTypeEnum.BeginGroup.value:
                group_counter += 1
                # This indicates there is a repeat time connected to current group so it might be a grid question
                # If we this begin group is inside another group then we are sure this is dynamic grid
                if group_counter > 1:
                    repeat_time = survey_dict.get('repeat_time')
                    survey_dict["repeat_time"] = repeat_time
                    survey_dict["type"] = XLFormQuestionTypeEnum.DynamicGrid.value
                    current_dynamic_grid_question = SurveyRow(self.file_name, **survey_dict)
                    dynamic_grid_stack.append(current_dynamic_grid_question)
                    continue

            if survey_dict['type'] == XLFormQuestionTypeEnum.EndGroup.value:
                group_counter -= 1
                if len(dynamic_grid_stack) > 0:
                    current_dynamic_grid_question = dynamic_grid_stack.pop()
                    self.create_question_code(current_dynamic_grid_question.grid_questions)
                    survey_row_list.append(current_dynamic_grid_question)
                    continue
            # Start of handling matrix/score type question
            if survey_dict['type'] == XLFormQuestionTypeEnum.GridInput.value:
                current_grid_question = SurveyRow(self.file_name, **survey_dict)
                continue

            elif survey_dict['type'] == XLFormQuestionTypeEnum.GridRow.value:
                current_grid_question.grid_questions.append(SurveyRow(self.file_name, **survey_dict))
                continue

            elif survey_dict['type'] == XLFormQuestionTypeEnum.GridInputEnd.value:
                if len(dynamic_grid_stack) > 0:
                    dynamic_grid_stack[-1].grid_questions.append(current_grid_question)
                else:
                    survey_row_list.append(current_grid_question)
                continue
            # End of handling matrix/score type question

            # This row belongs to dynamic grid so put it inside the dynamic grid
            if len(dynamic_grid_stack) > 0:
                dynamic_grid_stack[-1].grid_questions.append(SurveyRow(self.file_name, **survey_dict))
            # This is an usual row so push it to survey list
            else:
                survey_row_list.append(SurveyRow(self.file_name, **survey_dict))
        return survey_row_list

    def divide_into_groups(self):
        """
        This method starts with the ``full_survey`` and divides the survey into appropriate ``DynamicSurveyGroup``
        objects. Each ``DynamicSurveyGroup`` object contains the following things:
        1. code (name from the xls file)
        2. id (group counter)
        3. label (label of the group)
        4. question list (``SurveyRow`` list)


        :return: returns a list of ``DynamicSurveyGroup`` objects
        :rtype: python list of ``DynamicSurveyGroup`` objects
        """
        survey_group_list = []
        survey_row_list = []
        group_counter = 0
        # row_counter = 0
        for row in self.full_survey:
            if row.type == "begin group":
                survey_group_list.append(SurveyGroup())
                survey_group_list[-1].code = row.name
                group_counter += 1
                survey_group_list[-1].id = str(group_counter)
                survey_group_list[-1].label = row.label
                setattr(survey_group_list[-1], settings.SECONDARY_LANGUAGE,
                        getattr(row, settings.SECONDARY_LANGUAGE))

                continue
            if row.type == 'note':
                continue

            if row.type == "end group":
                survey_group_list[-1].question_list = survey_row_list[:]
                survey_row_list = []
                # row_counter = 0
                self.create_question_code(survey_group_list[-1].question_list, group_counter)
                continue

            survey_row_list.append(row)
        return survey_group_list

    def create_question_code(self, question_list, group_counter=None):
        """
        The code numbers for a list of questions under a specific group is generated by this method based on dependency
         on other questions. There can be two scenarios:
        1. The question is not dependent to anyone
        2. The question may be dependent to other questions.
        Scenario 1: The question's code will be incremented each time by 1 with group number prefix
        Scenario 2: The question's code will be incremented each time by 1 with depenedent question number prefix

        Finally the corresponding answer codes for each questions are generated.

        N.B: Here it's assumed a question can only be dependent within a section.
        :param question_list: list of questions (``SurveyRow`` objects) within the group
        :type question_list: python list of ``SurveyRow`` objects
        :param group_counter: group counter
        :type group_counter: int
        :return: None
        :rtype: None
        """
        counter = 0

        for index, question in enumerate(question_list):
            if question.relevant is None or question.relevant == "":
                counter += 1
                if group_counter:
                    question.code = str(group_counter) + "." + str(counter)
                else:
                    question.code = str(counter)
            else:
                # question.code = question_list[index - 1].code + "." + str(parent_counter)
                code, count = self.get_qs_code_from_name(question, self.full_survey)
                question.code = code + "." + str(count)
            question.create_answer_code()

    @staticmethod
    def get_qs_code_from_name(question, full_survey_list):
        """
        This method is better understood from the params and return descriptions.

        :param question: The specific question in which's parents we are interested in
        :type question: A ``SurveyRow`` object
        :param full_survey_list: List of all questions in the survey
        :type full_survey_list: A list of ``SurveyRow`` object
        :return: returns a tuple. The first element is the code number of the first parent question of the \
         current question. The second element is the counter which represents how many times the parent question
         had been used as the first dependent parent question.

        :rtype: A tuple containing a string and an intger
        """

        relevant = question.relevant.strip()
        dependency_list = re.findall(r"[^'\s]\S*|'.*?'", relevant)
        if len(dependency_list) == 3:
            for i in range(0, len(dependency_list), 3):
                relevant = dependency_list[i]
                dependent_qs_id = relevant[relevant.index("{") + 1:relevant.index("}")]
                for parent_qs in full_survey_list:
                    if parent_qs.name == dependent_qs_id:
                        question.parent_list.append(parent_qs)
                        # parent_qs.child_list.append(question)
                        current_relation = Relation(dependency_list[i + 1], dependency_list[i + 2])
                        parent_qs.count_as_a_parent += 1

                        question.parent_relation_list.append(current_relation)
        elif len(dependency_list) > 3:
            for i in range(0, len(dependency_list), 4):
                relevant = dependency_list[i]
                dependent_qs_id = relevant[relevant.index("{") + 1:relevant.index("}")]
                for parent_qs in full_survey_list:
                    if parent_qs.name == dependent_qs_id:
                        question.parent_list.append(parent_qs)
                        # parent_qs.child_list.append(question)
                        current_relation = Relation(dependency_list[i + 1], dependency_list[i + 2])

                        if (i + 3) < len(dependency_list):
                            current_relation.log_op = dependency_list[i + 3]

                        question.parent_relation_list.append(current_relation)
                        parent_qs.count_as_a_parent += 1
                        # parent_qs.child_realtion_list.append(current_relation)
        # Assuming Only One dependency
        # TODO Here we assumed a question's parent question is the first dependency question, it must be fixed
        relevant = question.relevant
        dependent_qs_id = relevant[relevant.index("{") + 1:relevant.index("}")]
        for qs in full_survey_list:
            if qs.name == dependent_qs_id:
                qs.parent_counter += 1
                return qs.code, qs.parent_counter
