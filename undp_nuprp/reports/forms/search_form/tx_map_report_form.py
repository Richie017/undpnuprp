from django import forms
from django.forms.forms import Form

from blackwidow.core.models import ConsoleUser
from undp_nuprp.reports.extensions.fields.date_fields import *
from undp_nuprp.reports.extensions.fields.model_field import ModelSingleObjectField


class TransactionMapReportForm(Form):
    from_date = forms.DateTimeField()
    to_date = forms.DateTimeField()
    created_by = forms.MultipleChoiceField()

    def __init__(self, data=None, **kwargs):
        super(TransactionMapReportForm, self).__init__(data=data, **kwargs)
        self.fields['from_date'] = \
            StartDateTimeField(
                label='From Date',
                related_field='date_created',
                input_formats=['%d/%m/%Y'],
                widget=forms.DateInput(
                    attrs={
                        'data-format': "dd/MM/yyyy",
                        'class': 'date-time-picker',
                    },
                    format='%d/%m/%Y'
                )
            )
        self.fields['to_date'] = \
            EndDateTimeField(
                label='To Date',
                related_field='date_created',
                input_formats=['%d/%m/%Y'],
                widget=forms.DateInput(
                    attrs={
                        'data-format': "dd/MM/yyyy",
                        'class': 'date-time-picker'
                    },
                    format='%d/%m/%Y'
                )
            )

        self.fields['created_by'] = \
            ModelSingleObjectField(
                queryset=ConsoleUser.objects.all(),
                empty_label="All",
                label='Select User',
                related_field='created_by',
                required=False,
                widget=forms.Select(
                    attrs={'class': 'select2', 'width': '220'}
                )
            )

    def build_search_query(self):
        query = {}
        for _f in self.fields:
            if _f in self.cleaned_data.keys():
                field = self.fields[_f]
                value = self.cleaned_data[_f]
                key = getattr(field, 'related_field', _f)
                if isinstance(field, StartDateTimeField):
                    query[key + '__gte'] = value
                elif isinstance(field, EndDateTimeField):
                    query[key + '__lte'] = value
                elif isinstance(field, forms.ModelChoiceField):
                    query[key + '_id'] = value.pk if value else None
        return query
