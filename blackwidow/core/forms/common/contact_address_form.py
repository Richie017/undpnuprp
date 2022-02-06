from django import forms
from django.db import transaction
from django.urls.base import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.common.contactaddress import ContactAddress
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.geography.geography_level import GeographyLevel
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.extensions.bw_titleize import bw_compress_name


class ContactAddressForm(GenericFormMixin):
    def __init__(self, data=None, files=None, form_header='', instance=None, prefix='', **kwargs):
        """
        In kwargs, you can pass "address_level" upto which the Geography Fields are displayed
        In kwargs, you can pass "skip_tp_address_level" to False to include "Country" in the form
        """
        super(ContactAddressForm, self).__init__(
            data=data, files=files, form_header=form_header, instance=instance, prefix=prefix, **kwargs)
        _prefix = prefix + '-' if prefix != '' else ''
        # self.fields['postcode'].required = False
        # self.add_child_form("location",
        #                     LocationForm(
        #                         data,
        #                         files,
        #                         form_header='Location',
        #                         instance=instance.location if instance is not None else None,
        #                         prefix=_prefix + str(len(self.suffix_child_forms)), **kwargs
        #                     ))

        # self.Meta.fields = ['street', 'city']
        geography_levels = GeographyLevel.objects.all().order_by('date_created')
        initial_geography = None
        if self.instance.pk:
            initial_geography = self.instance.geography

        address_level = kwargs.get('address_level', '')
        level_index = 0
        is_parent_geography = True
        for level in geography_levels:
            level_index += 1
            if level_index == 1:
                if kwargs.get('skip_top_address_level', True):
                    continue

            initial_of_current_level = None
            _geography = initial_geography
            while _geography is not None:
                if _geography.level_id == level.pk:
                    initial_of_current_level = _geography
                    break
                _geography = _geography.parent

            field_name = bw_compress_name(level.name.lower())
            if (self.instance.pk and self.instance.geography and self.instance.geography.level_id == level.pk) \
                    or level_index == len(geography_levels) or level.name == address_level:
                field_name = 'geography'

            if is_parent_geography:
                widget = forms.Select(
                    attrs={'class': 'select2', 'width': '220'}
                )
                is_parent_geography = False
            else:
                widget = forms.TextInput(
                    attrs={
                        'class': 'select2-input', 'width': '220',
                        'data-depends-on': bw_compress_name(level.parent.name.lower()),
                        'data-depends-property': 'parent:id',
                        'data-url': reverse(Geography.get_route_name(
                            ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1'}
                )

            self.fields[field_name] = \
                GenericModelChoiceField(
                    queryset=Geography.objects.filter(level_id=level.pk).order_by('name'),
                    empty_label='Select One', required=True, label=level.name,
                    initial=initial_of_current_level, widget=widget
                )
            self.Meta.fields.append(field_name)
            if field_name == 'geography':
                break

        # self.Meta.fields.append('postcode')

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super(ContactAddressForm, self).save(commit)
            if 'geography' in self.cleaned_data:
                self.instance.geography = self.cleaned_data['geography']
                self.instance.save()
            return self.instance

    class Meta:
        model = ContactAddress
        # fields = ['street', 'city', 'division', 'state', 'upazila', 'postcode']
        fields = []
        # widgets = {
        #     'street': forms.Textarea,
        # }
        # labels = {
        #     'street': 'Street/Village',
        #     'city': 'Union/City',
        # }
