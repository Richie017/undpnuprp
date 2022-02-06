from django.apps import apps

get_model = apps.get_model

__author__ = 'Tareq'


class AssignmentTrackedModelMixin(object):

    def get_assignment_trackable_fields(self):
        return []  # list of tuple. first item is field/property name, second item is given name

    def save_assignment_log(self):
        trackable_model = self.is_model_trackable(model=self._meta.model)
        if trackable_model:
            for f_key in self.get_assignment_trackable_fields():
                model_group = trackable_model
                model_name = self._meta.model.__name__
                model_app_label = self._meta.model._meta.app_label
                object_key = self.pk
                relation_name = f_key['field']
                display_name = f_key['display_name']

                AssignmentLog = get_model(app_label='core', model_name='AssignmentLog')
                _log = AssignmentLog.objects.filter(model_group=model_group, model_name=model_name,
                                                    model_app_label=model_app_label,
                                                    object_key=object_key, relation_name=relation_name).first()

                new_log = AssignmentLog(model_group=model_group, model_name=model_name, model_app_label=model_app_label,
                                        object_key=object_key, relation_name=relation_name)
                new_log.previous_related_key = _log.current_related_key if _log is not None else 0
                value = getattr(self, f_key['field']) if hasattr(self, f_key['field']) else None
                if isinstance(value, int):
                    new_log.current_related_key = value
                else:
                    new_log.current_related_key = value.pk if hasattr(value, 'pk') else 0
                if new_log.current_related_key != new_log.previous_related_key:
                    new_log.display_name = display_name
                    new_log.save()

    def is_model_trackable(self, model=None):
        if model is None:
            return False
        if 'track_assignments' in [decorator.__name__ for decorator in model._decorators]:
            return model.__name__
        base = model.__base__
        if base.__name__ == 'DomainEntity':
            return False
        return self.is_model_trackable(model=base)
