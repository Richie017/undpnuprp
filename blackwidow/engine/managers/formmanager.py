import importlib

from django.forms.models import ModelForm

from config.apps import INSTALLED_APPS

__author__ = 'Mahmud'


class FormManager(object):
    @classmethod
    def get_form_dict(cls):
        all_modules = []
        all_forms = dict()
        for app in INSTALLED_APPS:
            forms = app + '.forms'
            try:
                all_modules.append(importlib.import_module(forms))
            except ImportError as err:
                print(err)
            except Exception as err:
                print(err)
        for module in all_modules:
            all_attrs = [x for x in dir(module) if x.endswith('Form')]
            for _attr in all_attrs:
                try:
                    _form = getattr(module, _attr)
                    if issubclass(_form, ModelForm):
                        all_forms[_form.Meta.model.__name__] = _form
                except ImportError as err:
                    print(err)
                except Exception as err:
                    print(err)
        return all_forms

    @classmethod
    def get_form_class(cls, model, form_dict=None, **kwargs):
        if form_dict is None:
            form_dict = cls.get_form_dict()
        if model.__name__ not in form_dict:
            crud_model = model.get_crud_model()
            if crud_model == model:
                generic_form_mixin = getattr(importlib.import_module('blackwidow.core.mixins.formmixin.form_mixin'),
                                             'GenericFormMixin')
                return model.get_form(generic_form_mixin)
            return FormManager.get_form_class(crud_model, form_dict=form_dict)
        return form_dict[model.__name__]
