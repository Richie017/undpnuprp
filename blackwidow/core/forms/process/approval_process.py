from django import forms
from django.forms.models import modelformset_factory

from blackwidow.core.forms.process.approval_level import ApprovalLevelForm
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models.process.approval_level import ApprovalLevel
from blackwidow.core.models.process.approval_process import ApprovalProcess
from blackwidow.engine.library.model_list_finder import ModelListFinder
from config.apps import INSTALLED_APPS

__author__ = 'Sohel'

approval_step_formset = modelformset_factory(ApprovalLevel, form=ApprovalLevelForm, formset=GenericModelFormSetMixin,
                                             extra=0, min_num=1, validate_min=True, can_delete=True)


class ApprovalProcessForm(GenericFormMixin):
    def __init__(self, data=None, files=None, **kwargs):
        super().__init__(data=data, files=files, **kwargs)
        initial_steps = ApprovalLevel.objects.none()
        if self.instance and self.instance.pk:
            initial_steps = self.instance.levels.all().order_by('level')

        model_names = ModelListFinder.find_models(app_labels=INSTALLED_APPS, include_class_name=True)
        self.fields['model_name'] = forms.ChoiceField(label='Select Model', choices=model_names,
                                                      widget=forms.Select(attrs={'class': 'select2'}))
        self.add_child_form("levels", approval_step_formset(data=data, files=files, queryset=initial_steps,
                                                            header='Approval Levels', add_more=True, **kwargs))

    class Meta:
        model = ApprovalProcess
        fields = ['model_name']
