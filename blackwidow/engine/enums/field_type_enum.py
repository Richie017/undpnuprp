"""
Created by tareq on 7/30/17
"""
from enum import Enum

__author__ = 'Tareq'


class FieldTypesEnum(Enum):
    Choice_Field = 'choice_list'
    Character_Field = 'char'
    Date_Time_Field = 'datetime'
    Date_Field = 'date'
    Integer_Field = 'number'
    Big_Integer_Field = 'big_int'
    Boolean_Field = 'bool'
    Decimal_Field = 'decimal'
    Email_Field = 'email'
    Float_Field = 'float'
    Text_Field = 'text'
    Url_Field = 'url'

    Foreign_Key_Field = 'foreign_key'  # widget: select
    Many_to_Many_Field = 'many_to_many'  # new forms with add more/ delete options
    Many_to_Many_Select_Field = 'many_to_many_select'  # widget: select multiple
    New_Foreign_Key = 'new_f_key'  # new form

    Calculated_Field = 'calculated'  # calculated field (will depends on other field value)

    @classmethod
    def get_field_types_choices(cls):
        return (
            ('choice_list', 'Choice Field'),
            ('char', 'Character Field'),
            ('datetime', 'Date Time Field'),
            ('date', 'Date Field'),
            ('number', 'Integer Field'),
            ('big_int', 'BigIntegerField Field'),
            ('bool', 'Boolean Field'),
            ('decimal', 'DecimalField Field'),
            ('email', 'Email Field'),
            ('float', 'FloatField Field'),
            ('text', 'TextField Field'),
            ('url', 'URLField Field'),
            ('foreign_key', 'Foreign_Key_Field'),
            ('many_to_many', 'Many_to_Many_Field'),
            ('many_to_many_select', 'Many_to_Many_Select_Field'),
            ('new_f_key', 'New_Foreign_Key'),
            ('calculated', 'Calculated Field'),
        )
