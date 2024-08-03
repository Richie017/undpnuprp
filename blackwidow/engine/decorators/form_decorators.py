__author__ = 'Mahmud'


def form_data(**kwargs):
    registry = {}

    def form_data(original_class):
        if '_registry' in dir(original_class):
            if 'route' in original_class._registry[original_class.__name__]:
                original_class._registry[original_class.__name__]['form_data'].update(**kwargs)
            else:
                original_class._registry[original_class.__name__]['form_data'] = dict(**kwargs)
        else:
            registry[original_class.__name__] = dict()
            registry[original_class.__name__]['form_data'] = dict(**kwargs)
            original_class._registry = registry
        return original_class
    return form_data

