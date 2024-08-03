from django import forms
from django.db import transaction
from django.urls import reverse

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.geography.geography import Geography
from blackwidow.core.models.geography.geography_level import GeographyLevel
from blackwidow.engine.enums.view_action_enum import ViewActionEnum
from blackwidow.engine.exceptions import BWException

__author__ = 'Tareq'


class GeographyForm(GenericFormMixin):
    def __init__(self, data=None, files=None, prefix=None, instance=None, **kwargs):
        super(GeographyForm, self).__init__(data=data, files=files, prefix=prefix, instance=instance, **kwargs)

        if self.is_new_instance:
            self.fields['level'] = GenericModelChoiceField(
                queryset=GeographyLevel.objects.all(),
                widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
            )
        else:
            self.fields['level'] = GenericModelChoiceField(
                queryset=GeographyLevel.objects.filter(
                    pk=self.instance.level_id
                ) if self.instance and self.instance.level else GeographyLevel.objects.none(),
                widget=forms.Select(attrs={'class': 'select2', 'width': '220'})
            )

        self.fields['parent'] = \
            GenericModelChoiceField(
                queryset=Geography.objects.all().order_by('name'),
                empty_label='Select One', required=False,
                initial=self.instance.parent if self.instance else None,
                widget=forms.TextInput(
                    attrs={
                        'class': 'select2-input', 'width': '220',
                        'data-depends-on': 'level',
                        'data-depends-property': 'level:geographylevel:id',
                        'data-url': reverse(Geography.get_route_name(
                            ViewActionEnum.Manage)) + '?format=json&search=1&disable_pagination=1'}
                )
            )

    def clean(self):
        cleaned_data = super(GeographyForm, self).clean()
        geography_level = cleaned_data['level']
        geography_name = cleaned_data['name']
        geography_parent = cleaned_data['parent']
        if geography_level.name == 'Ward' and len(geography_name) == 1:
            if geography_name == '0':
                self.add_error('name', 'Name of the ward can not be zero (0). It can be 01 / larger value.')
            else:
                self.add_error('name', 'Name of the ward must be as follows: 0{}'.format(geography_name))
        existing_geography_queryset = Geography.objects.filter(
            name=geography_name,
            level=geography_level,
            parent=geography_parent
        )
        if not self.is_new_instance:
            existing_geography_queryset = existing_geography_queryset.exclude(pk=self.instance.pk)
        if existing_geography_queryset.exists():
            raise BWException("Geography already exists with the given parameters.")

        return cleaned_data

    def save(self, commit=True):
        with transaction.atomic():
            self.instance = super(GeographyForm, self).save(commit=commit)
            self.instance.type = self.instance.level.name
            self.instance.save()
            return self.instance

    class Meta(GenericFormMixin.Meta):
        model = Geography
        fields = ['level', 'name', 'parent', ]
