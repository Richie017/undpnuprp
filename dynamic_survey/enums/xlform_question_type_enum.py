from enum import Enum


class XLFormQuestionTypeEnum(Enum):
    TextInput = 'text'
    NumberInput = 'integer'
    PhoneNumberInput = 'mobile_number'
    SingleSelectInput = 'select_one'
    MultipleSelectInput = 'select_multiple'
    EditableSelectInput = 'free_choice_field'
    DateInput = 'date'
    RankSelectInput = 'rank_choice_field'
    ImageInput = "image"
    GridInput = "begin score"
    GridRow = "score__row"
    GridInputEnd = "end score"
    GridCode = "kobo--score-choices"
    BeginGroup = "begin group"
    EndGroup = "end group"
    DynamicGrid = "dynamic_grid"