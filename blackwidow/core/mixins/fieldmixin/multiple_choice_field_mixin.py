from django.forms import MultipleChoiceField
from django.forms.models import ModelChoiceField

__author__ = 'Mahmud'


class GenericModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_choice_name()


class GenericAppChoiceField(ModelChoiceField):
    def label_from_instance(self, app):
        return app['app_label']


class GenericModelClassChoiceField(ModelChoiceField):
    def label_from_instance(self, model):
        return model['model']


class GenericMultipleChoiceField(MultipleChoiceField):

    def prepare_value(self, value):
        if isinstance(value, str):
            value = value.split(',')
        return super(GenericMultipleChoiceField, self).prepare_value(value)
