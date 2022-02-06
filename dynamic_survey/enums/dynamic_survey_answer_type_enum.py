from enum import Enum


class DynamicSurveyAnswerTypeEnum(Enum):
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
    RankSelectInput = 'rank'
    ImageInput = "image"
    GridInput = "grid"
    DynamicGrid = "dynamic_grid"
