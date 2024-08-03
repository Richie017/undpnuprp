__author__ = 'Mahmud'


def enable_assignment(**kwargs):
    registry = {}

    def enable_assignment(original_class):
        if '_registry' in dir(original_class):
            if original_class.__name__ in original_class._registry and 'enable_assignment' in original_class._registry[original_class.__name__]:
                original_class._registry[original_class.__name__]['enable_assignment'].update(**kwargs)
            else:
                if original_class.__name__ not in original_class._registry:
                    original_class._registry[original_class.__name__] = dict()
                original_class._registry[original_class.__name__]['enable_assignment'] = dict(**kwargs)
        else:
            registry[original_class.__name__] = dict()
            registry[original_class.__name__]['enable_assignment'] = dict(**kwargs)
            original_class._registry = registry
        return original_class
    return enable_assignment