from django import forms
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FileField
from django.forms.widgets import SelectMultiple

from blackwidow.core.mixins.fieldmixin.multiple_select_field_mixin import GenericModelMultipleChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.process.approval_level import ApprovalLevel
from blackwidow.core.models.roles.role import Role
from blackwidow.engine.library.model_list_finder import ModelListFinder
from config.apps import INSTALLED_APPS

__author__ = 'Sohel'


class ApprovalLevelForm(GenericFormMixin):
    def __init__(self, instance=None, data=None, files=None, **kwargs):
        super().__init__(data=data, instance=instance, files=files, **kwargs)
        self.fields['roles'] = GenericModelMultipleChoiceField(
            label='Select Roles', required=True,
            queryset=Role.objects.all(),
            widget=SelectMultiple(
                attrs={
                    'class': 'select2',
                    'multiple': 'multiple'
                }
            ),
            initial=instance.roles.all() if instance is not None else None
        )
        model_names = [('---', 'Select Model')]
        model_names += ModelListFinder.find_models(app_labels=INSTALLED_APPS, include_class_name=True)
        self.fields['approve_model'] = forms.ChoiceField(label='Approved Model', required=False, choices=model_names,
                                                         widget=forms.Select(attrs={'class': 'select2'}))
        self.fields['reject_model'] = forms.ChoiceField(label='Rejected Model', required=False, choices=model_names,
                                                        widget=forms.Select(attrs={'class': 'select2'}))
        self.fields['level'] = forms.IntegerField(min_value=1, initial=1, required=True, widget=forms.NumberInput(
            attrs={'class': 'approval_process_level', 'readonly': 'true'}))

    def show_form_inline(self):
        return True

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if field.disabled:
                value = self.initial.get(name, field.initial)
            else:
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)

    class Meta:
        model = ApprovalLevel
        fields = ['roles', 'approve_model', 'reject_model', 'level']
