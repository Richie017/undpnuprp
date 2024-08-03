from django import forms

from blackwidow.core.forms import LocationForm, ImageFileObjectForm
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models import Geography
from undp_nuprp.approvals.models import SIFAndCRMIFIntervention
from undp_nuprp.approvals.models.interactive_maps.output_five.sif_and_crmif_intervention import INTERVENTIONS, \
    REPORT_TYPES

__author__ = 'Ziaul Haque'

INTERVENTION_CHOICES = [
    ('', 'Select One'),
]

for intervention_type in INTERVENTIONS:
    INTERVENTION_CHOICES.append((intervention_type, intervention_type), )

REPORT_TYPE_CHOICES = [
    ('', 'Select One'),
]

for report_type in REPORT_TYPES:
    REPORT_TYPE_CHOICES.append((report_type, report_type), )


class SIFAndCRMIFInterventionForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SIFAndCRMIFInterventionForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['type_of_report'] = forms.ChoiceField(
            label='Type of Report',
            choices=REPORT_TYPE_CHOICES,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.type_of_report if instance and instance.pk else None
        )

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City', empty_label='Select One',
            initial=instance.city if instance else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )

        self.fields['survey_time'] = forms.DateTimeField(
            label='Survey Time',
            required=False,
            input_formats=['%d/%m/%Y'],
            widget=forms.DateInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.survey_time if instance else None
        )

        self.fields['type_of_intervention'] = forms.ChoiceField(
            label='Type of Intervention',
            choices=INTERVENTION_CHOICES,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.type_of_intervention if instance and instance.pk else None
        )

        self.fields['footpath_length'] = forms.DecimalField(
            label="Length of the footpath in meter",
            min_value=0, required=False, widget=forms.NumberInput()
        )
        self.fields['drain_length'] = forms.DecimalField(
            label="Length of the drain in meter (average)",
            min_value=0, required=False, widget=forms.NumberInput()
        )
        self.fields['number_of_benefited_households'] = forms.IntegerField(
            label="Total number of Households benefiting from this facility",
            min_value=0, required=False, widget=forms.NumberInput()
        )

        kwargs.update({
            'prefix': 'image'
        })
        self.add_child_form("image", ImageFileObjectForm(
            data=data, files=files,
            instance=instance.image if instance else None,
            form_header='Image', **kwargs
        ))

        kwargs.update({
            'prefix': 'location'
        })
        self.add_child_form('location', LocationForm(
            data=data, files=files,
            instance=instance.location if instance else None,
            form_header='Location', **kwargs
        ))

    class Meta(GenericFormMixin.Meta):
        model = SIFAndCRMIFIntervention
        fields = (
            'type_of_report', 'city', 'survey_time', 'type_of_intervention', 'footpath_length', 'drain_length',
            'number_of_benefited_households',
        )
