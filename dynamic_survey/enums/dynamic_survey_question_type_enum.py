from enum import Enum

from dynamic_survey.enums.xlform_question_type_enum import XLFormQuestionTypeEnum


class DynamicSurveyQuestionTypeEnum(Enum):
    TextInput = 'text'
    NumberInput = 'number'
    PhoneNumberInput = 'phone'
    SingleSelectInput = 'single'
    MultipleSelectInput = 'multiple'
    EditableSelectInput = 'editable'
    EmailAddressInput = 'email'
    DateInput = 'date'
    TimeInput = 'time'
    MixedInput = 'mixed'
    RankSelectInput = 'rank'
    ImageInput = "image"
    GridInput = "grid"
    GridRow = "grid_row"
    DynamicGrid = "dynamic_grid"

    @classmethod
    def get_question_type_from_raw(cls, raw):
        if raw == XLFormQuestionTypeEnum.NumberInput.value:
            return cls.NumberInput.value
        if raw == XLFormQuestionTypeEnum.TextInput.value:
            return cls.TextInput.value
        if raw == XLFormQuestionTypeEnum.PhoneNumberInput.value:
            return cls.PhoneNumberInput.value
        if raw == XLFormQuestionTypeEnum.DateInput.value:
            return cls.DateInput.value
        if str(raw).startswith(XLFormQuestionTypeEnum.SingleSelectInput.value):
            return cls.SingleSelectInput.value
        if str(raw).startswith(XLFormQuestionTypeEnum.MultipleSelectInput.value):
            return cls.MultipleSelectInput.value
        if str(raw).startswith(XLFormQuestionTypeEnum.EditableSelectInput.value):
            return cls.EditableSelectInput.value
        if str(raw).startswith(XLFormQuestionTypeEnum.RankSelectInput.value):
            return cls.RankSelectInput.value
        if str(raw).startswith(XLFormQuestionTypeEnum.ImageInput.value):
            return cls.ImageInput.value
        if str(raw).startswith(XLFormQuestionTypeEnum.GridInput.value):
            return cls.GridInput.value
        if str(raw).startswith(XLFormQuestionTypeEnum.GridRow.value):
            return cls.GridRow.value
        if str(raw).startswith(XLFormQuestionTypeEnum.DynamicGrid.value):
            return cls.DynamicGrid.value
