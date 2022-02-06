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
from undp_nuprp.approvals.models import SCGMonthlyReportField, \
    PendingSCGMonthlyReport
from undp_nuprp.nuprp_admin.models import CDC, PrimaryGroup, SavingsAndCreditGroup

__author__ = "Ziaul Haque"


class PendingSCGMonthlyReportForm(GenericFormMixin):
    city = forms.IntegerField()
    cdc = forms.IntegerField()
    primary_group = forms.IntegerField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(PendingSCGMonthlyReportForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix,
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
            empty_label='Select One',
            initial=instance.scg.primary_group.parent.address.geography.parent if instance else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}))

        self.fields['cdc'] = GenericModelChoiceField(
            queryset=CDC.objects.all(), label='CDC',
            initial=instance.scg.primary_group.parent if instance else None,
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220',
                                          'data-depends-on': 'city',
                                          'data-depends-property': 'address:geography:parent:id',
                                          'data-url': reverse(CDC.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                                          })
        )

        self.fields['primary_group'] = GenericModelChoiceField(
            queryset=PrimaryGroup.objects.all(), label='Primary Group',
            initial=instance.scg.primary_group if instance else None,
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220',
                                          'data-depends-on': 'cdc',
                                          'data-depends-property': 'parent:id',
                                          'data-url': reverse(PrimaryGroup.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                                          })
        )

        self.fields['scg'] = GenericModelChoiceField(
            queryset=SavingsAndCreditGroup.objects.all(), label='SCG',
            initial=instance.scg if instance else None,
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220',
                                          'data-depends-on': 'primary_group',
                                          'data-depends-property': 'primary_group:id',
                                          'data-url': reverse(SavingsAndCreditGroup.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                                          })
        )

        self.add_child_form('location', LocationForm(
            data=data, files=files,
            instance=instance.location if instance else None,
            form_header='Location', **kwargs
        ))

        scg_monthly_report_field_form = self

        scg_monthly_report_fields = SCGMonthlyReportField.objects.all().order_by('assigned_code')
        scg_monthly_report_field_values = self.instance.field_values.all()
        for x in scg_monthly_report_fields:
            field_instance_args = {
                'label': bw_titleize(x.name),
                'required': x.is_required,
            }
            if x.field_type in [FieldTypesEnum.Integer_Field.value, FieldTypesEnum.Calculated_Field.value]:
                pass
            scg_monthly_report_field_form.fields['field_' + str(x.assigned_code)] = \
                genarate_form_field(x, field_instance_args)
            if x.assigned_code not in [f.field.assigned_code for f in scg_monthly_report_field_values]:
                scg_monthly_report_field_form.fields['field_' + str(x.assigned_code)].initial = ""
            else:
                scg_monthly_report_field_form.fields['field_' + str(x.assigned_code)].initial = \
                    [f.value for f in scg_monthly_report_field_values if f.field.assigned_code == x.assigned_code][0]

    def save(self, commit=True):
        with transaction.atomic():
            pending_scg_monthly_report = PendingSCGMonthlyReport()
            pending_scg_monthly_report.parent_id = self.instance.parent_id
            pending_scg_monthly_report.parent_tsync_id = self.instance.parent_tsync_id
            pending_scg_monthly_report.year = self.cleaned_data['year']
            pending_scg_monthly_report.month = self.cleaned_data['month']
            pending_scg_monthly_report.scg = self.cleaned_data['scg']
            pending_scg_monthly_report.remarks = self.cleaned_data['remarks']

            _location_form = [t[1] for t in self.child_forms if t[0] == 'location'][0]
            location = Location()
            location.longitude = _location_form.cleaned_data['longitude']
            location.latitude = _location_form.cleaned_data['latitude']
            location.save()

            pending_scg_monthly_report.location = location
            pending_scg_monthly_report.save()

            scg_monthly_report_fields = SCGMonthlyReportField.objects.all().order_by('assigned_code')
            scg_monthly_report_field_form = self
            for x in scg_monthly_report_fields:
                if ('field_' + str(x.assigned_code)) in scg_monthly_report_field_form.fields:
                    value = scg_monthly_report_field_form.cleaned_data['field_' + str(x.assigned_code)]
                    f_value = CustomFieldValue()
                    f_value.value = value
                    f_value.field = x
                    f_value.save()
                    pending_scg_monthly_report.field_values.add(f_value)

            self.instance = pending_scg_monthly_report
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = PendingSCGMonthlyReport
        fields = ('year', 'month', 'city', 'cdc', 'primary_group', 'scg', 'remarks')
        widgets = {
            'remarks': forms.Textarea
        }

    @classmethod
    def field_groups(cls):
        _group = super(PendingSCGMonthlyReportForm, cls).field_groups()
        _group['Basic Information'] = ['year', 'month', 'city', 'cdc', 'primary_group', 'scg', 'remarks']

        scg_monthly_report_fields = SCGMonthlyReportField.objects.order_by('field_group__weight', 'weight').values(
            'field_group__name', 'assigned_code')
        for _monthly_report_field in scg_monthly_report_fields:
            _field_name = 'field_' + _monthly_report_field['assigned_code']
            if _monthly_report_field['field_group__name'] not in _group.keys():
                _group[_monthly_report_field['field_group__name']] = list()
            _group[_monthly_report_field['field_group__name']].append(_field_name)

        return _group
