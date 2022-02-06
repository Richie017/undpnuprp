import calendar

from django import forms
from django.db import transaction
from django.urls.base import reverse

from blackwidow.core.forms import LocationForm
from blackwidow.core.mixins.fieldmixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models import Geography, Location, CustomFieldValue
from blackwidow.engine.enums.field_type_enum import FieldTypesEnum
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions import bw_titleize
from blackwidow.engine.extensions.generate_form_fields import genarate_form_field
from undp_nuprp.approvals.models import PendingCDCMonthlyReport, CDCMonthlyReportField
from undp_nuprp.nuprp_admin.models import CDC

__author__ = "Ziaul Haque"


class PendingCDCMonthlyReportForm(GenericFormMixin):
    city = forms.IntegerField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(PendingCDCMonthlyReportForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
                                                          **kwargs)
        self.fields['year'] = forms.CharField(
            widget=forms.Select(
                choices=[(_y, str(_y)) for _y in range(2010, 2031)],
                attrs={'class': 'select2', 'width': '220'}
            )
        )

        self.fields['month'] = forms.CharField(
            widget=forms.Select(
                choices=[(i, calendar.month_name[i]) for i in range(1, 13)],
                attrs={'class': 'select2', 'width': '220'}
            )
        )

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One', initial=instance.cdc.address.geography.parent if instance else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['cdc'] = GenericModelChoiceField(
            queryset=CDC.objects.all(), label='CDC',
            initial=instance.cdc if instance else None,
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220',
                                          'data-depends-on': 'city',
                                          'data-depends-property': 'address:geography:parent:id',
                                          'data-url': reverse(CDC.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                                          })
        )

        self.add_child_form('location', LocationForm(
            data=data, files=files,
            instance=instance.location if instance else None,
            form_header='Location', **kwargs
        ))

        cdc_monthly_report_field_form = self

        cdc_monthly_report_fields = CDCMonthlyReportField.objects.all().order_by('assigned_code')
        cdc_monthly_report_field_values = self.instance.field_values.all()
        for x in cdc_monthly_report_fields:
            field_instance_args = {
                'label': bw_titleize(x.name),
                'required': x.is_required,
            }
            if x.field_type in [FieldTypesEnum.Integer_Field.value, FieldTypesEnum.Calculated_Field.value]:
                pass
            cdc_monthly_report_field_form.fields['field_' + str(x.assigned_code)] = genarate_form_field(x,
                                                                                                        field_instance_args)
            if x.assigned_code not in [f.field.assigned_code for f in cdc_monthly_report_field_values]:
                cdc_monthly_report_field_form.fields['field_' + str(x.assigned_code)].initial = ""
            else:
                cdc_monthly_report_field_form.fields['field_' + str(x.assigned_code)].initial = \
                    [f.value for f in cdc_monthly_report_field_values if f.field.assigned_code == x.assigned_code][0]

    def save(self, commit=True):
        with transaction.atomic():
            pending_cdc_monthly_report = PendingCDCMonthlyReport()
            pending_cdc_monthly_report.parent_id = self.instance.parent_id
            pending_cdc_monthly_report.parent_tsync_id = self.instance.parent_tsync_id
            pending_cdc_monthly_report.year = self.cleaned_data['year']
            pending_cdc_monthly_report.month = self.cleaned_data['month']
            pending_cdc_monthly_report.cdc = self.cleaned_data['cdc']
            pending_cdc_monthly_report.remarks = self.cleaned_data['remarks']

            _location_form = [t[1] for t in self.child_forms if t[0] == 'location'][0]
            location = Location()
            location.longitude = _location_form.cleaned_data['longitude']
            location.latitude = _location_form.cleaned_data['latitude']
            location.save()

            pending_cdc_monthly_report.location = location
            pending_cdc_monthly_report.save()

            cdc_monthly_report_fields = CDCMonthlyReportField.objects.all().order_by('assigned_code')
            cdc_monthly_report_field_form = self
            for x in cdc_monthly_report_fields:
                if ('field_' + str(x.assigned_code)) in cdc_monthly_report_field_form.fields:
                    value = cdc_monthly_report_field_form.cleaned_data['field_' + str(x.assigned_code)]
                    f_value = CustomFieldValue()
                    f_value.value = value
                    f_value.field = x
                    f_value.save()
                    pending_cdc_monthly_report.field_values.add(f_value)

            self.instance = pending_cdc_monthly_report
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = PendingCDCMonthlyReport
        fields = ('year', 'month', 'city', 'cdc', 'remarks')
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(PendingCDCMonthlyReportForm, cls).field_groups()
        _group['Basic Information'] = ['year', 'month', 'city', 'cdc_cluster', 'cdc', 'remarks']

        cdc_monthly_report_fields = CDCMonthlyReportField.objects.order_by('field_group__weight', 'weight').values(
            'field_group__name', 'assigned_code')
        for cdc_monthly_report_field in cdc_monthly_report_fields:
            _field_name = 'field_' + cdc_monthly_report_field['assigned_code']
            if cdc_monthly_report_field['field_group__name'] not in _group.keys():
                _group[cdc_monthly_report_field['field_group__name']] = list()
            _group[cdc_monthly_report_field['field_group__name']].append(_field_name)

        return _group
