from django import forms
from django.forms import modelformset_factory

from blackwidow.core.forms import FileObjectForm
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField, GenericModelMultipleChoiceField
from blackwidow.core.mixins.formmixin import GenericFormMixin, GenericModelFormSetMixin
from blackwidow.core.models import ImageFileObject, Geography
from blackwidow.engine.widgets.image_widget import ImageWidget
from undp_nuprp.approvals.forms import FieldMonitoringFollowupForm
from undp_nuprp.approvals.models import SubmittedFieldMonitoringReport, FieldMonitoringFollowup
from undp_nuprp.approvals.models.field_monitoring.field_monitoring_output import FieldMonitoringOutput


class FileObjectForm2(FileObjectForm):
    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super(FileObjectForm2, self).__init__(data=data, files=files, instance=instance, **kwargs)
        self.fields['file'].disabled = True


class ImageFileObjectForm2(FileObjectForm2):
    file = \
        forms.ImageField(
            required=False,
            label='Image',
            widget=ImageWidget(
                attrs={
                    'style': 'margin:0 0 0 160px;'
                }
            )
        )

    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super(ImageFileObjectForm2, self).__init__(data=data, files=files, instance=instance, **kwargs)

    class Meta:
        model = ImageFileObject
        fields = ['file', 'description']


class FieldMonitoringFollowupForm2(FieldMonitoringFollowupForm):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(FieldMonitoringFollowupForm2, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        for field, val in self.fields.items():
            self.fields[field].disabled = True


image_formset = modelformset_factory(
    ImageFileObject, form=ImageFileObjectForm2, formset=GenericModelFormSetMixin, extra=0, min_num=1, max_num=3,
    validate_min=True, validate_max=True
)

followup_formset = modelformset_factory(
    FieldMonitoringFollowup, form=FieldMonitoringFollowupForm2, formset=GenericModelFormSetMixin,
    extra=0, min_num=1, validate_min=True
)


class SubmittedFieldMonitoringReportForm(GenericFormMixin):
    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SubmittedFieldMonitoringReportForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            required=False,
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One',
            initial=instance.city if instance is not None else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
        )

        self.fields['date'] = forms.DateTimeField(
            label='Date',
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
            initial=instance.date if instance else None
        )

        self.fields['followup_date'] = forms.DateTimeField(
            label='Followup Date',
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
            initial=instance.followup_date if instance else None
        )

        self.fields['output'] = GenericModelMultipleChoiceField(
            required=False,
            queryset=FieldMonitoringOutput.objects.all().order_by('date_created'),
            label='Output (1 to 5) please mentioned under which output you visited',
            widget=forms.SelectMultiple(
                attrs={'class': 'select2', 'multiple': 'multiple'}
            ),
            initial=instance.output.all() if instance and instance.pk else None
        )

        self.add_child_form("attachment", FileObjectForm2(
            data=data, files=files,
            instance=instance.attachment if instance is not None else None,
            form_header='Please attach a file', **kwargs
        ))

        if instance and instance.pk:
            followup_objects = instance.key_observations.all()
        else:
            followup_objects = FieldMonitoringFollowup.objects.none()

        if instance and instance.pk:
            report_pictures = instance.report_pictures.all()
        else:
            report_pictures = ImageFileObject.objects.none()

        self.add_child_form("key_observations", followup_formset(
            data=data, files=files, queryset=followup_objects,
            prefix='key_observations',
            header='Key Observations',
            add_more=False, **kwargs
        ))

        self.add_child_form("report_pictures", image_formset(
            data=data, files=files, queryset=report_pictures,
            header='Please submit report pictures',
            prefix='report_pictures',
            add_more=False, **kwargs
        ))

        for sect, fields in self.field_groups().items():
            if sect == 'Management Comments':
                continue
            for field in fields:
                self.fields[field].disabled = True

    class Meta(GenericFormMixin.Meta):
        model = SubmittedFieldMonitoringReport

        fields = ('international_technical_adviser', 'project_manager', 'monitoring_and_evaluation_specialist',
                  'output_leads', 'others', 'city', 'ward', 'date', 'name', 'designation', 'mission_objective',
                  'output', 'report_submitted', 'followup_date')

        labels = {
            'report_submitted': 'Report submitted (Prescribed BTOR: This is both for HQ and Field team)'
        }

    @classmethod
    def field_groups(cls):
        _group = super(SubmittedFieldMonitoringReportForm, cls).field_groups()
        _group['Management Comments'] = ['international_technical_adviser', 'project_manager',
                                         'monitoring_and_evaluation_specialist', 'output_leads', 'others']
        _group['Basic Details'] = ['city', 'ward', 'date', 'name', 'designation', 'mission_objective', 'output',
                                   'report_submitted', 'followup_date']

        return _group
