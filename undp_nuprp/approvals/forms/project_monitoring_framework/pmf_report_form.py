from django import forms
from django.db import transaction
from openpyxl.reader.excel import load_workbook

from blackwidow.core.forms import FileObjectForm
from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.exceptions import BWException
from undp_nuprp.approvals.models import PMFReport, PMFUploadedFileQueue

YEAR_CHOICES = [
    (year, year) for year in range(2020, 2025)
]

MONTH_CHOICES = [
    (1, "January"),
    (2, "February"),
    (3, "March"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December")
]

__author__ = "Ziaul Haque"


class PMFAttachmentForm(FileObjectForm):
    def __init__(self, data=None, files=None, instance=None, allow_login=True, **kwargs):
        super(PMFAttachmentForm, self).__init__(data=data, files=files, instance=instance, **kwargs)
        self.fields['file'].label = "Excel"
        self.fields['file'].required = True

    def clean(self):
        cleaned_data = super(PMFAttachmentForm, self).clean()
        if 'file' in cleaned_data:
            try:
                load_workbook(cleaned_data['file'])
            except:
                raise BWException("Invalid file format, attachment must be a valid excel.")
        return cleaned_data


class PMFReportForm(GenericFormMixin):

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(PMFReportForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'),
            label='City', required=False, disabled=False if self.is_new_instance else True,
            empty_label='All Cities', initial=instance.city if instance and instance.pk else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}),
        )

        self.fields['year'] = forms.ChoiceField(
            label='Year', choices=YEAR_CHOICES,
            disabled=False if self.is_new_instance else True,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.year if instance and instance.pk else None
        )

        self.fields['month'] = forms.ChoiceField(
            label='Month', choices=MONTH_CHOICES,
            disabled=False if self.is_new_instance else True,
            widget=forms.Select(
                attrs={'class': 'select2'},
            ),
            initial=instance.month if instance and instance.pk else None
        )

        self.add_child_form("attachment", PMFAttachmentForm(
            data=data, files=files, instance=None,
            form_header='PMF Attachment', **kwargs
        ))

    def clean(self):
        cleaned_data = super(PMFReportForm, self).clean()
        city = cleaned_data.get('city', None)
        year = int(cleaned_data.get('year'))
        month = int(cleaned_data.get('month'))
        if self.is_new_instance:
            existing_report = PMFReport.objects.filter(city=city, year=year, month=month).first()
            if existing_report:
                raise BWException(
                    "Item already exists with given information, please update existing one instead of add new one."
                )
        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super(PMFReportForm, self).save(commit)

            _excel_form = [t[1] for t in self.child_forms if t[0] == 'attachment'][0].save()
            uploaded_excel = PMFUploadedFileQueue()
            uploaded_excel.pmf_report = self.instance
            uploaded_excel.file = _excel_form
            uploaded_excel.save()
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = PMFReport
        fields = ('city', 'year', 'month',)
