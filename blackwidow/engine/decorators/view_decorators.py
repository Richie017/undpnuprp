__author__ = 'Mahmud'


def override_view(model=None, view=None , **kwargs):
    registry = {}

    def override_view(original_class):

        if '_registry' in dir(original_class):
            if original_class.__name__ not in original_class._registry:
                original_class._registry[original_class.__name__] = dict()

            if 'override_view' in original_class._registry[original_class.__name__]:
                original_class._registry[original_class.__name__]['override_view'].update(model=model, view=view, **kwargs)
            else:
                original_class._registry[original_class.__name__]['override_view'] = dict(model=model, view=view, **kwargs)
        else:
            registry[original_class.__name__] = dict()
            registry[original_class.__name__]['override_view'] = dict(model=model, view=view, **kwargs)
            original_class._registry = registry
        return original_class
    return override_view
