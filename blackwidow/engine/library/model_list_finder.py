from django.apps import apps
from django.contrib.contenttypes.models import ContentType

__author__ = 'Sohel'

class ModelListFinder(object):
    @classmethod
    def find_models(cls, app_labels=[], include_class_name=False):
        if not include_class_name:
            model_names = ContentType.objects.all()
            if app_labels:
                model_names = model_names.filter(app_label__in=app_labels)
            model_names = model_names.values('model').order_by('model')
            print(model_names)
            model_names = [(x['model'],x['model'].capitalize()) for x in model_names]
            return model_names
        else:
            app_models = []
            for app in app_labels:
                try:
                    temp_models = apps.get_models(app)
                    for _model in temp_models:
                        if not ( _model.__name__, _model.__name__ ) in app_models:
                            app_models += [ ( _model.__name__, _model.__name__ ) ]
                except:
                    pass
            return app_models

