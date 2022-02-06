__author__ = 'Mahmud'


def enable_search(predefined=[]):
    registry = {}
    kwargs = {
        'predefined': predefined
    }

    def enable_search(original_class):
        if '_registry' in dir(original_class):
            if original_class.__name__ not in original_class._registry:
                original_class._registry[original_class.__name__] = dict()

            if 'enable_search' in original_class._registry[original_class.__name__]:
                original_class._registry[original_class.__name__]['enable_search'].update(**kwargs)
            else:
                original_class._registry[original_class.__name__]['enable_search'] = dict(**kwargs)
        else:
            registry[original_class.__name__] = dict()
            registry[original_class.__name__]['enable_search'] = dict(**kwargs)
            original_class._registry = registry
        return original_class
    return enable_search