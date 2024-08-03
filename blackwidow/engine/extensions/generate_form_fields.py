__author__ = 'ruddra'
from django import forms
from rest_framework import serializers


def genarate_form_field(field, instance_args=dict()):
    '''
    ('char', 'Character Field'),
    ('int', 'Integer Field'),
    ('big_int', 'BigIntegerField Field'),
    ('bool', 'Boolean Field'),
    ('decimal', 'DecimalField Field'),
    ('email', 'Email Field'),
    ('float', 'FloatField Field'),
    ('text', 'TextField Field'),
    ('url', 'URLField Field'),
    ('choice_list', 'Choice Field'),
    ('datetime', 'DateTime Field'),
    ('date', 'Date Field'),
'''

    if field.field_type == 'datetime':
        field_class = forms.CharField
        instance_args['widget'] = forms.DateTimeInput(
            attrs={
                'data-format': "dd/MM/yyyy hh:mm:ss",
                'class': 'date-time-picker'
            },
            format='%d/%m/%Y %H:%M:%S'
        )

    elif field.field_type == 'date':
        field_class = forms.CharField
        instance_args['widget'] = forms.DateTimeInput(
            attrs={
                'data-format': "dd/MM/yyyy",
                'class': 'date-time-picker'
            },
            format='%d/%m/%Y'
        )
    elif field.field_type == 'number':
        field_class = forms.IntegerField

    elif field.field_type == 'calculated':
        field_class = forms.IntegerField

    elif field.field_type == 'int':
        field_class = forms.IntegerField

    elif field.field_type == 'big_int':
        field_class = forms.IntegerField

    elif field.field_type == 'bool':
        field_class = forms.BooleanField

    elif field.field_type == 'decimal':
        field_class = forms.DecimalField

    elif field.field_type == 'email':
        field_class = forms.EmailField

    elif field.field_type == 'float':
        field_class = forms.FloatField

    elif field.field_type == 'text':
        field_class = forms.CharField
        instance_args['max_length'] = 800
        instance_args['widget'] = forms.Textarea(attrs={'class': 'description'})

    elif field.field_type == 'url':
        field_class = forms.URLField

    elif field.field_type == 'choice_list':
        field_class = forms.ChoiceField
        choices = (('', '---------'),)
        if field.list_values:
            choices = field.choices_as_array
        instance_args['choices'] = choices
        instance_args['widget'] = forms.Select(attrs={'class': 'select2'})

    elif field.field_type == 'char':
        field_class = forms.CharField
    else:
        field_class = forms.Textarea
        instance_args['max_length'] = 800
        instance_args['required'] = False

    return field_class(**instance_args)


def genarate_serializer_field(type):
    if type == 'datetime':
        return serializers.CharField(widget=forms.DateTimeInput(format='%d/%m/%Y %H:%M:%S'), required=False)
    elif type == 'int':
        return serializers.IntegerField(required=False)
    elif type == 'big_int':
        return serializers.IntegerField(required=False)
    elif type == 'bool':
        return serializers.BooleanField(required=False)
    elif type == 'decimal':
        return serializers.DecimalField(required=False)
    elif type == 'email':
        return serializers.EmailField(required=False)
    elif type == 'float':
        return serializers.FloatField(required=False)
    elif type == 'text':
        return serializers.CharField(widget=forms.TextInput, required=False)
    elif type == 'url':
        return serializers.URLField(required=False)
    else:
        return serializers.CharField(max_length=8000, required=False)
