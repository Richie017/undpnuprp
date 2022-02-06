from django import forms
from django.db import transaction
from django.db.models.functions import Length
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc_cluster import CDCCluster
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup

__author__ = "Shama"


class PrimaryGroupForm(GenericFormMixin):
    city = forms.IntegerField()
    cdc_cluster = forms.IntegerField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(PrimaryGroupForm, self).__init__(data=data, files=files, instance=instance, prefix=prefix, **kwargs)

        self.fields['name'].required = False

        self.fields['date_of_formation'] = forms.DateTimeField(
            label='Date of Formation',
            input_formats=['%d/%m/%Y %H:%M'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy hh:mm",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y %H:%M'
            ),
        )

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name='Pourashava/City Corporation').order_by('name'), label='City',
            empty_label='Select One', initial=instance.parent.address.geography.parent if instance else None,
            widget=forms.Select(attrs={'class': 'select2', 'width': '220'}),
            required=False
        )

        self.fields['cdc_cluster'] = GenericModelChoiceField(
            queryset=CDCCluster.objects.all(), label='CDC Cluster',
            initial=instance.parent.parent if instance else None,
            required=False,
            widget=forms.TextInput(
                attrs={'class': 'select2-input', 'width': '220',
                       'data-depends-on': 'city',
                       'data-depends-property': 'address:geography:id',
                       'data-url': reverse(CDCCluster.get_route_name(
                           ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                       }
            )
        )

        self.fields['parent'] = GenericModelChoiceField(
            queryset=CDC.objects.all(), label='CDC',
            initial=instance.parent if instance is not None else None,
            required=False,
            widget=forms.TextInput(attrs={'class': 'select2-input', 'width': '220',
                                          'data-depends-on': 'cdc_cluster',
                                          'data-depends-property': 'parent:id',
                                          'data-url': reverse(CDC.get_route_name(
                                              ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                                          }))

    def clean(self):
        cleaned_data = super(PrimaryGroupForm, self).clean()
        instance = self.instance
        parent = cleaned_data['parent']
        if instance and parent != instance.parent:
            if instance.client_set.count():
                self.add_error('parent', "Can't change CDC of this group.")
        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            previous_parent = None
            if not self.is_new_instance:
                previous_parent = self.instance.parent

            self.instance = super(PrimaryGroupForm, self).save(commit)
            if self.instance.assigned_code is None or self.instance.assigned_code == '' or (
                    previous_parent and previous_parent != self.instance.parent):
                cdc_code = self.instance.parent.assigned_code
                pg_number = PrimaryGroup.all_objects.annotate(code_len=Length('assigned_code')).filter(
                    parent__pk=self.instance.parent.pk, code_len=10).count()
                pg_serial = str(pg_number + 1)
                if len(pg_serial) < 2:
                    pg_serial = '0' + pg_serial
                self.instance.assigned_code = '%s%2s' % (cdc_code, pg_serial)
                self.instance.save()
            else:
                pass
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = PrimaryGroup
        fields = ('name', 'date_of_formation', 'city', 'cdc_cluster', 'parent')
