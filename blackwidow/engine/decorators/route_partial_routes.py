from blackwidow.engine.enums.view_scope import ViewScope

__author__ = 'Mahmud'


def is_profile_content(original_class):
    return original_class


def route(scope=ViewScope.General, **kwargs):
    registry = {}

    def route(original_class):
        if '_registry' in dir(original_class):
            if original_class.__name__ not in original_class._registry:
                original_class._registry[original_class.__name__] = dict()

            if 'route' in original_class._registry[original_class.__name__]:
                original_class._registry[original_class.__name__]['route'].update(**kwargs)
            else:
                original_class._registry[original_class.__name__]['route'] = dict(**kwargs)
        else:
            registry[original_class.__name__] = dict()
            registry[original_class.__name__]['route'] = dict(**kwargs)
            original_class._registry = registry
        return original_class

    return route


def partial_route(**kwargs):
    registry = {}

    def partial_route(original_class):
        if '_registry' in dir(original_class):
            if original_class.__name__ not in original_class._registry:
                original_class._registry[original_class.__name__] = dict()

            if 'partial_route' in original_class._registry[original_class.__name__]:
                original_class._registry[original_class.__name__]['partial_route'].update(**kwargs)
            else:
                original_class._registry[original_class.__name__]['partial_route'] = dict(**kwargs)
        else:
            registry[original_class.__name__] = dict()
            registry[original_class.__name__]['partial_route'] = dict(**kwargs)
            original_class._registry = registry
        return original_class

    return partial_route


def is_business_role(original_class):
    return original_class
