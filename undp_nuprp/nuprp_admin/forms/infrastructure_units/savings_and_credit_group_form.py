from django import forms
from django.db import transaction
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.geography.geography import Geography
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from undp_nuprp.nuprp_admin.models.infrastructure_units.cdc import CDC
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group import PrimaryGroup
from undp_nuprp.nuprp_admin.models.infrastructure_units.primary_group_member import PrimaryGroupMember
from undp_nuprp.nuprp_admin.models.infrastructure_units.savings_and_credit_group import SavingsAndCreditGroup

__author__ = "Shama, Ziaul Haque"


class SavingsAndCreditGroupForm(GenericFormMixin):
    division = forms.IntegerField()
    city = forms.IntegerField()
    cdc = forms.IntegerField()

    def __init__(self, data=None, files=None, instance=None, prefix='', **kwargs):
        super(SavingsAndCreditGroupForm, self).__init__(
            data=data, files=files, instance=instance, prefix=prefix, **kwargs)
        initial_division = None
        initial_city = None
        if instance and instance.address:
            initial_city = instance.address.geography
            initial_division = initial_city.parent

        self.fields['name'].required = False

        self.fields['division'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name__icontains='division').order_by('name'), label='Division',
            initial=initial_division, widget=forms.Select(attrs={'class': 'select2', 'width': '220'}),
            required=False
        )

        self.fields['city'] = GenericModelChoiceField(
            queryset=Geography.objects.filter(level__name__icontains='city').order_by('name'),
            label='Pouroshava/City Corporation', initial=initial_city,
            required=False,
            widget=forms.TextInput(
                attrs={
                    'class': 'select2-input', 'width': '220',
                    'data-depends-on': 'division',
                    'data-depends-property': 'parent:id',
                    'data-url': reverse(Geography.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1'
                }
            )
        )

        self.fields['cdc'] = GenericModelChoiceField(
            queryset=CDC.objects.all(), label='CDC',
            initial=instance.primary_group.parent if instance else None,
            required=False,
            widget=forms.TextInput(
                attrs={
                    'class': 'select2-input', 'width': '220',
                    'data-depends-on': 'city',
                    'data-depends-property': 'address:geography:parent:id',
                    'data-url': reverse(CDC.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                }
            )
        )

        self.fields['primary_group'] = GenericModelChoiceField(
            queryset=PrimaryGroup.objects.all(), label='Primary Group',
            initial=instance.primary_group if instance else None,
            required=False,
            widget=forms.TextInput(
                attrs={
                    'class': 'select2-input', 'width': '220',
                    'data-depends-on': 'cdc',
                    'data-depends-property': 'parent:id',
                    'data-url': reverse(PrimaryGroup.get_route_name(
                        ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1&sort=name'
                }
            )
        )

        self.fields['date_of_formation'] = forms.DateTimeField(
            label='Date of SCG Formation',
            input_formats=['%d/%m/%Y'],
            required=False,
            widget=forms.DateTimeInput(
                attrs={
                    'data-format': "dd/MM/yyyy",
                    'class': 'date-time-picker',
                    'readonly': 'True'
                },
                format='%d/%m/%Y'
            ),
            initial=instance.date_of_formation if instance else None
        )

    def save(self, commit=True):
        with transaction.atomic():
            city = self.cleaned_data['city']
            new_instance = True
            if self.instance and self.instance.pk:
                new_instance = False
            self.instance = super(SavingsAndCreditGroupForm, self).save()

            create_address = True
            if self.instance.address and self.instance.address.geography_id == city.pk:
                create_address = False
            if create_address:
                address = ContactAddress.objects.create(geography_id=city.pk)
                self.instance.address = address
                self.instance.save()

            if new_instance:
                pg_members = PrimaryGroupMember.objects.filter(assigned_to_id=self.instance.primary_group_id)
                pg_members = list(pg_members)
                self.instance.members.add(*pg_members)
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = SavingsAndCreditGroup
        fields = ('name', 'division', 'city', 'cdc', 'primary_group', 'date_of_formation')
