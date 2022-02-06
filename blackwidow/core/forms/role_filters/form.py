from django import forms

from blackwidow.core.mixins.fieldmixin.multiple_choice_field_mixin import GenericModelChoiceField
from blackwidow.core.mixins.formmixin.form_mixin import GenericFormMixin
from blackwidow.core.models.roles.role import Role
from blackwidow.core.models.roles.role_filter import RoleFilter, RoleFilterEntity

__author__ = 'Machine II'


class RoleFilterForm(GenericFormMixin):

    def __init__(self, data=None, files=None, prefix='', instance=None, **kwargs):
        super().__init__(data=data, files=files, prefix=prefix, instance=instance, **kwargs)
        role_query = Role.objects.all()
        self.fields['role'] = GenericModelChoiceField(label='Select Role', queryset=role_query,
                                                      widget=forms.Select(attrs={'class': 'select2'}),
                                                      initial=instance.role if instance else None)
        self.fields['relations'] = GenericModelChoiceField(label='Select Related Model', queryset=RoleFilter.objects.all(),
                                                           widget=forms.Select(attrs={'class': 'select2'}), required=False)
        self.fields['value_prefix'] = forms.CharField(label='Relation Prefix', required=False)
        self.fields['query_postfix'] = forms.CharField(label='Query Suffix', required=False)

    def save(self, commit=True):
        self.instance = super().save()
        relation = self.cleaned_data['relations']
        value_prefix = str(self.cleaned_data['value_prefix'])
        query_postfix = str(self.cleaned_data['query_postfix'])
        filters = relation.filters.all()
        for filter in filters:
            n_filter = RoleFilterEntity()
            n_filter.target_model_app = filter.target_model_app
            n_filter.target_model = filter.target_model

            if query_postfix:
                head = str(filter.query_str).split('__')[0]
                tails = str(filter.query_str).split('__')[1:]
                query = head + '__' + query_postfix
                for tail in tails:
                    query += '__' + tail
            else:
                query = str(filter.query_str)
            n_filter.query_str = query


            if value_prefix:
                n_filter.value = value_prefix + '.' + str(filter.value)
            else:
                n_filter.value = str(filter.value)

            n_filter.save()
            self.instance.filters.add(n_filter)
        RoleFilter.write_filters()
        return self.instance

    class Meta(GenericFormMixin.Meta):
        model = RoleFilter
        fields = ['role']