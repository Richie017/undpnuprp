from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import models

__author__ = 'ruddra'



def get_model_description(model_name=None, return_property_list=True):
    for item in models.get_models(include_auto_created=True):
        if item.__name__ == model_name:
            if return_property_list is True:
                return item.get_trigger_properties()
            else:
                return item
    return []

def get_model_by_name(model_name, app_label=None, **kwargs):
    if app_label is not None:
        return apps.get_model(app_label, model_name)
    model_object = ContentType.objects.get(model=model_name.lower())
    return apps.get_model(model_object.app_label, model_name)