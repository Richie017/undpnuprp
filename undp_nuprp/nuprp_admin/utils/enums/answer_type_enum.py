from enum import Enum

__author__ = 'Tareq'


class AnswerTypeEnum(Enum):
    TextInput = 'text'
    NumberInput = 'number'
    PhoneNumberInput = 'phone'
    SingleSelectInput = 'single'
    MultipleSelectInput = 'multiple'
    EmailAddressInput = 'email'
    DateInput = 'date'
    TimeInput = 'time'
    MixedInput = 'mixed'
    OtherOption = 'other'

    @classmethod
    def get_answer_type_from_raw(cls, raw):
        if raw == 'Number Input':
            return cls.NumberInput.value
        if raw == 'Free Text Input':
            return cls.TextInput.value
        if raw == 'Mobile Number':
            return cls.PhoneNumberInput.value
        if raw == 'Single Select Option':
            return cls.SingleSelectInput.value
        if raw == 'Multiple Select Option':
            return cls.MultipleSelectInput.value
        if raw == 'Date Input':
            return cls.DateInput.value
        if raw == 'Other Option':
            return cls.OtherOption.value

    @classmethod
    def get_answer_type_label(cls, raw):
        if raw == cls.NumberInput.value:
            return 'Number Input'
        if raw == cls.TextInput.value:
            return 'Free Text Input'
        if raw == cls.PhoneNumberInput.value:
            return 'Mobile Number'
        if raw == cls.SingleSelectInput.value:
            return 'Single Select Option'
        if raw == cls.MultipleSelectInput.value:
            return 'Multiple Select Option'
        if raw == cls.DateInput.value:
            return 'Date Input'
        if raw == cls.OtherOption.value:
            return 'Other Option'
