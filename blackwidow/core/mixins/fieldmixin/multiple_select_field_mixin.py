from django import forms
from django.forms.models import ModelMultipleChoiceField

__author__ = 'Mahmud'


class MultipleSelectWidget(forms.Select):

    def __init__(self, attrs=None, choices=()):
        super(MultipleSelectWidget, self).__init__(attrs)

    def value_from_datadict(self, data, files, name):
        return [ int(value) for value in data.getlist(name) ]


class GenericModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.get_choice_name()

