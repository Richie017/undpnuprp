from collections import OrderedDict

from crequest.middleware import CrequestMiddleware
from django.db import transaction
from django.forms.models import ModelForm, BaseModelFormSet
from django.forms.utils import ErrorList

from blackwidow.core.models.contracts.base import DomainEntity
from blackwidow.core.models.contracts.organizationdomainentity import OrganizationDomainEntity
from blackwidow.engine.extensions.bw_titleize import bw_titleize

__author__ = 'mahmudul'

from django import forms

allowed_formset_kwargs = ['data', 'files', 'auto_id', 'prefix', 'initial', 'error_class', 'form_kwargs', 'queryset']


class GenericModelFormSetMixin(BaseModelFormSet):
    request = None
    header = ''
    add_more = True
    inline = False
    partial_view = False
    tab = ''
    render_table = False
    extra_params = dict()

    def __init__(self, request=None, instance=None, header='', render_table=False, form_header='', display_inline=False,
                 add_more=True, partial_view=False, tab='', **kwargs):
        super().__init__(**(GenericModelFormSetMixin._construct_base_formset_kwargs(**kwargs)))
        self.request = request
        self.header = header
        self.add_more = add_more
        self.inline = display_inline
        self.partial_view = partial_view
        self.tab = tab
        self.render_table = render_table
        self.extra_params = GenericModelFormSetMixin._construct_form_kwargs(**kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs.update({
            'request': self.request,
            'tab': self.tab,
            'partial_view': self.partial_view,
            'render_table': self.render_table
        })
        kwargs.update(self.extra_params)
        return super()._construct_form(i, **kwargs)

    @classmethod
    def _construct_base_formset_kwargs(cls, **kwargs):
        kw_args = dict()
        for key in kwargs.keys():
            if key in allowed_formset_kwargs:
                kw_args[key] = kwargs[key]
        return kw_args

    @classmethod
    def _construct_form_kwargs(cls, **kwargs):
        kw_args = kwargs.copy()
        for key in kwargs.keys():
            if key in allowed_formset_kwargs:
                del kw_args[key]
        return kw_args


class GenericFormMixin(ModelForm):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    step = forms.CharField(required=False, widget=forms.HiddenInput)
    total_steps = forms.CharField(required=False, widget=forms.HiddenInput)
    child_forms = list()
    header = ''
    encryption_enabled = None
    request = None
    inline = False
    partial_view = False
    render_table = False
    form_context = dict()

    @classmethod
    def get_template(cls):
        return ''

    @property
    def prefix_child_forms(self):
        return [x[1] for x in self.child_forms if x[2]]

    @property
    def suffix_child_forms(self):
        return [x[1] for x in self.child_forms if not x[2]]

    def add_child_form(self, key, form, is_prefix_form=False):
        if key is None:
            key = form.__class__.__name__.lower()
        self.child_forms.append((key, form, is_prefix_form))
        # self.__class__.form_context[form.__class__.__name__.lower()] = form.__class__.get_form_context()

    def get_wizard_form(self, step=0):
        steps = self.prefix_child_forms + [self] + self.suffix_child_forms
        return steps[step]

    def show_form_inline(self):
        return False

    @classmethod
    def field_groups(cls):
        _group = OrderedDict()
        return _group

    @property
    def field_count(self):
        return len(self.fields) + (1 if self.render_table else 0)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix="",
                 initial=None, error_class=ErrorList, label_suffix=None, render_table=False,
                 empty_permitted=False, request=None, partial_view=False, instance=None, generate_childforms=False,
                 childform_dict={}, display_inline=False, **kwargs):

        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix,
                         initial=initial, error_class=error_class, label_suffix=label_suffix,
                         empty_permitted=empty_permitted, instance=instance)
        self.request = request
        self.child_forms = list()

        self.partial_view = partial_view
        self.encryption_enabled = False
        self.header = kwargs.get('form_header', '')
        self.inline = display_inline
        self.render_table = render_table
        if self.header == '':
            self.header = bw_titleize(self.Meta.model.__name__) + ' form'
        if instance and instance.pk:
            self.is_new_instance = False
        else:
            self.is_new_instance = True

    def is_valid(self):
        valid = True
        for f in self.prefix_child_forms:
            valid &= f.is_valid()
        for f in self.suffix_child_forms:
            valid &= f.is_valid()
        valid = super().is_valid() and valid
        return valid

    def load_default_fields(self):
        request = CrequestMiddleware.get_request()
        if isinstance(self.instance, OrganizationDomainEntity):
            self.instance.organization = request.c_organization

        if isinstance(self.instance, DomainEntity) and not self.instance.created_by:
            self.instance.last_updated_by = request.c_user
            self.instance.created_by = request.c_user
        else:
            self.instance.last_updated_by = request.c_user

    def save(self, commit=True):
        from django.db import models

        # Before Updating the object create a new version of that object based on decorator and project settings
        try:
            if not self.is_new_instance:
                self._meta.model.objects.get(id=self.instance.pk).handle_version_creation()
        except Exception as e:
            _msg = "{} Version Couldn't Be Created. Error Message: {}".format(self.Meta.model.__name__, e)
            from blackwidow.core.models import ErrorLog
            ErrorLog.log(exp=_msg)

        f_models = dict()
        m2m_models = dict()
        self.load_default_fields()
        for (k, f, p) in self.child_forms:
            try:
                field = self.instance._meta.get_field(k)
                if isinstance(field, (models.OneToOneField, models.ForeignKey)):
                    f_models[k] = f
                elif isinstance(field, models.ManyToManyField):
                    m2m_models[k] = f
            except Exception as exp:
                # ErrorLog.log(exp)
                pass
        with transaction.atomic():
            for k in f_models.keys():
                setattr(self.instance, k, f_models[k].save(commit))
            self.instance = super().save(commit)
            for k in m2m_models.keys():
                _items = getattr(self.instance, k)
                _item_dict = dict()
                for _f in m2m_models[k]:
                    try:
                        _item = _f.save(commit)
                        if _item.pk is not None:
                            _item_dict[_item.pk] = _item
                            if not _items.filter(pk=_item.pk).exists():
                                _items.add(_item)
                    except:
                        pass

                for _item in _items.all():
                    if _item.pk not in _item_dict:
                        _items.remove(_item)
            if hasattr(self.instance, 'create_version_if_needed'):
                self.instance.create_version_if_needed()
            return self.instance

    @classmethod
    def get_step_count(cls):
        return 1

    @classmethod
    def get_form_context(cls):
        return cls.form_context

    class Meta:
        model = DomainEntity
        fields = []
        exclude = ['date_created', 'last_updated', 'created_by', 'last_updated_by']
        render_tab = False


class GenericDefaultFormMixin(forms.Form):
    id = forms.CharField(required=False, widget=forms.HiddenInput)
    step = forms.CharField(required=False, widget=forms.HiddenInput)
    total_steps = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, request=None, partial_view=False, generate_childforms=False, childform_dict={},
                 display_inline=False, **kwargs):
        super().__init__(data=data, files=files, auto_id=auto_id, prefix=prefix,
                         initial=initial, error_class=error_class, label_suffix=label_suffix,
                         empty_permitted=empty_permitted)

    def save(self, **kwargs):
        pass
