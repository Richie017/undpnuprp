from django.dispatch import Signal

versioned_data = Signal(providing_args=["instance"])


def enable_caching(reference_model=None, hidden=False):
    """
    Based on David Cramer's track_data.py
    See: http://cramer.io/2010/12/06/tracking-changes-to-fields-in-django

    Here we just add a single line to issue the track_data specific
    signal.
    """

    def enable_caching(original_class):
        original_class.__reference_model = reference_model if reference_model else original_class
        original_class.__hidden_in_cache_list = hidden

        def save(self, *args, **kwargs):
            from blackwidow.core.views.models.json_generator_view import ModelDataToJsonView

            save._original(self, *args, **kwargs)
            ModelDataToJsonView.convert_data_to_json(model=original_class.__reference_model)
        save._original = original_class.save
        original_class.save = save

        def soft_delete(self, *args, **kwargs):
            from blackwidow.core.views.models.json_generator_view import ModelDataToJsonView

            soft_delete._original(self, *args, **kwargs)
            ModelDataToJsonView.convert_data_to_json(model=original_class.__reference_model)
        soft_delete._original = original_class.soft_delete
        original_class.soft_delete = soft_delete

        def restore(self, *args, **kwargs):
            from blackwidow.core.views.models.json_generator_view import ModelDataToJsonView

            restore._original(self, *args, **kwargs)
            ModelDataToJsonView.convert_data_to_json(model=original_class.__reference_model)
        restore._original = original_class.restore
        original_class.restore = restore

        return original_class

    return enable_caching
