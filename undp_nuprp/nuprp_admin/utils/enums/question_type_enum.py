from enum import Enum

__author__ = 'Tareq'


class QuestionTypeEnum(Enum):
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
    DynamicGrid = 'dynamic_grid'

    @classmethod
    def get_question_type_from_raw(cls, raw):
        if raw == 'Number Input':
            return cls.NumberInput.value
        if raw == 'Free Text Input':
            return cls.TextInput.value
        if raw == 'Mobile Number':
            return cls.PhoneNumberInput.value
        if raw == 'Single Choice Field':
            return cls.SingleSelectInput.value
        if raw == 'Multiple Choice Field':
            return cls.MultipleSelectInput.value
        if raw == 'Free Choice Field':
            return cls.EditableSelectInput.value
        if raw == 'Date Input':
            return cls.DateInput.value
        if raw == 'Dynamic Grid':
            return cls.DynamicGrid.value

    @classmethod
    def get_question_type_from_value(cls, value):
        if value == cls.NumberInput.value:
            return 'Number Input'
        if value == cls.TextInput.value:
            return 'Free Text Input'
        if value == cls.PhoneNumberInput.value:
            return 'Mobile Number'
        if value == cls.SingleSelectInput.value:
            return 'Single Choice Field'
        if value == cls.MultipleSelectInput.value:
            return 'Multiple Choice Field'
        if value == cls.EditableSelectInput.value:
            return 'Free Choice Field'
        if value == cls.DateInput.value:
            return 'Date Input'
        if value == cls.DynamicGrid.value:
            return 'Dynamic Grid'
